from Common.Logger import Logger
from DescriptionProcessing.CBERT.BertPreprocessing import BertPreprocessor
from Projects.Bridge import Bridge
from Projects.Road import Road
from Projects.Energy import Energy
from Projects.DescriptionParsing import DescriptionParser
from Projects.GenericProject import GenericProject
from Projects.Railway import Railway


def get_project_builder(logger: Logger, bpp: BertPreprocessor):
    description_parser = DescriptionParser(bpp)
    pb = ProjectBuilder(logger, description_parser)
    return pb


class ProjectBuilder:
    def __init__(self, logger: Logger, parser: DescriptionParser):
        self._lgr = logger
        self._parser = parser
        self._project_type_to_project = {}
        Bridge.register(self)
        Road.register(self)
        Energy.register(self)
        GenericProject.register(self)
        Railway.register(self)

    def add_project_type(self, project_type, project_class):
        self._project_type_to_project[project_type] = project_class

    def from_project_type(self, project_type):
        if project_type.lower() in self._project_type_to_project:
            p_class = self._project_type_to_project[project_type.lower()]
            p = p_class(self._lgr)
            p.set_description_parser(self._parser)
            return True, p
        return False, []

    def from_json(self, json_dict: dict) -> (bool, object):
        valid_types = self._project_type_to_project
        if "project_type" not in json_dict:
            err = f"'project_type' required. Must be one of {valid_types.keys()}"
            return False, err

        requested_type = json_dict["project_type"].lower()
        if requested_type not in valid_types:
            err = f"'project_type' required and must be one of {valid_types.keys()}"
            return False, err

        p_class = valid_types[requested_type]
        return p_class.from_json(self._lgr, json_dict)
