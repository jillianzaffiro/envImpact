from Common.Logger import Logger
from Projects.GenericProject import IProject
from EnvironmentalImpact.CO2Predictor import CO2Predictor
from EnvironmentalImpact.MonteCarloSim import MonteCarloSim
from EnvironmentalImpact.LCAConnector import LCAConnector
from EnvironmentalImpact.LCAConnectorMC import LCAConnectorMC

def get_impact_predictor(logger: Logger):
    lca = LCAConnector(logger)
    lcamc = LCAConnectorMC(logger)
    co2 = CO2Predictor(logger, lca)
    mc = MonteCarloSim(logger, lcamc)
    ip = ImpactPredictor(logger, co2, mc)
    return ip


class ImpactPredictor:
    def __init__(self, logger: Logger, co2: CO2Predictor, mc: MonteCarloSim):
        self.logger = logger
        self._co2 = co2
        self._mc = mc

    def get_co2(self, project: IProject):
        if self._co2 is not None:
            ok_a, co2_a = self._co2.co2_emissions_method_a(project)
            ok_b, co2_b = self._co2.co2_emissions_method_b(project)
        else:
            ok_a, co2_a = self._mc.co2_emissions_method_a(project)
            ok_b, co2_b = self._mc.co2_emissions_method_b(project)
        return ok_a, ok_b, co2_a, co2_b
