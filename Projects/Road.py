import EnvironmentalImpact.ImpactConversions as cvt
from EnvironmentalImpact.UnitConversions import FEET, SQR_FEET, TONS, ft_per_mile
from Projects.IProject import IProject
from Projects.Rules import REQUIRED_DESCRIPTORS, CALCULATED_DESCRIPTORS, FACTS, RULES, PROJECT_TYPE
from Projects.Rules import LENGTH, LANES, SURFACE_TYPE
from Projects.Rules import WIDTH, SURFACE_AREA, TONS_CONCRETE, TONS_ASPHALT
from Projects.ProjectTypes import ProjectType

#
# Road Construction Rules
# Use the 'typical' road project
# Length in Feet
# https://www.apai.net/Files/content/DesignGuide/Chapter_4B.pdf
#
ROAD_DATA = {
    PROJECT_TYPE: ProjectType.ROADS.name.lower(),
    REQUIRED_DESCRIPTORS:  [
        (LENGTH, FEET), (LANES, LANES), (SURFACE_TYPE, SURFACE_TYPE)
    ],
    CALCULATED_DESCRIPTORS: [
        (WIDTH, FEET), (SURFACE_AREA, SQR_FEET), (TONS_CONCRETE, TONS), (TONS_ASPHALT, TONS)
    ],
    FACTS: {
        LENGTH: 20 * ft_per_mile,
        LANES: 2,
        SURFACE_TYPE: 'asphalt',
        "road_lane_width": 18.0,                   # 18 feet
        "road_asphalt_thickness": 12.0 / 12.0,     # 12 inches
        "concrete_weight": cvt.concrete_pounds_per_cubic_foot,
        "asphalt_weight": 123,
        "pounds_per_ton": cvt.pounds_per_ton,
    },
    RULES: [
        f"{WIDTH} = {LANES} * road_lane_width",
        f"{SURFACE_AREA} = {LENGTH} * {WIDTH}",
        f"volume = {SURFACE_AREA} * road_asphalt_thickness",
        f"pounds_concrete = volume * concrete_weight",
        f"pounds_asphalt = volume * asphalt_weight",
        f"{TONS_CONCRETE} = pounds_concrete / pounds_per_ton",
        f"{TONS_ASPHALT} = pounds_asphalt / pounds_per_ton",
    ]
}


class Road(IProject):
    def __init__(self, logger):
        super().__init__(logger)
        self._init(ROAD_DATA)

    @staticmethod
    def from_json(logger, json_dict):
        b = Road(logger)
        return b._build_from_json(json_dict)

    @staticmethod
    def register(builder):
        builder.add_project_type(ROAD_DATA[PROJECT_TYPE], Road)
