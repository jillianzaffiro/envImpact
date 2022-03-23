import torch
import re
from transformers import BertTokenizer


class BertPreprocessor:
    def __init__(self, max_len):
        self._max_len = max_len
        self._tokenizer = BertTokenizer.from_pretrained(
            'bert-base-uncased',
            do_lower_case=True)

    def tokenize_sentence_with_numbers(self, sentence):
        # BERT tries to match to a vocabulary but doesn't get numbers right.
        #  First, make sure we have a separation between numbers and words
        # return only tokens, not IDs since we don't have IDs for all numbers
        sentence = self._add_space_for_numbers(sentence)
        t, i = self.tokenize_one_sentence(sentence)
        t = self._reconstitute_numbers(t)
        return t

    def tokenize_one_sentence(self, sentence):
        tokens = self._tokenizer.tokenize(sentence)
        input_ids = self._tokenizer.encode(sentence, add_special_tokens=True)
        return tokens, input_ids

    def preprocess_data(self, sentences):
        input_ids = []
        attention_masks = []

        for sentence in sentences:
            # `encode_plus` will:
            #   (1) Tokenize the sentence.
            #   (2) Prepend the `[CLS]` token to the start.
            #   (3) Append the `[SEP]` token to the end.
            #   (4) Map tokens to their IDs.
            #   (5) Pad or truncate the sentence to `max_length`
            #   (6) Create attention masks for [PAD] tokens.
            encoded_dict = self._tokenizer.encode_plus(
                sentence,                   # Sentence to encode.
                add_special_tokens=True,    # Add '[CLS]' and '[SEP]'
                max_length=self._max_len,   # Pad & truncate all sentences.
                padding='max_length',
                return_attention_mask=True,  # Construct attn. masks.
                return_tensors='pt',        # Return pytorch tensors.
                truncation=True             # Let the tokenizer truncate sentences
            )
            input_ids.append(encoded_dict['input_ids'])
            attention_masks.append(encoded_dict['attention_mask'])

        # Convert the lists into tensors.
        input_ids = torch.cat(input_ids, dim=0)
        attention_masks = torch.cat(attention_masks, dim=0)
        return input_ids, attention_masks

    def show_tokenizer_info(self):
        sentence = "Welcome to the bert tokenizer.  I hope you enjoy it."
        print(' Original: ', sentence)
        print('Tokenized: ', self._tokenizer.tokenize(sentence))
        tokens = self._tokenizer.tokenize(sentence)
        print('Token IDs: ', self._tokenizer.convert_tokens_to_ids(tokens))

    def _add_space_for_numbers(self, sentence):
        # Add space after a string of digits. digits may have commas or decimal points
        sentence = re.sub(r"([0-9,]+(\.[0-9]+)?)", r" \1 ", sentence).strip()

        # Remove commas within a string of digits
        sentence = sentence.replace(",", "")
        return sentence

    def _reconstitute_numbers(self, tokens):
        # tokenizer may break up numbers in a few ways
        #   '97', '##0'   should be '970'
        new_tokens = []
        prev_token = None
        for cur_token in tokens:
            if '##' in cur_token and prev_token is not None:
                if prev_token.isdecimal():
                    new_tokens.pop()
                    cur_token = self._concat_tokens(prev_token, cur_token)
            new_tokens.append(cur_token)
            prev_token = cur_token
        return new_tokens

    def _concat_tokens(self, t1, t2) -> str:
        res1 = [i for i in t1 if i.isdigit()]
        res2 = [i for i in t2 if i.isdigit()]
        return "".join(res1 + res2)
