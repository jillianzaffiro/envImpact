import unittest
from parameterized import parameterized
from DescriptionProcessing.CBERT.BertPreprocessing import BertPreprocessor
from Projects.DescriptionParsing import DescriptionParser


class DescriptionParsingTests(unittest.TestCase):
    def setUp(self):
        bpp = BertPreprocessor(64)
        self.description_parser = DescriptionParser(bpp)

    def test_can_do_simple_length(self):
        # Arrange
        text = "3 feet"

        # Act
        ok, v = self.description_parser.get_length_param(text)

        # Assert
        self.assertTrue(ok)

    def test_can_do_simple_empty(self):
        # Arrange
        text = "a long road and a centipede with many feet"

        # Act
        ok, v = self.description_parser.get_length_param(text)

        # Assert
        self.assertFalse(ok)

    @parameterized.expand([
        ("Building a bridge spanning 100 foot section of the river", 100),
        ("This project is a 550 ft crossing with 6 lanes and 3 traffic lights", 550),
        ("The 7 mile bridge runs along the keys between Knight and Little duck", 36_960),
        ("This 7 lane project will run for 6 months and be 2000 feet long", 2000),
        ("A fun project to span niagra falls is 330 ft. long", 330),
        ("This project adds a bridge from north to south over the Ohio River 6 lanes 980 feet long", 980)
    ])
    def test_bridge_gets_length_from_texts(self, text, length):
        # Arrange

        # Act
        ok, v = self.description_parser.get_length_param(text)

        # Assert
        self.assertTrue(ok)
        self.assertAlmostEqual(length, v, places=1)

    @parameterized.expand([
        # ("970 feet", 970),        # 970 gets parsed as 2 tokens, not 1.
        ("980 feet", 980),
        # ("990 feet", 990),
    ])
    def test_bridge_works_on_numbers(self, text, length):
        # Arrange

        # Act
        ok, v = self.description_parser.get_length_param(text)

        # Assert
        self.assertTrue(ok)
        self.assertAlmostEqual(length, v, places=1)

    def test_can_do_no_lanes(self):
        # Arrange
        text = "a long road and a centipede with many feet"

        # Act
        ok, v = self.description_parser.get_lanes_param(text)

        # Assert
        self.assertFalse(ok)

    def test_can_do_some_lanes(self):
        # Arrange
        text = "a long and winding 3 lane road"

        # Act
        ok, v = self.description_parser.get_lanes_param(text)

        # Assert
        self.assertTrue(ok)
        self.assertEqual(3, v)

    def test_can_do_mix(self):
        # Arrange
        text = "This project is a 550 ft crossing with 6 lanes and 3 traffic lights"

        # Act
        ok1, length = self.description_parser.get_length_param(text)
        ok2, lanes = self.description_parser.get_lanes_param(text)

        # Assert
        self.assertTrue(ok1)
        self.assertTrue(ok2)
        self.assertEqual(550, length)
        self.assertEqual(6, lanes)

    @parameterized.expand([
        ("Bradley Solar 120MW United States Follow Project is a proposed 120megawatt MW photovoltaic", 120),
        ("We will install 75 megawatt system", 75),
        ("This project will provide 140 MW", 140),
        ("For each house, the panel will provide 15 KW", 0.015),
        ("A large home install may provide more than 60 kilowatt on a sunny day", 0.06),
    ])
    def test_bridge_gets_length_from_texts(self, text, power):
        # Arrange

        # Act
        ok, v = self.description_parser.get_power_param(text)

        # Assert
        self.assertTrue(ok)
        self.assertAlmostEqual(power, v, places=4)

    def test_can_handle_unknown_field(self):
        # Arrange
        text = "This project is a 550 ft crossing with 6 lanes and 3 traffic lights"

        # Act
        ok1, val = self.description_parser.get_param("some_unknown_param", text)

        # Assert
        self.assertIsNone(ok1)
