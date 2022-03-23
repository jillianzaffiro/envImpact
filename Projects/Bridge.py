import EnvironmentalImpact.ImpactConversions as cvt
from EnvironmentalImpact.UnitConversions import FEET, SQR_FEET, TONS
from Projects.IProject import IProject
from Projects.Rules import REQUIRED_DESCRIPTORS, CALCULATED_DESCRIPTORS, FACTS, RULES, PROJECT_TYPE
from Projects.Rules import LENGTH, LANES
from Projects.Rules import WIDTH, SURFACE_AREA, TONS_CONCRETE, TONS_STEEL
from Projects.ProjectTypes import ProjectType

#
# Bridge Construction Rules
#     Use the 'typical' bridge parameters (https://aiimpacts.org/historic-trends-in-bridge-span-length/)
#     Length in Feet
BRIDGE_DATA = {
    PROJECT_TYPE: ProjectType.BRIDGES.name.lower(),

    REQUIRED_DESCRIPTORS:  [
        (LENGTH, FEET), (LANES, LANES)
    ],

    CALCULATED_DESCRIPTORS: [
        (WIDTH, FEET), (SURFACE_AREA, SQR_FEET), (TONS_CONCRETE, TONS), (TONS_STEEL, TONS)
    ],

    FACTS: {
        LENGTH: 1000,
        LANES: 4,
        "bridge_thickness": 18.0 / 12.0,        # 18 inches
        "bridge_lane_width": 24.0,               # 24 feet
        "concrete_weight": cvt.concrete_pounds_per_cubic_foot,
        "pounds_per_ton": cvt.pounds_per_ton,
        "tons_per_foot_steel": 123,
    },

    RULES: [
        f"{WIDTH} = {LANES} * bridge_lane_width",
        f"{SURFACE_AREA} = {LENGTH} * {WIDTH}",
        f"volume = {SURFACE_AREA} * bridge_thickness",
        f"pounds_concrete = volume * concrete_weight",
        f"{TONS_CONCRETE} = pounds_concrete / pounds_per_ton",
        f"{TONS_STEEL} = tons_per_foot_steel * length",
    ]
}


class Bridge(IProject):
    def __init__(self, logger):
        super().__init__(logger)
        self._init(BRIDGE_DATA)

    @staticmethod
    def from_json(logger, json_dict):
        b = Bridge(logger)
        return b._build_from_json(json_dict)

    @staticmethod
    def register(builder):
        builder.add_project_type(BRIDGE_DATA[PROJECT_TYPE], Bridge)
