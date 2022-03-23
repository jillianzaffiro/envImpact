from Common.Logger import Logger
from Projects.IProject import IProject
from Projects.Rules import REQUIRED_DESCRIPTORS, CALCULATED_DESCRIPTORS, FACTS, RULES, PROJECT_TYPE
from Projects.Rules import GALLONS_DIESEL, TONS_CONCRETE
from EnvironmentalImpact.UnitConversions import GALLONS, TONS
from Projects.ProjectTypes import ProjectType


GENERIC_PROJECT_DATA = {
    PROJECT_TYPE: ProjectType.OTHER.name.lower(),
    REQUIRED_DESCRIPTORS:  [
        (GALLONS_DIESEL, GALLONS), (TONS_CONCRETE, TONS)
    ],
    CALCULATED_DESCRIPTORS: [
    ],
    FACTS: {
        GALLONS_DIESEL: 1000,
        TONS_CONCRETE: 100
    },
    RULES: [
    ]
}


class GenericProject(IProject):
    def __init__(self, logger):
        super().__init__(logger)
        self._init(GENERIC_PROJECT_DATA)

    @staticmethod
    def from_json(logger: Logger, json_dict: dict):
        b = GenericProject(logger)
        return b._build_from_json(json_dict)

    @staticmethod
    def register(builder):
        builder.add_project_type(GENERIC_PROJECT_DATA[PROJECT_TYPE], GenericProject)
