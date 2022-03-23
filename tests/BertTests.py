import unittest
from parameterized import parameterized
import numpy as np

from DescriptionProcessing.CBERT.BertPreprocessing import BertPreprocessor


class BertTests(unittest.TestCase):
    def setUp(self):
        self.bpp = BertPreprocessor(64)

    def test_can_instantiate_bert(self):
        # Arrange

        # Act
        bpp = BertPreprocessor(64)

        # Assert
        self.assertIsNotNone(bpp)

    def test_can_get_tokens(self):
        # Arrange
        sentence = "Welcome to the bert tokenizer."

        # Act
        tokens, _ = self.bpp.tokenize_one_sentence(sentence)

        # Assert
        self.assertEqual(7, len(tokens))
        self.assertEqual(['welcome', 'to', 'the', 'bert', 'token', '##izer', '.'], tokens)

    def test_adds_start_token_to_ids(self):
        # Arrange
        sentence = "Welcome to the bert tokenizer."

        # Act
        _, ids = self.bpp.tokenize_one_sentence(sentence)

        # Assert
        self.assertEqual(101, ids[0])

    def test_adds_end_token_to_ids(self):
        # Arrange
        sentence = "Welcome to the bert tokenizer."

        # Act
        _, ids = self.bpp.tokenize_one_sentence(sentence)

        # Assert
        self.assertEqual(102, ids[-1])

    def test_can_get_tokens_ids(self):
        # Arrange
        sentence = "Welcome to the bert tokenizer."

        # Act
        _, ids = self.bpp.tokenize_one_sentence(sentence)

        # Assert
        self.assertEqual(9, len(ids))
        self.assertEqual([101, 6160, 2000, 1996, 14324, 19204, 17629, 1012, 102], ids)

    def test_can_process_sentences_into_tokens(self):
        # Arrange
        sentences = ["Welcome to the bert tokenizer.", "I hope you have fun."]

        # Act
        ids, _ = self.bpp.preprocess_data(sentences)

        # Assert
        self.assertEqual(2, len(ids))
        s1_ids = ids[0]
        s2_ids = ids[1]
        self.assertEqual(64, len(s1_ids))
        self._arrays_equal([101, 6160, 2000, 1996, 14324, 19204, 17629, 1012, 102], s1_ids[:9].numpy())
        self._arrays_equal([101, 1045, 3246, 2017, 2031, 4569, 1012, 102], s2_ids[:8].numpy())

    def test_can_process_sentences_into_masks(self):
        # Arrange
        sentences = ["Welcome to the bert tokenizer.", "I hope you have fun."]

        # Act
        _, masks = self.bpp.preprocess_data(sentences)

        # Assert
        self.assertEqual(2, len(masks))
        s1_mask = masks[0]
        s2_mask = masks[1]
        self.assertEqual(64, len(s1_mask))
        num_tokens = 7 + 2
        self._arrays_equal(np.ones(num_tokens), s1_mask[:num_tokens].numpy())
        self._arrays_equal(np.zeros(64 - num_tokens), s1_mask[num_tokens:].numpy())
        self.assertEqual(64, len(s2_mask))
        num_tokens = 6 + 2
        self._arrays_equal(np.ones(num_tokens), s2_mask[:num_tokens].numpy())
        self._arrays_equal(np.zeros(64 - num_tokens), s2_mask[num_tokens:].numpy())

    @parameterized.expand([
        ("970 feet", "970", 'feet'),
        ("980 miles", "980", 'miles'),
        ("990 days", "990", 'days'),
        ("5m", "5", 'm'),
        ("150,000,000watt", "150000000", 'watt')
    ])
    def test_can_tokenize_numbers(self, text, first_token, second_token):
        # Arrange

        # Act
        tokens = self.bpp.tokenize_sentence_with_numbers(text)

        # Assert
        print(tokens)
        self.assertEqual(2, len(tokens))
        self.assertEqual([first_token, second_token], tokens)

    def _arrays_equal(self, a1, a2):
        self.assertEqual(len(a1), len(a2))
        for idx in range(len(a1)):
            self.assertEqual(a1[idx], a2[idx])
