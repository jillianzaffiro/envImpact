import EnvironmentalImpact.ImpactConversions as cvt
from EnvironmentalImpact.UnitConversions import FEET, SQR_FEET, TONS, ft_per_meter, kg_per_pound, ft_per_mile, ft_per_yard
from Projects.IProject import IProject
from Projects.Rules import REQUIRED_DESCRIPTORS, CALCULATED_DESCRIPTORS, FACTS, RULES, PROJECT_TYPE, TONS_TIMBER
from Projects.Rules import LENGTH, LANES
from Projects.Rules import WIDTH, TONS_CONCRETE, TONS_STEEL, TONS_BALLAST
from Projects.ProjectTypes import ProjectType

'''
Railways:


US Standard Gauge is 4' 8.5 in (https://www.saferack.com/railroad-track-facts-construction-safety/)
http://www.railsystem.net/rail-gauges/

The different gauges can broadly be divided into the following four categories:
Broad Gauge: width 1676 mm to 1524 mm or 5’6” to 5’0”
Standard Gauge: width 1435 mm and 1451 mm or 4’-8⅟2”
Metre Gauge: width 1067 mm, 1000 mm and 915 mm or 3’-6”, 3’-33/8” and 3’-0”
Narrow Gauge: width 762 mm and 610 mm or 2’-6” and 2’-0”.


Materials: (http://www.railroadpart.com/news/steel-rail-raw-material-and-structure.html)
----------
Track  (http://www.railroadpart.com/rail-track-parts/steel-rails.html)
    Length:
        Track length = Length in miles *2
        Sections = Track length/ 80 (80 SECTIONS PER MILE)

    Steel : How much steel? http://www.railroadpart.com/rail-track-parts/steel-rails.html(approx 50kg/m)
    Total Steel : Track length in m * 50 kg

1 km approx 40 sections  per KM
    25 meters per section = 25 *50 = 1250 kg/section
Support:
    Rail plank
        Sleeper/Plank or Cross Tie: Length in Miles * 3250 (wood)
        Sleeper/Plank or Cross Tie: Length in Miles * 2640 (concerete)

    Fastening
        Tie plate = Planks * 2 (Both sides)
        Rail spikes = Tie plates * 4

Joins (May be insignificant compared to railway steel per meter)
    Fish plate = Sections * 1 * 17 kg steel (http://www.railroadpart.com/rail-joints/fish-plate.html)
    4 bolts - 0.7 kg each (http://www.railroadpart.com/rail-joints/fish-bolts.html)  

Track ballast (Trackebed for sleepers) (https://en.wikipedia.org/wiki/Track_ballast)
    first class line – 60 lb/yd (29.8 kg/m) rail – 1,700 cu yd/mi (810 m3/km).
    second class line – 41.5 lb/yd (20.6 kg/m) rail – 1,135 cu yd/mi (539 m3/km).
    third class line – 30 lb/yd (14.9 kg/m) rail – 600 cu yd/mi (290 m3/km). 

An average wooden railroad tie weighs about 200 pounds
'''
RAILWAY_DATA = {
    PROJECT_TYPE: ProjectType.RAILWAYS.name.lower(),

    REQUIRED_DESCRIPTORS:  [
        (LENGTH, FEET)
    ],

    CALCULATED_DESCRIPTORS: [
        (TONS_STEEL, TONS), (TONS_CONCRETE, TONS), (TONS_BALLAST, TONS), (TONS_TIMBER, TONS)
    ],

    FACTS: {
        LENGTH: 1000,             # feet
        "track ballast" :  20.6,  # kg/m
        "track_weight": 50,       # 50 kg / meter
        "concrete_weight_for_per_crosstie": 600,  # lbs
        "wood_weight_for_crosstie": 250,  # lbs
        "crosstie_per_mile": 2640,
        "ballast_pound_per_yard": 41.5,
        "ft_per_meter": ft_per_meter,
        "ft_per_mile": ft_per_mile,
        "kg_per_pound": kg_per_pound,
        "ft_per_yard": ft_per_yard,
        "pounds_per_ton": cvt.pounds_per_ton
    },

    RULES: [
        f"track_length = {LENGTH} * 2",
        f"kg_per_foot_steel = track_weight / ft_per_meter",
        f"pound_per_foot_steel = kg_per_foot_steel / kg_per_pound",
        f"tons_per_foot_steel = pound_per_foot_steel / pounds_per_ton",
        f"{TONS_STEEL} = tons_per_foot_steel * track_length",
        f"length_in_miles = {LENGTH} / ft_per_mile",
        f"number_of_crosstie = length_in_miles * crosstie_per_mile",
        f"concrete_weight = number_of_crosstie * concrete_weight_for_per_crosstie",
        f"track_length_yard = track_length / ft_per_yard",
        f"ballast_pounds = track_length_yard * ballast_pound_per_yard",
        f"ballast_ton = ballast_pounds / pounds_per_ton",
        f"{TONS_CONCRETE} = concrete_weight / pounds_per_ton",
        f"{TONS_BALLAST} = ballast_ton",
        f"{TONS_TIMBER} = number_of_crosstie * wood_weight_for_crosstie / pounds_per_ton",
    ]
}


class Railway(IProject):
    def __init__(self, logger):
        super().__init__(logger)
        self._init(RAILWAY_DATA)

    @staticmethod
    def from_json(logger, json_dict):
        b = Railway(logger)
        print(b)
        return b._build_from_json(json_dict)

    @staticmethod
    def register(builder):
        builder.add_project_type(RAILWAY_DATA[PROJECT_TYPE], Railway)
