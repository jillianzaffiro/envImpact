from Common.Logger import Logger
from Projects.GenericProject import IProject
from Projects.Energy import Energy
from Projects.Rules import ENERGY_TYPE, AREA
from Projects.Bridge import Bridge
from Projects.Rules import TONS_CONCRETE, GALLONS_DIESEL, SURFACE_AREA
from RulesEngine.RulesEngine import RulesEngine, Fact, Rule
from EnvironmentalImpact.ImpactConversions import tons_co2_per_ton_concrete, tons_co2_per_gallon_diesel
from EnvironmentalImpact.UnitConversions import sq_meter_per_sq_foot, ton_per_KG
from EnvironmentalImpact.LCAConnector import LCAConnector


class CO2Predictor:
    def __init__(self, logger: Logger, lca: LCAConnector):
        self.lgr = logger
        self.lca = lca

    FACTS = {
        "tons_co2_per_ton_concrete": tons_co2_per_ton_concrete,
        "tons_co2_per_gallon_diesel": tons_co2_per_gallon_diesel
    }

    RULES = [
        f"co2_concrete = {TONS_CONCRETE} * tons_co2_per_ton_concrete",
        f"co2_diesel = {GALLONS_DIESEL} * tons_co2_per_gallon_diesel",
        f"co2 = co2_concrete + co2_diesel",
    ]

    def co2_emissions_method_a(self, project: IProject):
        self.lgr.info("Calculating using method a")
        rules_engine = self._get_clear_rules_engine()
        rules_engine.add_fact(Fact("has_value", TONS_CONCRETE, project.get_param_value(TONS_CONCRETE)))
        rules_engine.add_fact(Fact("has_value", GALLONS_DIESEL, project.get_param_value(GALLONS_DIESEL)))
        co2 = rules_engine.query("has_value", "co2")
        return True, co2[0]

    def co2_emissions_method_b(self, project: IProject):
        self.lgr.info("Calculating using method b")

        if isinstance(project, Energy):
            area = project.get_param_value(AREA)
            ok, results = self.lca.get_co2(area)
            if ok:
                co2 = results * ton_per_KG
                return True, co2
            else:
                return False, results
        elif isinstance(project, Bridge):
            area = project.get_param_value(SURFACE_AREA) * sq_meter_per_sq_foot
            ok, results = self.lca.get_co2(area)
            if ok:
                co2 = results * ton_per_KG
                return True, co2
            else:
                return False, results
        else:
            return self.co2_emissions_method_a(project)

    def _get_clear_rules_engine(self):
        rules_engine = RulesEngine()
        for f in self.FACTS.keys():
            rules_engine.add_fact(Fact("has_value", f, self.FACTS[f]))
        for r in self.RULES:
            rules_engine.add_rule(Rule(r))
        rules_engine.set_default_behavior(0.0)
        return rules_engine
