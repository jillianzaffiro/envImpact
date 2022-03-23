import unittest
from parameterized import parameterized

from DescriptionProcessing.ProjectDescription import ProjectType
from tests.Mocks import MockPrediction


class ProjectTypesTests(unittest.TestCase):

    def test_can_show_sectors(self):
        # Arrange

        # Act
        other = ProjectType.OTHER

        # Assert
        self.assertEqual(other, 0)

    def test_can_translate_back(self):
        # Arrange
        p = MockPrediction()
        p.add_row([0, 0, 3, 0, 0, 0, 0, 0])

        # Act
        res = ProjectType.translate_prediction(p)

        # Assert
        self.assertEqual(0.0, res[ProjectType.OTHER.name])
        self.assertEqual(0.0, res[ProjectType.ENERGY.name])
        self.assertEqual(1.0, res[ProjectType.ROADS.name])
        self.assertEqual(0.0, res[ProjectType.BRIDGES.name])
        self.assertEqual(0.0, res[ProjectType.BUILDINGS.name])
        self.assertEqual(0.0, res[ProjectType.RAILWAYS.name])
        self.assertEqual(0.0, res[ProjectType.WATERWORKS.name])
        self.assertEqual(0.0, res[ProjectType.TRANSPORT.name])

    def test_can_distribute_results(self):
        # Arrange
        p = MockPrediction()
        p.add_row([0, 1, 0, 1, 0, 0, 0, 0])

        # Act
        res = ProjectType.translate_prediction(p)

        # Assert
        self.assertEqual(0.0, res[ProjectType.OTHER.name])
        self.assertEqual(0.5, res[ProjectType.ENERGY.name])
        self.assertEqual(0.0, res[ProjectType.ROADS.name])
        self.assertEqual(0.5, res[ProjectType.BRIDGES.name])
        self.assertEqual(0.0, res[ProjectType.BUILDINGS.name])
        self.assertEqual(0.0, res[ProjectType.RAILWAYS.name])
        self.assertEqual(0.0, res[ProjectType.WATERWORKS.name])
        self.assertEqual(0.0, res[ProjectType.TRANSPORT.name])

    @parameterized.expand([
        ([1, 0, 0, 0, 0, 0, 0, 0], ProjectType.OTHER.name),
        ([0, 1, 0, 0, 0, 0, 0, 0], ProjectType.ENERGY.name),
        ([0, 0, 1, 0, 0, 0, 0, 0], ProjectType.ROADS.name),
        ([0, 0, 0, 1, 0, 0, 0, 0], ProjectType.BRIDGES.name),
        ([0, 0, 0, 0, 1, 0, 0, 0], ProjectType.BUILDINGS.name),
        ([0, 0, 0, 0, 0, 1, 0, 0], ProjectType.RAILWAYS.name),
        ([0, 0, 0, 0, 0, 0, 1, 0], ProjectType.WATERWORKS.name),
        ([0, 0, 0, 0, 0, 0, 0, 1], ProjectType.TRANSPORT.name),
    ])
    def test_can_translate_all_enums(self, data_row, res_name):
        # Arrange
        p = MockPrediction()
        p.add_row(data_row)

        # Act
        res = ProjectType.translate_prediction(p)

        # Assert
        self.assertEqual(1.0, res[res_name])

    def test_can_validate_sector(self):
        # Arrange

        # Act
        valid = ProjectType.is_valid_sector("Bridges")

        # Assert
        self.assertTrue(valid)

    def test_can_invalidate_sector(self):
        # Arrange

        # Act
        valid = ProjectType.is_valid_sector("Rockets")

        # Assert
        self.assertFalse(valid)

    def test_can_convert_sector_name(self):
        # Arrange

        # Act
        val = ProjectType.sector_label("Transport")

        # Assert
        self.assertEqual(7, val)
