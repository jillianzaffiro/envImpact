import EnvironmentalImpact.UnitConversions as cvt
from Projects.Rules import LENGTH, LANES, POWER_OUTPUT
from DescriptionProcessing.CBERT.BertPreprocessing import BertPreprocessor


class DescriptionParser:
    def __init__(self, bpp: BertPreprocessor):
        self._bpp = bpp

    def get_param(self, param_name, description):
        if param_name == LENGTH:
            return self.get_length_param(description)
        if param_name == LANES:
            return self.get_lanes_param(description)
        if param_name == POWER_OUTPUT:
            return self.get_power_param(description)
        return None, 0.0

    def get_power_param(self, description):
        units = {'kw': ['kw', 'kw'],
                 'mw': ['mw', 'mw'],
                 }
        description = description.replace("kilowatt", 'kw')
        description = description.replace("megawatt", 'mw')
        unit, value = self._get_measure(units, description)
        return cvt.convert_units(value, unit, "mw")

    def get_length_param(self, description):
        units = {'feet': ['feet', 'ft', 'foot'],
                 'mile': ['mile', 'miles'],
                 'meters': ['meter', 'meters'],
                 'km': ['km', 'kilometers']}
        unit, value = self._get_measure(units, description)
        return cvt.convert_units(value, unit, "feet")

    def get_lanes_param(self, description):
        units = {'lanes': ['lane', 'lanes'], }
        unit, value = self._get_measure(units, description)
        return cvt.convert_units(value, unit, "lanes")

    def _get_measure(self, units, description):
        tokens = self._bpp.tokenize_sentence_with_numbers(description)
        measure_value = 0
        find_units = False
        for t in tokens:
            if find_units:
                for unit in units.keys():
                    if t in units[unit]:
                        return unit, measure_value
            try:
                measure_value = int(t)
                find_units = True
            except Exception:
                measure_value = 0
        return None, 0.0
