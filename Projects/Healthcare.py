import EnvironmentalImpact.ImpactConversions as cvt
from EnvironmentalImpact.UnitConversions import FEET, SQR_FEET, TONS
from Projects.IProject import IProject
from Projects.Rules import REQUIRED_DESCRIPTORS, CALCULATED_DESCRIPTORS, FACTS, RULES, PROJECT_TYPE
from Projects.Rules import LENGTH, LANES
from Projects.Rules import WIDTH, SURFACE_AREA, TONS_CONCRETE, TONS_STEEL, AREA
from Projects.ProjectTypes import ProjectType

#
# Healthcare Sources:
#https://elakeside.com/medical/selecting-the-right-material-for-healthcare-facilities/
HEALTHCARE_DATA = {
    PROJECT_TYPE: ProjectType.HEALTHCARE.name.lower(),

    REQUIRED_DESCRIPTORS:  [
        (AREA, SQR_FEET)
    ],

    CALCULATED_DESCRIPTORS: [

    ],

    FACTS: {
        AREA: 5000
    },

    RULES: [

    ]
}


class Healthcare(IProject):
    def __init__(self, logger):
        super().__init__(logger)
        self._init(HEALTHCARE_DATA)

    @staticmethod
    def from_json(logger, json_dict):
        b = Healthcare(logger)
        return b._build_from_json(json_dict)

    @staticmethod
    def register(builder):
        builder.add_project_type(HEALTHCARE_DATA[PROJECT_TYPE], Healthcare)
