from EnvironmentalImpact.UnitConversions import MEGAWATTS, FEET, SQR_FEET, TONS
from Projects.IProject import IProject
from Projects.Rules import ENERGY_TYPE, POWER_OUTPUT
from Projects.Rules import REQUIRED_DESCRIPTORS, CALCULATED_DESCRIPTORS, FACTS, RULES, PROJECT_TYPE
from Projects.Rules import SURFACE_AREA, TONS_CONCRETE, TONS_STEEL, AREA
from Projects.ProjectTypes import ProjectType

#
# Energy Construction Rules
# wind turbine materials:
# https://www.usgs.gov/faqs/what-materials-are-used-make-wind-turbines#:~:text=According%20to%20a%20report%20from,aluminum%20(0%2D2%25)
# https://www.forbes.com/sites/christopherhelman/2021/04/28/how-green-is-wind-power-really-a-new-report-tallies-up-the-carbon-cost-of-renewables/?sh=274892f73cd9
# hydropower plant materials:
# https://www.pnnl.gov/materials-science-hydropower
# https://www.hydropower.org/factsheets/greenhouse-gas-emissions#:~:text=The%20IPCC%20states%20that%20hydropower,490%20gCO%E2%82%82%2Deq%2FkWh
#
# wind turbine calculation: https://sciencing.com/much-land-needed-wind-turbines-12304634.html
# solar panel calculation: https://palmetto.com/learning-center/blog/how-much-roof-space-is-needed-for-solar-panels
# coal calculation: https://www.mcginley.co.uk/news/how-much-of-each-energy-source-does-it-take-to-power-your-home/bp254/
# hydropower calculation:
# https://powerauthority.org/about-us/history-of-hoover#:~:text=Presently%2C%20Hoover%20Dam%20can%20produce,southern%20California%2C%20and%20southern%20Nevada
# https://www.usbr.gov/lc/hooverdam/faqs/damfaqs.html#:~:text=How%20much%20concrete%20is%20in,dam%2C%20powerplant%20and%20appurtenant%20works
# https://www.traditionaloven.com/building/masonry/concrete/convert-cubic-yard-cu-yd-concrete-to-kilogram-kg-of-concrete.html#:~:text=One%20cubic%20yard%20of%20concrete,equals%20to%201%2C839.92%20kg%20%2D%20kilo
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