import unittest
from parameterized import parameterized

from DescriptionProcessing.CBERT.BertPreprocessing import BertPreprocessor
from Projects.GenericProject import GenericProject
from Projects.DescriptionParsing import DescriptionParser
from Projects.Bridge import Bridge
from Projects.Rules import LENGTH, LANES
from Projects.Rules import WIDTH, SURFACE_AREA, TONS_CONCRETE
from tests.Mocks import MockLogger


class ProjectsTests(unittest.TestCase):
    def setUp(self) -> None:
        bpp = BertPreprocessor(16)
        self.lgr = MockLogger()
        self.description_parser = DescriptionParser(bpp)

    def test_can_instantiate_generic(self):
        # Arrange

        # Act
        p = GenericProject(self.lgr)

        # Assert
        self.assertIsNotNone(p)

    def test_can_instantiate_bridge(self):
        # Arrange

        # Act
        p = Bridge(self.lgr)

        # Assert
        self.assertIsNotNone(p)

    def test_bridge_has_defaults(self):
        # Arrange
        p = Bridge(self.lgr)

        # Act

        # Assert
        self.assertAlmostEqual(p.get_param_value(LENGTH), 1000.0, places=1)
        self.assertAlmostEqual(p.get_param_value(LANES), 4)
        self.assertAlmostEqual(p.get_param_value(WIDTH), 96.0, places=1)
        self.assertAlmostEqual(p.get_param_value(SURFACE_AREA), 96_000.0, places=1)
        self.assertAlmostEqual(p.get_param_value(TONS_CONCRETE), 10800.0, places=1)

    def test_bridge_calculates_surface(self):
        # Arrange
        params = {'name': "test bridge", 'length': 100, 'lanes': 2}
        _, p = Bridge.from_json(self.lgr, params)

        # Act
        surface = p.get_param_value(SURFACE_AREA)

        # Assert
        # 100 ft * 2 lanes * 24 ft / lane = 4800 ft^2
        self.assertAlmostEqual(4800.0, surface, places=1)

    def test_bridge_calculates_concrete(self):
        # Arrange
        params = {"name": "GenericBridge", "length": 100, "lanes": 2}
        _, p = Bridge.from_json(self.lgr, params)

        # Act
        concrete = p.get_param_value(TONS_CONCRETE)

        # Assert
        # 100 ft * 2 lanes * 24 ft / lane = 4800 ft^2
        # 4800 * 1.5 ft thick * 150 lb/ft^3 = 1_080_000 lb / 2000 = 540 tons
        self.assertAlmostEqual(540.0, concrete, places=1)

    def test_bridge_gets_length_from_text(self):
        # Arrange
        params = {"name": "GenericBridge", "length": 100, "lanes": 2}
        _, p = Bridge.from_json(self.lgr, params)
        p.set_description_parser(self.description_parser)

        text = "Building a bridge 2500 ft long."
        expected_length = 2500.0
        expected_width = 48.0
        expected_area = expected_width * expected_length

        # Act
        ok, err = p.params_from_description(text)

        # Assert
        self.assertTrue(ok)
        self.assertAlmostEqual(expected_length, p.get_param_value(LENGTH), places=1)
        self.assertAlmostEqual(p.get_param_value(LANES), 2)
        self.assertAlmostEqual(p.get_param_value(WIDTH), expected_width, places=1)
        self.assertAlmostEqual(p.get_param_value(SURFACE_AREA), expected_area, places=1)
        self.assertAlmostEqual(p.get_param_value(TONS_CONCRETE), 13_500.0, places=1)

    @parameterized.expand([
        ("short", "Building a bridge spanning 100 foot section of the river", 100, 2),
        ("mid", "This project is a 550 ft crossing with 6 lanes and 3 traffic lights", 550, 6),
        ("large", "The 7 mile bridge runs along the keys between Knight and Little duck", 36_960, 2),
        ("mixed", "This 7 lane project will run for 6 months and be 2000 feet long", 2000, 7),
        ("noLength", "A fun project to span Niagra falls with a 9 lane barrel", 100, 9)
    ])
    def test_bridge_gets_length_from_texts(self, name, text, length, lanes):
        # Arrange
        params = {"name": "GenericBridge", "length": 100, "lanes": 2}
        _, p = Bridge.from_json(self.lgr, params)
        p.set_description_parser(self.description_parser)

        # Act
        ok, err = p.params_from_description(text)

        # Assert
        width = lanes * 24                  # Lanes calculated field is correctly updated
        surface_area = p.get_param_value(LENGTH) * width     # Length calculated field is correctly updated
        self.assertTrue(ok)
        self.assertAlmostEqual(length, p.get_param_value(LENGTH), places=1)
        self.assertAlmostEqual(lanes, p.get_param_value(LANES), places=1)
        self.assertAlmostEqual(width, p.get_param_value(WIDTH), places=1)
        self.assertAlmostEqual(surface_area, p.get_param_value(SURFACE_AREA), places=1)

    def test_values_not_overwritten_when_not_specified(self):
        # Arrange
        params = {"name": "GenericBridge", "length": 100, "lanes": 2, "width": 17}
        _, p = Bridge.from_json(self.lgr, params)
        p.set_description_parser(self.description_parser)
        text = "This project is a 490 ft crossing with 3 traffic lights"

        # Act
        ok, err = p.params_from_description(text)

        # Assert
        surface_area = 490 * 17     # Uses new length and old width
        self.assertTrue(ok)
        self.assertAlmostEqual(490, p.get_param_value(LENGTH), places=1)
        self.assertAlmostEqual(2, p.get_param_value(LANES), places=1)
        self.assertAlmostEqual(17, p.get_param_value(WIDTH), places=1)
        self.assertAlmostEqual(surface_area, p.get_param_value(SURFACE_AREA), places=1)


class ProjectsJsonTests(unittest.TestCase):
    def setUp(self) -> None:
        bpp = BertPreprocessor(16)
        self.lgr = MockLogger()
        self.description_parser = DescriptionParser(bpp)

    def test_to_json(self):
        # Arrange
        p = Bridge(self.lgr)

        # Act
        json_dict = p.to_json()

        # Assert
        self.assertTrue("length" in json_dict)

    def test_type_in_json(self):
        # Arrange
        p = Bridge(self.lgr)

        # Act
        json_dict = p.to_json()

        # Assert
        self.assertTrue("project_type" in json_dict)
        self.assertEqual("bridges", json_dict["project_type"])
