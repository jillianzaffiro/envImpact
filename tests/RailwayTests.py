import unittest
from parameterized import parameterized

from DescriptionProcessing.CBERT.BertPreprocessing import BertPreprocessor
from Projects.Railway import Railway
from Projects.DescriptionParsing import DescriptionParser
from Projects.Rules import LENGTH
from Projects.Rules import TONS_STEEL
from Projects.Rules import TONS_CONCRETE
from Projects.Rules import TONS_BALLAST
from tests.Mocks import MockLogger


class RailwayTests(unittest.TestCase):
    def setUp(self) -> None:
        bpp = BertPreprocessor(16)
        self.lgr = MockLogger()
        self.description_parser = DescriptionParser(bpp)

    def test_can_instantiate_railway(self):
        # Arrange

        # Act
        p = Railway(self.lgr)

        # Assert
        self.assertIsNotNone(p)

    def test_railway_has_defaults(self):
        # Arrange
        p = Railway(self.lgr)

        # Act

        # Assert
        self.assertAlmostEqual(p.get_param_value(LENGTH), 1000.0, places=1)
        self.assertAlmostEqual(p.get_param_value(TONS_STEEL), 33.6, places=1)
        self.assertAlmostEqual(p.get_param_value(TONS_CONCRETE), 150.0, places=1)
        self.assertAlmostEqual(p.get_param_value(TONS_BALLAST), 13.8, places=1)

    def test_railway_calculates_concrete(self):
        # Arrange
        params = {"name": "Train Project", "length": 5200}
        _, p = Railway.from_json(self.lgr, params)

        # Act
        concrete = p.get_param_value(TONS_CONCRETE)

        # Assert
        self.assertAlmostEqual(780.0, concrete, places=1)

    def test_railway_gets_length_from_text(self):
        # Arrange
        params = {"name": "Train", "length": 2500}
        _, p = Railway.from_json(self.lgr, params)
        p.set_description_parser(self.description_parser)

        text = "Building a railway 5 miles long."
        expected_length = 26400.0

        # Act
        ok, err = p.params_from_description(text)

        # Assert
        self.assertTrue(ok)
        self.assertAlmostEqual(expected_length, p.get_param_value(LENGTH), places=1)
        self.assertAlmostEqual(p.get_param_value(TONS_CONCRETE), 3960.0, places=1)

    @parameterized.expand([
        ("short", "Building a train rail running 18000 foot.", 18000),
        ("mid", "This project is a 70 mile light rail from Cincinatti to Columbus", 369_600),
        ("long", "Interstate transportation with 1500 miles of new train tracks", 7_920_000)
    ])
    def test_bridge_gets_length_from_texts(self, name, text, length):
        # Arrange
        params = {"name": "Train", "length": 100}
        _, p = Railway.from_json(self.lgr, params)
        p.set_description_parser(self.description_parser)

        # Act
        ok, err = p.params_from_description(text)

        # Assert
        self.assertTrue(ok)
        self.assertAlmostEqual(length, p.get_param_value(LENGTH), places=1)


class RailwayJsonTests(unittest.TestCase):
    def setUp(self) -> None:
        bpp = BertPreprocessor(16)
        self.lgr = MockLogger()
        self.description_parser = DescriptionParser(bpp)

    def test_to_json(self):
        # Arrange
        p = Railway(self.lgr)

        # Act
        json_dict = p.to_json()

        # Assert
        self.assertTrue("length" in json_dict)

    def test_type_in_json(self):
        # Arrange
        p = Railway(self.lgr)

        # Act
        json_dict = p.to_json()

        # Assert
        self.assertTrue("project_type" in json_dict)
        self.assertEqual("railways", json_dict["project_type"])
