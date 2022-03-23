from Projects.ProjectTypes import ProjectType


class ProjectDescription:
    def __init__(self):
        self.project_id = None
        self.name = None
        self.description = None
        self.keywords = None
        self.country = None
        self.location = None
        self.sector = None
        self.subsector = None
        self.budget = 0.0
        self.lat = 0.0
        self.long = 0.0

    def to_json(self):
        return self.__dict__

    @staticmethod
    def from_json(json_dict):
        p = ProjectDescription()
        p.project_id = json_dict['project_id']
        p.description = json_dict['description']
        p.keywords = json_dict['keywords']
        p.country = json_dict['country']
        p.location = json_dict['location']
        p.sector = json_dict['sector']
        p.subsector = json_dict['subsector']
        p.budget = json_dict['budget']
        p.lat = json_dict['lat']
        p.name = json_dict['name']
        p.long = json_dict['long']
        return p

    def get_label(self):
        sector = self.sector.lower()
        subsector = self.subsector.lower()
        category = ProjectType.OTHER
        if 'energy' in sector or 'oil & gas' in sector or "electricity" in subsector:
            category = ProjectType.ENERGY
        elif 'highway' in subsector:
            category = ProjectType.ROADS
        elif 'bridge' in subsector:
            category = ProjectType.BRIDGES
        elif "industrial" in sector or "real" in sector or 'supermarket' in subsector:
            category = ProjectType.BUILDINGS
        elif 'housing' in subsector or 'jail' in subsector:
            category = ProjectType.BUILDINGS
        elif 'transit' in subsector or 'rail' in subsector:
            category = ProjectType.RAILWAYS
        elif 'water' in sector:
            category = ProjectType.WATERWORKS
        elif 'transport' in sector:
            category = ProjectType.TRANSPORT
        elif 'hospital' in subsector:
            category = ProjectType.HOSPITALS
        elif 'communication' in sector:
            category = ProjectType.COMMUNICATIONS
        elif ('' == sector and '' == subsector) or \
             ('social' == sector and 'other' == subsector) or \
             ('urban' in sector and 'other' == subsector) or \
             ('other' == sector and 'other' == subsector):
            category = ProjectType.OTHER
        elif 'tourism' in sector:
            category = ProjectType.OTHER
        elif 'logistics' in sector:
            category = ProjectType.OTHER
        elif 'mining' in sector:
            category = ProjectType.OTHER
        else:
            print(f"OTHER:  {sector}/{subsector}")

        return category.name, category.value
