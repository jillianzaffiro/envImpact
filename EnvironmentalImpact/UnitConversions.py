#
# Basic unit conversions
#

# Units
FEET = "feet"
SQR_FEET = "square_feet"
TONS = "tons"
GALLONS = "gallons"
MEGAWATTS = "megawatts"


# Length
ft_per_yard = 3.0
ft_per_meter = 3.281
ft_per_mile = 5280.0
meter_per_kilometer = 1000.0

# Area
sq_meter_per_sq_foot = 1 / (ft_per_meter * ft_per_meter)

# Volume/Weight
ton_per_KG = 1 / 907.185
pounds_per_ton = 2000.0
kg_per_pound = 0.453592
kg_per_tonne = 1000

pounds_per_tonne = kg_per_tonne / kg_per_pound
ton_per_tonne = pounds_per_tonne / pounds_per_ton


def convert_units(value, in_units, out_units):
    if in_units is None:
        return False, 0

    if in_units == out_units:
        return True, value

    if out_units == 'feet':
        return _convert_to_feet(value, in_units)

    if out_units == 'mw':
        return _convert_to_megawatt(value, in_units)


def _convert_to_megawatt(value, in_units):
    if in_units == 'mw':
        return True, value
    if in_units == 'kw':
        return True, value / 1000.0
    else:
        return False, 0.0


def _convert_to_feet(value, in_units):
    if in_units == 'feet':
        return True, value
    if in_units == 'meters':
        return True, value * ft_per_meter
    elif in_units == 'mile':
        return True, value * ft_per_mile
    elif in_units == 'km':
        return True, value * meter_per_kilometer * ft_per_meter
    else:
        return False, 0.0
