import numpy as np
from EnvironmentalImpact.UnitConversions import kg_per_pound, pounds_per_ton, ton_per_tonne

#
# Conversion of materials into Emissions
#

# https://sustainableinfrastructure.org/

def _get_average_co2_for_concrete():
    tons_co2_per_ton_concrete_ = []

    # Concrete = Cement + stone + sand + water
    # Tons of CO2 from Tons of concrete
    # 9.8 million tons of CO2 generated
    # from the production of “76 million tons of finished concrete in the US.”
    # 9.8 / 76 = 0.13 (Includes the emissions during production of concrete AND energy)
    tons_co2_per_ton_concrete_.append(0.13)

    # https://www.bbc.com/news/science-environment-46455844 (2016,
    # In 2016, world cement production generated around 2.2 billion tonnes of CO2
    tons_co2_per_ton_concrete_.append(2200.0 / 4200.0)

    # https://www3.epa.gov/ttnchie1/conference/ei13/ghg/hanle.pdf (pg 9)
    # tons_co2_per_ton_concrete_.append(0.97)

    # https://www.sustainableconcrete.org.uk/Sustainable-Concrete/Performance-Indicators/CO2-Emissions-Production.aspx
    # 72.2 kg CO2/tonne of concrete (= 0.0722 kg/kg)
    tons_co2_per_ton_concrete_.append((72.2 / kg_per_pound / pounds_per_ton) / ton_per_tonne)

    avg_tons_co2_per_ton_concrete = np.average(tons_co2_per_ton_concrete_)
    return avg_tons_co2_per_ton_concrete


#
# Conversions of materials into Emissions
#
tons_co2_per_ton_concrete = _get_average_co2_for_concrete()
# https://www.eia.gov/environment/emissions/co2_vol_mass.php
# 22.4 Pounds of CO2 from a gallon of diesel
tons_co2_per_gallon_diesel = 22.4 / pounds_per_ton

concrete_pounds_per_cubic_foot = 150.0
concrete_pounds_per_cubic_yard = 4_050  # should be 150 * 27
