from Common.Logger import Logger

from DescriptionProcessing.ProjectDataset import ProjectDataset
from DescriptionProcessing.CBERT.BertPreprocessing import BertPreprocessor
from DescriptionProcessing.CBERT.CBertModel import CBert
from Projects.ProjectTypes import ProjectType


def show_bert(logger: Logger, bpp: BertPreprocessor, ajp_data: ProjectDataset):
    bpp.show_tokenizer_info()
    ajp_data.show_data_metrics(bpp)
    ajp_data.save_csv_training()


def train_bert(logger: Logger, bpp: BertPreprocessor, ajp_data: ProjectDataset, vers):
    sentences, labels = ajp_data.get_training_data()
    num_labels = ProjectType.num_sectors()
    input_ids, attention_masks = bpp.preprocess_data(sentences)

    # Model should be None on initial training, it will use the Base.
    cbert = CBert(logger, num_labels, "./models", None)
    cbert.split_datasets(input_ids, attention_masks, labels)

    stats = cbert.train()
    cbert.show_training_stats(stats)
    cbert.save_model(vers)


def show_bert_accuracy(logger: Logger, bpp: BertPreprocessor, ajp_data: ProjectDataset, vers):
    sentences, labels = ajp_data.get_training_data()
    num_labels = ProjectType.num_sectors()

    input_ids, attention_masks = bpp.preprocess_data(sentences)

    cbert = CBert(logger, num_labels, "./models", vers)
    cbert.split_datasets(input_ids, attention_masks, labels)

    cbert.total_accuracy()


def run_bert(logger: Logger, bpp: BertPreprocessor, vers):
    num_labels = ProjectType.num_sectors()

    cbert = CBert(logger, num_labels, "./models", vers)

    test_sentence = ["The concept of an access controlled, high-capacity transportation facility "
                     "connecting Phoenix and Las Vegas", ]
    input_ids, attention_masks = bpp.preprocess_data(test_sentence)

    results = cbert.predict(input_ids, attention_masks)

    sector = ProjectType.translate_prediction(results)
    print(sector)


def run():
    VERS = "CV0.1"
    logger = Logger("BERT")
    bpp = BertPreprocessor(max_len=64)
    ajp_data = ProjectDataset(logger)

    show_bert(logger, bpp, ajp_data)
    train_bert(logger, bpp, ajp_data, VERS)
    show_bert_accuracy(logger, bpp, ajp_data, VERS)
    run_bert(logger, bpp, VERS)


if __name__ == "__main__":
    run()
