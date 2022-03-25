from EnvironmentalImpact.UnitConversions import MEGAWATTS, FEET, SQR_FEET, TONS
from Projects.IProject import IProject
from Projects.Rules import ENERGY_TYPE, POWER_OUTPUT
from Projects.Rules import REQUIRED_DESCRIPTORS, CALCULATED_DESCRIPTORS, FACTS, RULES, PROJECT_TYPE
from Projects.Rules import SURFACE_AREA, TONS_CONCRETE, TONS_STEEL, AREA
from Projects.ProjectTypes import ProjectType

#
# Energy Construction Rules
# wind turbine calculation: https://sciencing.com/much-land-needed-wind-turbines-12304634.html
# solar panel calculation: https://palmetto.com/learning-center/blog/how-much-roof-space-is-needed-for-solar-panels
#
ENERGY_DATA = {
    PROJECT_TYPE: ProjectType.ENERGY.name.lower(),
    REQUIRED_DESCRIPTORS:  [
        (POWER_OUTPUT, MEGAWATTS), (ENERGY_TYPE, ENERGY_TYPE), (AREA, SQR_FEET)
    ],
    CALCULATED_DESCRIPTORS: [
        (TONS_CONCRETE, TONS), (TONS_STEEL, TONS)
    ],
    FACTS: {
        POWER_OUTPUT: 100,      # MW
        ENERGY_TYPE: "solar",
        AREA: 80000,
        "sq_ft_in_acre": 43560,
        "acres_per_MW": .75,
        "MW_per_turbine": 2,
        "sq_feet_per_panel": 17.5,
        "MW_from_coal": 2.46,
        "lbs_per_ton": 2000,
        "to_kg": 2.20462,
        "kg_to_yd3": 1839.92,
        "yd3_concrete": 4360000,
        "kg_per_ton": 907.185,
        "steel_in_hoover_dam": 156300000,

        # may not be needed
        "steel_for_plant": 82545,  # kg -- these amounts could be off
        "aluminum": 596,  # kg
        "cast_iron": 14210,  # kg
        "copper": 2544,  # kg
        "plastic": 13508  # kg
    },
    RULES: [
        f"number_turbines = (({AREA} / sq_ft_in_acre ) / acres_per_MW) / MW_per_turbine",
        f"number_solar_panels = ({AREA} / sq_feet_per_panel",
        f"kg_coal = (({POWER_OUTPUT} / MW_from_coal) * to_tons) / to_kg",
        f"g_uranium = {POWER_OUTPUT} / 1",
        f"kg_concrete = {POWER_OUTPUT} / lbs_per_ton * yd3_concrete * kg_to_yd3",
        f"{TONS_CONCRETE} = kg_concrete / kg_per_ton",
        f"{TONS_STEEL} = steel_in_hoover_dam * {POWER_OUTPUT} / lbs_per_ton * lbs_per_ton",

    ]
}


class Energy(IProject):
    def __init__(self, logger):
        super().__init__(logger)
        self._init(ENERGY_DATA)

    @staticmethod
    def from_json(logger, json_dict):
        b = Energy(logger)
        return b._build_from_json(json_dict)

    @staticmethod
    def register(builder):
        builder.add_project_type(ENERGY_DATA[PROJECT_TYPE], Energy)