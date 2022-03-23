# from __future__ import annotations
from abc import ABC, abstractmethod
from Common.Logger import Logger
from Projects.Rules import REQUIRED_DESCRIPTORS, CALCULATED_DESCRIPTORS, FACTS, RULES, PROJECT_TYPE
from RulesEngine.RulesEngine import RulesEngine, Rule, Fact


class Parameter:
    def __init__(self, name, value, units):
        self.name = name
        self.value = value
        self.units = units
        self.forced = False


class IProject(ABC):
    def __init__(self, logger: Logger):
        self.lgr = logger
        self._base_parameters = {}
        self._calculated_parameters = {}
        self._project_type = None
        self.__description_parser = None
        self.__data_map = None

    def _init(self, data_map):
        self.__data_map = data_map
        self._project_type = data_map[PROJECT_TYPE]
        for p in data_map[REQUIRED_DESCRIPTORS]:
            param = Parameter(p[0], None, p[1])
            self._base_parameters[param.name] = param
        for p in data_map[CALCULATED_DESCRIPTORS]:
            param = Parameter(p[0], None, p[1])
            self._calculated_parameters[param.name] = param
        self._recalculate()

    def set_description_parser(self, parser):
        self.__description_parser = parser

    def params_from_description(self, description):
        if self.__description_parser is None:
            err_msg = "Description Parser not set, cannot parse descriptions"
            self.lgr.error(err_msg)
            return False, [err_msg]
        for param in self._base_parameters.keys():
            ok, val = self.__description_parser.get_param(param, description)
            if ok:
                p = self._base_parameters[param]
                p.value = val
                p.forced = True
        self._recalculate()
        return True, []

    def get_param_value(self, param_name):
        p = self.get_param(param_name)
        if p is None:
            return None
        else:
            return p.value

    def get_param(self, param_name):
        if param_name in self._base_parameters:
            return self._base_parameters[param_name]
        if param_name in self._calculated_parameters:
            return self._calculated_parameters[param_name]
        return None

    @staticmethod
    @abstractmethod
    def register(builder):
        pass

    @staticmethod
    @abstractmethod
    def from_json(logger: Logger, json_dict: dict) -> (bool, object):
        # Derived class should construct itself then call _build_from_json
        pass

    def to_json(self) -> dict:
        json_dict = {}
        for k in self._base_parameters.keys():
            json_dict[k] = self._base_parameters[k].value
        for k in self._calculated_parameters.keys():
            json_dict[k] = self._calculated_parameters[k].value
        json_dict["project_type"] = self._project_type
        return json_dict

    def _recalculate(self):
        e = RulesEngine()
        project_facts = self.__data_map[FACTS]
        project_rules = self.__data_map[RULES]
        for f in project_facts.keys():
            v_var = self.get_param(f)
            if v_var is not None and v_var.forced:
                e.add_fact(Fact("has_value", f, v_var.value))
            else:
                e.add_fact(Fact("has_value", f, project_facts[f]))
        for r_txt in project_rules:
            r = Rule(r_txt)
            var_name = r.left
            v_var = self.get_param(var_name)
            if v_var is not None and v_var.forced:
                e.add_fact(Fact("has_value", var_name, v_var.value))
            e.add_rule(r)

        for p_name in self._base_parameters.keys():
            self.get_param(p_name).value = e.query("has_value", p_name)[0]
        for p_name in self._calculated_parameters.keys():
            self.get_param(p_name).value = e.query("has_value", p_name)[0]

    def _build_from_json(self, json_dict: dict):
        ok, err = self._verify_json(json_dict)
        if not ok:
            return False, err

        for param_name in self._base_parameters.keys():
            p = self._base_parameters[param_name]
            p.value = json_dict[param_name]
            p.forced = True

        for param_name in self._calculated_parameters.keys():
            if param_name in json_dict:
                p = self._calculated_parameters[param_name]
                p.value = json_dict[param_name]
                p.forced = True
        self._recalculate()
        return True, self

    def _verify_json(self, json_dict):
        err = []
        for param_name in self._base_parameters.keys():
            units = self._base_parameters[param_name].units
            if param_name not in json_dict:
                err.append(f"'{param_name}' required for {self._project_type}. Add {param_name} in {units}.")
        return len(err) == 0, err
