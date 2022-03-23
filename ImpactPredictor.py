from Common.Logger import Logger
from Projects.GenericProject import IProject
from EnvironmentalImpact.CO2Predictor import CO2Predictor
from EnvironmentalImpact.LCAConnector import LCAConnector


def get_impact_predictor(logger: Logger):
    lca = LCAConnector(logger)
    co2 = CO2Predictor(logger, lca)
    ip = ImpactPredictor(logger, co2)
    return ip


class ImpactPredictor:
    def __init__(self, logger: Logger, co2: CO2Predictor):
        self.logger = logger
        self._co2 = co2

    def get_co2(self, project: IProject):
        ok_a, co2_a = self._co2.co2_emissions_method_a(project)
        ok_b, co2_b = self._co2.co2_emissions_method_b(project)
        return ok_a, ok_b, co2_a, co2_b
