import unittest
from parameterized import parameterized

from Projects.ProjectTypes import ProjectType
from DescriptionProcessing.ProjectDescription import ProjectDescription


class ProjectDescriptionsTests(unittest.TestCase):

    def test_get_aggregated_sector(self):
        # Arrange
        p = ProjectDescription()
        p.sector = "rail"
        p.subsector = "rail"

        # Act
        category, label = p.get_label()

        # Assert
        self.assertEqual("railways", category.lower())
        self.assertEqual(5, label)

    @parameterized.expand([
        ("energy", "Atomic energy", ProjectType.ENERGY),
        ("oil & gas production", "Oil pipeline", ProjectType.ENERGY),
        ("Solar", "solar electricity", ProjectType.ENERGY),
        ("transport", "highway", ProjectType.ROADS),
        ("transport", "bridge", ProjectType.BRIDGES),
        ("transport", "high speed rail", ProjectType.RAILWAYS),
        ("transport", "bus station", ProjectType.TRANSPORT),
        ("transport", "transit", ProjectType.RAILWAYS),
        ("transport", "rail", ProjectType.RAILWAYS),
        ("industrial", "iron plant", ProjectType.BUILDINGS),
        ("real", "urban housing", ProjectType.BUILDINGS),
        ("urban", "supermarket", ProjectType.BUILDINGS),
    ])
    def test_get_aggregated_sector_multi(self, sector, subsector, aggregated_sector):
        # Arrange
        p = ProjectDescription()
        p.sector = sector
        p.subsector = subsector

        # Act
        category, label = p.get_label()

        # Assert
        self.assertEqual(aggregated_sector.name, category.upper())
