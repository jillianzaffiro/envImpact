from EnvironmentalImpact.UnitConversions import MEGAWATTS
from Projects.IProject import IProject
from Projects.Rules import ENERGY_TYPE, POWER_OUTPUT
from Projects.Rules import REQUIRED_DESCRIPTORS, CALCULATED_DESCRIPTORS, FACTS, RULES, PROJECT_TYPE
from Projects.ProjectTypes import ProjectType

#
# Energy Construction Rules
#
ENERGY_DATA = {
    PROJECT_TYPE: ProjectType.ENERGY.name.lower(),
    REQUIRED_DESCRIPTORS:  [
        (POWER_OUTPUT, MEGAWATTS), (ENERGY_TYPE, ENERGY_TYPE)
    ],
    CALCULATED_DESCRIPTORS: [
    ],
    FACTS: {
        POWER_OUTPUT: 100,      # MW
        ENERGY_TYPE: "solar",
    },
    RULES: [
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
