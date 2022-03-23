import os
import time
import datetime
import pickle
import random

from Common.Logger import Logger
from Common.gpu import check_for_GPU
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import torch
from torch.utils.data import TensorDataset, random_split
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler
from transformers import BertForSequenceClassification, AdamW
from transformers import get_linear_schedule_with_warmup


class CBert:
    def __init__(self, logger: Logger, num_labels, models_dir, model_vers):
        # https://www.tensorflow.org/official_models/fine_tuning_bert
        self._lgr = logger
        self._lgr.info(f"Init CBERT with model vers: {model_vers}")
        self._device, self._strategy = check_for_GPU()

        # For fine-tuning BERT on a specific task, the authors recommend a batch
        # size of 16 or 32 and 4 epochs.
        self.batch_size = 32
        self.num_epochs = 4
        self.num_labels = num_labels  # The number of output labels--2 for binary classification.

        self._models_dir = models_dir
        self._model_version = model_vers
        if model_vers is None:
            self._model = self._load_base_model()
            self._model_version = 'pretrained'
        else:
            self._model = self._restore_model(model_vers)

        self._train_dataloader = None
        self._validation_dataloader = None

        self._lgr.info("Done with CBERT init")

    def split_datasets(self, input_ids, attention_masks, labels):
        labels = torch.tensor(labels)
        dataset = TensorDataset(input_ids, attention_masks, labels)
        train_size = int(0.9 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

        self._lgr.info('{:>5,} training samples'.format(train_size))
        self._lgr.info('{:>5,} validation samples'.format(val_size))

        # Create the DataLoaders for our training and validation sets.
        # We'll take training samples in random order.
        self._train_dataloader = DataLoader(
            train_dataset,  # The training samples.
            sampler=RandomSampler(train_dataset),  # Select batches randomly
            batch_size=self.batch_size  # Trains with this batch size.
        )

        # For validation the order doesn't matter, so we'll just read them sequentially.
        self._validation_dataloader = DataLoader(
            val_dataset,  # The validation samples.
            sampler=SequentialSampler(val_dataset),  # Pull out batches sequentially.
            batch_size=self.batch_size  # Evaluate with this batch size.
        )

    def save_model(self, version):
        assert self._model is not None, "Model not set, call 'load_module'"
        if version is None:
            version = self._model_version

        model_dir = f"{self._models_dir}/bert_{version}"
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        torch.save(self._model.state_dict(), model_dir + "/model.pk")
        configuration = self._model.config
        with open(model_dir + "/config.pkl", 'wb') as handle:
            pickle.dump(configuration, handle, protocol=pickle.HIGHEST_PROTOCOL)

        self._model_version = version

    def _restore_model(self, version):
        self._lgr.info(f"Restoring model to version {version}")
        model_dir = f"{self._models_dir}/bert_{version}"
        with open(model_dir + "/config.pkl", 'rb') as handle:
            # configuration = BertConfig()
            configuration = pickle.load(handle)
        model = BertForSequenceClassification(configuration)
        model.load_state_dict(torch.load(model_dir + "/model.pk"))
        model.eval()
        return model

    def _load_base_model(self):
        self._lgr.info(f"Restoring model to base pretrained")
        verbose = False
        # Load BertForSequenceClassification, the pretrained BERT model with a single
        # linear classification layer on top.
        model = BertForSequenceClassification.from_pretrained(
            "bert-base-uncased",  # Use the 12-layer BERT model, with an uncased vocab.
            num_labels=self.num_labels,
            output_attentions=False,  # Whether the model returns attentions weights.
            output_hidden_states=False,  # Whether the model returns all hidden-states.
        )

        # Tell pytorch to run this model on the GPU.
        # model.cuda()
        if verbose:
            # Get all of the model's parameters as a list of tuples.
            params = list(model.named_parameters())
            print('The BERT model has {:} different named parameters.\n'.format(len(params)))
            print('==== Embedding Layer ====\n')
            for p in params[0:5]:
                print("{:<55} {:>12}".format(p[0], str(tuple(p[1].size()))))

            print('\n==== First Transformer ====\n')
            for p in params[5:21]:
                print("{:<55} {:>12}".format(p[0], str(tuple(p[1].size()))))

            print('\n==== Output Layer ====\n')
            for p in params[-4:]:
                print("{:<55} {:>12}".format(p[0], str(tuple(p[1].size()))))

        return model

    def predict(self, input_ids, input_mask):
        with torch.no_grad():
            # Forward pass, calculate logit predictions.
            results = self._model(input_ids, attention_mask=input_mask)

        logits = results.logits
        logits = logits.detach().cpu().numpy()
        return logits

    def train(self):
        assert self._model is not None, "Model not set, call 'load_module'"
        assert self._train_dataloader is not None, "Train dataloader not set, call 'split_datasets'"
        assert self._validation_dataloader is not None, "Validation dataloader not set, call 'split_datasets'"

        optimizer = AdamW(self._model.parameters(),
                          lr=2e-5,  # args.learning_rate
                          eps=1e-8  # args.adam_epsilon
                          )

        # Total number of training steps is [number of batches] x [number of epochs].
        total_steps = len(self._train_dataloader) * self.num_epochs
        scheduler = get_linear_schedule_with_warmup(optimizer,
                                                    num_warmup_steps=0,  # Default value in run_glue.py
                                                    num_training_steps=total_steps)

        return self._training_loop(optimizer, scheduler)

    def _training_loop(self, optimizer, scheduler):
        self._lgr.info(f"Start training: num labels = {self.num_labels}")
        # This training code is based on the `run_glue.py` script here:
        # https://github.com/huggingface/transformers/blob/5bfcd0485ece086ebcbed2d008813037968a9e58/examples/run_glue.py#L128
        seed_val = 42
        random.seed(seed_val)
        np.random.seed(seed_val)
        torch.manual_seed(seed_val)
        torch.cuda.manual_seed_all(seed_val)

        training_stats = []

        # For each epoch...
        for epoch_i in range(0, self.num_epochs):
            # ========================================
            #               Training
            # ========================================
            # Perform one full pass over the training set.
            print('======== Epoch {:} / {:} ========'.format(epoch_i + 1, self.num_epochs))

            # Put the model into training mode. Don't be mislead--the call to
            # `train` just changes the *mode*, it doesn't *perform* the training.
            # `dropout` and `batchnorm` layers behave differently during training
            # vs. test (source: https://stackoverflow.com/questions/51433378/what-does-model-train-do-in-pytorch)
            self._model.train()
            avg_train_loss, training_time = self._run_one_epoch(optimizer, scheduler)

            # ========================================
            #               Validation
            # ========================================
            # After the completion of each training epoch, measure our performance on
            # our validation set.
            print("Running Validation...")

            # Put the model in evaluation mode--the dropout layers behave differently
            # during evaluation.
            self._model.eval()
            avg_val_loss, avg_val_accuracy, validation_time = self._validate()

            # Record all statistics from this epoch.
            # Calculate the average loss over all of the batches.
            training_stats.append(
                {
                    'epoch': epoch_i + 1,
                    'Training Loss': avg_train_loss,
                    'Training Time': training_time,
                    'Valid. Loss': avg_val_loss,
                    'Valid. Accur.': avg_val_accuracy,
                    'Validation Time': validation_time
                }
            )

        print("Training complete!")
        return training_stats

    def _run_one_epoch(self, optimizer, scheduler):
        total_train_loss = 0.0
        num_steps = 0
        t0 = time.time()

        for step, batch in enumerate(self._train_dataloader):
            if step % 10 == 0 and not step == 0:
                # Calculate elapsed time in minutes.
                elapsed = self._format_time(time.time() - t0)
                print('  Batch {:>5,}  of  {:>5,}.    Elapsed: {:}.'
                      .format(step, len(self._train_dataloader), elapsed))

            # `batch` contains three pytorch tensors:
            #   [0]: input ids
            #   [1]: attention masks
            #   [2]: labels
            b_input_ids = batch[0].to(self._device)
            b_input_mask = batch[1].to(self._device)
            b_labels = batch[2].to(self._device)

            # Always clear any previously calculated gradients before performing a
            # backward pass. PyTorch doesn't do this automatically because
            # accumulating the gradients is "convenient while training RNNs".
            # (source: https://stackoverflow.com/questions/48001598/why-do-we-need-to-call-zero-grad-in-pytorch)
            self._model.zero_grad()

            # Perform a forward pass (evaluate the model on this training batch).
            # The documentation for this `model` function is here:
            # https://huggingface.co/transformers/v4.7.0/model_doc/bert.html#transformers.BertForSequenceClassification
            # It returns different numbers of parameters depending on what arguments
            # are given and what flags are set.
            # token_type_ids is the same as the "segment ids", which
            # differentiates sentence 1 and 2 in 2-sentence tasks.
            # For our usage here, it returns
            # the loss (because we provided labels) and
            # the "logits", i.e. the model outputs prior to activation.
            results = self._model(b_input_ids,
                                  token_type_ids=None,
                                  attention_mask=b_input_mask,
                                  labels=b_labels)

            loss = results.loss
            total_train_loss += loss.item()
            num_steps += 1
            print(f"Loss:{loss.item()}, step:{step}")

            # Perform a backward pass to calculate the gradients.
            loss.backward()

            # Clip the norm of the gradients to 1.0.
            # This is to help prevent the "exploding gradients" problem.
            torch.nn.utils.clip_grad_norm_(self._model.parameters(), 1.0)

            # Update parameters and take a step using the computed gradient.
            # The optimizer dictates the "update rule"--how the parameters are
            # modified based on their gradients, the learning rate, etc.
            optimizer.step()

            # Update the learning rate.
            scheduler.step()

        training_time = self._format_time(time.time() - t0)
        avg_train_loss = total_train_loss / num_steps
        print("  Average training loss: {0:.2f}".format(avg_train_loss))
        print("  Training epoch took: {:}".format(training_time))
        return avg_train_loss, training_time

    def _validate(self):
        # Tracking variables
        t0 = time.time()
        total_eval_accuracy = 0
        total_eval_loss = 0

        # Evaluate data for one epoch
        for batch in self._validation_dataloader:
            b_labels, results = self._predict_one_batch(batch)

            # Accumulate the validation loss.
            loss = results.loss
            logits = results.logits
            total_eval_loss += loss.item()

            # Move logits and labels to CPU
            logits = logits.detach().cpu().numpy()
            label_ids = b_labels.to('cpu').numpy()

            # Calculate the accuracy for this batch of test sentences, and
            # accumulate it over all batches.
            num_correct, num_predicted = self._flat_accuracy(logits, label_ids)
            total_eval_accuracy += num_correct / num_predicted

        # Report the final accuracy for this validation run.
        num_validation_points = len(self._validation_dataloader)
        avg_val_accuracy = total_eval_accuracy / num_validation_points
        print("  Accuracy: {0:.2f}".format(avg_val_accuracy))

        # Calculate the average loss over all of the batches.
        avg_val_loss = total_eval_loss / num_validation_points

        # Measure how long the validation run took.
        validation_time = self._format_time(time.time() - t0)
        print("  Validation Loss: {0:.2f}".format(avg_val_loss))
        print("  Validation took: {:}".format(validation_time))

        return avg_val_loss, avg_val_accuracy, validation_time

    def _predict_one_batch(self, batch):
        # `batch` contains three pytorch tensors:
        #   [0]: input ids
        #   [1]: attention masks
        #   [2]: labels
        b_input_ids = batch[0].to(self._device)
        b_input_mask = batch[1].to(self._device)
        b_labels = batch[2].to(self._device)
        # Tell pytorch not to bother with constructing the compute graph during
        # the forward pass, since this is only needed for backprop (training).
        with torch.no_grad():
            # Forward pass, calculate logit predictions.
            results = self._model(b_input_ids,
                                  token_type_ids=None,
                                  attention_mask=b_input_mask,
                                  labels=b_labels)
        return b_labels, results

    def total_accuracy(self):
        total_correct = 0
        total_predicted = 0
        num_steps = len(self._train_dataloader)
        for step, batch in enumerate(self._train_dataloader):
            b_labels, results = self._predict_one_batch(batch)
            logits = results.logits

            # Move logits and labels to CPU
            logits = logits.detach().cpu().numpy()
            label_ids = b_labels.to('cpu').numpy()

            num_correct, num = self._flat_accuracy(logits, label_ids)
            total_correct += num_correct
            total_predicted += num

            curr_accuracy = num_correct / num
            total_accuracy = total_correct / total_predicted
            print(f'Batch {step:>5,}/{num_steps:>5,}. '
                  f'Accuracy: {curr_accuracy * 100.0:.2f},  '
                  f'Running average Accuracy: {total_accuracy * 100:.2f}')

    # Function to calculate the accuracy of our predictions vs labels
    @staticmethod
    def _flat_accuracy(preds, labels):
        pred_flat = np.argmax(preds, axis=1).flatten()
        labels_flat = labels.flatten()
        num_correct = np.sum(pred_flat == labels_flat)
        return num_correct, len(labels_flat)

    @staticmethod
    def _format_time(elapsed):
        elapsed_rounded = int(round(elapsed))
        return str(datetime.timedelta(seconds=elapsed_rounded))

    @staticmethod
    def show_training_stats(training_stats):
        pd.set_option('precision', 2)
        df_stats = pd.DataFrame(data=training_stats)
        df_stats = df_stats.set_index('epoch')
        print(df_stats)

        # Use plot styling from seaborn.
        sns.set(style='darkgrid')

        # Increase the plot size and font size.
        sns.set(font_scale=1.5)
        plt.rcParams["figure.figsize"] = (12, 6)

        # Plot the learning curve.
        plt.plot(df_stats['Training Loss'], 'b-o', label="Training")
        plt.plot(df_stats['Valid. Loss'], 'g-o', label="Validation")

        # Label the plot.
        plt.title("Training & Validation Loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.legend()
        plt.xticks([1, 2, 3, 4])

        plt.show()
