from enum import IntEnum, unique


@unique
class ProjectType(IntEnum):
    """Aggregated Sector"""
    ENERGY = 1
    ROADS = 2
    BRIDGES = 3
    BUILDINGS = 4
    RAILWAYS = 5
    WATERWORKS = 6
    TRANSPORT = 7
    HOSPITALS = 8
    COMMUNICATIONS = 9
    OTHER = 0

    @staticmethod
    def sector_list():
        s = {}
        for name, member in ProjectType.__members__.items():
            s[name.lower()] = int(member)
        return s

    @staticmethod
    def is_valid_sector(name):
        return name.upper() in ProjectType.__members__

    @staticmethod
    def sector_label(sector_name):
        return int(ProjectType[sector_name.upper()])

    @staticmethod
    def num_sectors():
        return len(ProjectType.__members__)

    @staticmethod
    def translate_prediction(prediction):
        total_prob = 0.0
        min_val = prediction.min()
        sector = {}
        prediction = prediction[0]
        for name, member in ProjectType.__members__.items():
            idx = int(member)
            if idx < len(prediction):
                p = prediction[idx] - min_val
            else:
                p = 0
            total_prob += p
            sector[name] = p

        for s in sector.keys():
            sector[s] = sector[s] / total_prob

        return sector
