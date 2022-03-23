from Common.Logger import Logger
from EnvironmentalImpact.LCAConnector import LCAConnector
from Projects.DescriptionParsing import DescriptionParser

class MockLCA(LCAConnector):
    def __init__(self):
        pass

    def get_co2(self, surface_area):
        return True, 100.0 * surface_area


class MockPrediction:
    def __init__(self):
        self.data = []

    def add_row(self, data_row):
        self.data.append(data_row)

    def min(self):
        return 0

    def __getitem__(self, item):
        return self.data[item]


class MockLogger(Logger):
    def __init__(self):
        super().__init__("test")

    def info(self, msg):
        pass


class MockDescriptionParser(DescriptionParser):
    def __init__(self):
        pass

    def get_param(self, param, description):
        return True, 123
