import unittest
from ImpactPredictor import get_impact_predictor, ImpactPredictor, CO2Predictor, MonteCarloSim
from Projects.GenericProject import GenericProject
from Projects.Bridge import Bridge
from tests.Mocks import MockLCA, MockMC, MockLogger


class TestCO2(unittest.TestCase):
    def setUp(self) -> None:
        lca = MockLCA()
        self.lgr = MockLogger()
        self.co2 = CO2Predictor(self.lgr, lca)

    def test_can_instantiate_co2(self):
        # Arrange
        lca = MockLCA()
        lgr = MockLogger()

        # Act
        co2 = CO2Predictor(lgr, lca)

        # Assert
        self.assertIsNotNone(co2)

    def setUp_mc(self) -> None:
        lcamc = MockMC()
        self.lgr = MockLogger()
        self.mc = MonteCarloSim(self.lgr, lcamc)

    def test_can_instantiate_co2_mc(self):
        # Arrange
        lcamc = MockMC()
        lgr = MockLogger()

        # Act
        mc = MonteCarloSim(lgr, lcamc)

        # Assert
        self.assertIsNotNone(mc)

    def test_can_calculate_from_concrete(self):
        # Arrange
        _, project = GenericProject.from_json(self.lgr, {"tons_concrete": 1000.0, "gallons_diesel": 0.0})

        # Act
        ok, res = self.co2.co2_emissions_method_a(project)

        # Assert
        self.assertTrue(ok)
        self.assertAlmostEqual(242.0, res, places=1)

    def test_can_calculate_from_diesel(self):
        # Arrange
        _, project = GenericProject.from_json(self.lgr, {"tons_concrete": 0.0, "gallons_diesel": 15_000.0})

        # Act
        ok, res = self.co2.co2_emissions_method_a(project)

        # Assert
        self.assertTrue(ok)
        self.assertAlmostEqual(168.0, res, places=1)

    def test_can_calculate_from_concrete_and_diesel(self):
        # Arrange
        _, project = GenericProject.from_json(self.lgr, {"tons_concrete": 2000.0, "gallons_diesel": 10_000.0})

        # Act
        ok, res = self.co2.co2_emissions_method_a(project)

        # Assert
        # Linear combination of the two
        #   2 * 242.0 + 2/3 * 168 =
        self.assertTrue(ok)
        self.assertAlmostEqual(596.0, res, places=1)

    def test_both_methods_same_for_non_bridges(self):
        # Arrange
        project = GenericProject(self.lgr)
        project.tons_concrete = 2000.00
        project.gallons_diesel = 10_000.00

        # Act
        res_a = self.co2.co2_emissions_method_a(project)
        res_b = self.co2.co2_emissions_method_b(project)

        # Assert
        self.assertAlmostEqual(res_a, res_b)

    def test_methods_diff_for_bridges(self):
        # Arrange
        params = {"name": "Test Bridge", "length": 100, "lanes": 2}
        _, project = Bridge.from_json(self.lgr, params)

        # Act
        ok_a, res_a = self.co2.co2_emissions_method_a(project)
        ok_b, res_b = self.co2.co2_emissions_method_b(project)

        # Assert
        self.assertTrue(ok_a)
        self.assertAlmostEqual(130.68, res_a, places=1)
        self.assertTrue(ok_b)
        self.assertAlmostEqual(49.15, res_b, places=1)


class TestImpact(unittest.TestCase):
    def setUp(self) -> None:
        lgr = MockLogger()
        self.ip = get_impact_predictor(lgr)

    def test_can_instantiate_impact(self):
        # Arrange

        # Act

        # Assert
        self.assertIsNotNone(self.ip)

    def test_can_calculate_from_non_bridge(self):
        # Arrange
        lgr = MockLogger()
        _, project = GenericProject.from_json(lgr, {"tons_concrete": 2000.0, "gallons_diesel": 10_000.0})

        # Act
        ok_a, ok_b, res_a, res_b = self.ip.get_co2(project)

        # Assert
        self.assertTrue(ok_a)
        self.assertTrue(ok_b)
        self.assertAlmostEqual(596.0, res_a, places=1)
        self.assertAlmostEqual(596.0, res_b, places=1)

    def test_can_calculate_from_bridge(self):
        # Arrange
        lca = MockLCA()
        lgr = MockLogger()
        co2 = CO2Predictor(lgr, lca)
        ip = ImpactPredictor(lgr, co2, None)      # We need the mock LCA since openLCA does not run in CI
        params = {"name": "Test Bridge", "length": 100, "lanes": 2}
        _, project = Bridge.from_json(lgr, params)

        # Act
        ok_a, ok_b, res_a, res_b = ip.get_co2(project)

        # Assert
        self.assertTrue(ok_a)
        self.assertTrue(ok_b)
        # 100 ft * 2 lanes * 24 ft per lane = 4800 ft^2
        # 926 tons concrete * 242 / 1000 = 130.68
        self.assertAlmostEqual(130.68, res_a, places=1)
        # 4800 ft^2 = 446 m^2 => 44600 kG => 49.17
        self.assertAlmostEqual(49.17, res_b, places=1)

    # this will be a test for the monte carlo simulator - not fully fleshed out
    # def test_can_calculate_from_bridge_mc(self):
    #     # Arrange
    #     lcamc = MockMC()
    #     lgr = MockLogger()
    #     mc = MonteCarloSim(lgr, lcamc)
    #     ip = ImpactPredictor(lgr, None, mc)  # We need the mock LCA since openLCA does not run in CI
    #     params = {"name": "Test Bridge", "length": 100, "lanes": 2}
    #     _, project = Bridge.from_json(lgr, params)
    #
    #     # Act
    #     ok_a, ok_b, res_a, res_b = ip.get_co2(project)
    #
    #     # Assert
    #     self.assertTrue(ok_a)
    #     self.assertTrue(ok_b)
    #     # 100 ft * 2 lanes * 24 ft per lane = 4800 ft^2
    #     # 926 tons concrete * 242 / 1000 = 130.68
    #     self.assertAlmostEqual(130.68, res_a, places=1)
    #     # 4800 ft^2 = 446 m^2 => 44600 kG => 49.17
    #     self.assertAlmostEqual(49.17, res_b, places=1)
