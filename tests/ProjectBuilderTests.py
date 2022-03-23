import unittest
from parameterized import parameterized
from Projects.Energy import Energy
from Projects.Bridge import Bridge
from Projects.Road import Road
from Projects.Railway import Railway
from Projects.GenericProject import GenericProject
from Projects.ProjectBuilder import ProjectBuilder
from tests.Mocks import MockLogger, MockDescriptionParser


class ProjectBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lgr = MockLogger()
        self.desc_parser = MockDescriptionParser()
        self.pb = ProjectBuilder(self.lgr, self.desc_parser)

    def test_can_instantiate(self):
        # Arrange

        # Act
        pb = ProjectBuilder(self.lgr, self.desc_parser)

        # Assert
        self.assertIsNotNone(pb)

    @parameterized.expand([
        ("Energy", Energy),
        ("Roads", Road),
        ("Bridges", Bridge),
        ("Railways",  Railway),
        ("Other", GenericProject),
    ])
    def test_can_get_from_type(self, proj_type, expected_class):
        # Arrange

        # Act
        ok, project = self.pb.from_project_type(proj_type)

        # Assert
        self.assertTrue(ok)
        self.assertIsNotNone(project)
        self.assertTrue(isinstance(project, expected_class))

    @parameterized.expand([
        ("Buildings", GenericProject),
        ("Waterworks", GenericProject),
        ("Transport", GenericProject),
        ("Hospitals", GenericProject),
        ("Communications", GenericProject),
    ])
    def test_cannot_get_from_sector_when_not_implemented(self, proj_type, expected_class):
        # Arrange

        # Act
        ok, project = self.pb.from_project_type(proj_type)

        # Assert
        self.assertFalse(ok)

    def test_project_properly_formed(self):
        # Arrange
        _, project = self.pb.from_project_type("Energy")

        # Act
        ok, err = project.params_from_description("solar power 10 MW")

        # Assert
        self.assertTrue(ok)
        self.assertIsNotNone(project)
        self.assertTrue(isinstance(project, Energy))
        self.assertEqual(123, project.get_param_value("power_generated"))   # Comes from mock parser

    def test_project_from_json_if_no_type(self):
        # Arrange
        j_dict = {"name": "some project"}

        # Act
        ok, p = self.pb.from_json(j_dict)

        # Assert
        self.assertFalse(ok)

    @parameterized.expand([
        ("Energy", Energy, ["power_generated", "energy_type"]),
        ("Roads", Road, ['length', 'lanes', 'surface_type']),
        ("Bridges", Bridge, ['length', 'lanes']),
        ("Railways", Railway, ['length']),
        ("Other", GenericProject, ['gallons_diesel', 'tons_concrete']),
    ])
    def test_project_from_json_if_type(self, proj_type, expected_class, required_params):
        # Arrange
        j_dict = {"name": "some project", "project_type": proj_type}
        for p in required_params:
            j_dict[p] = 0

        # Act
        ok, p = self.pb.from_json(j_dict)

        print(p)
        # Assert
        self.assertTrue(ok)
        self.assertTrue(isinstance(p, expected_class))

    @parameterized.expand([
        ("Buildings", GenericProject),
        ("Waterworks", GenericProject),
        ("Transport", GenericProject),
        ("Hospitals", GenericProject),
        ("Communications", GenericProject),
    ])
    def test_cannot_get_from_json_when_not_implemented(self, proj_type, expected_class):
        # Arrange
        j_dict = {"name": "some project", "project_type": proj_type}

        # Act
        ok, p = self.pb.from_json(j_dict)

        # Assert
        self.assertFalse(ok)
        self.assertTrue("'project_type' required and must be one of" in p)
