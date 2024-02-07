""" Launch manually the full process """

import numpy as np
import pandas as pd

from pathlib import Path
from colorama import Fore, Style

from weather_checker.params import *
from weather_checker.climatology.geo_to_climate import *


def get_climatology(lat_list:list = [5.390770,5.392571,5.324686,5.323670],
                    lon_list:list = [-6.505318,-6.427247, -6.502779,-6.427451],
                    locations_weights:list = [1/4 for i in range(4)]):
    
    print(f"Running get_climatology() :\n lat_list:{lat_list}\n lon_list:{lon_list}\n locations_weights:{locations_weights}")
    
    # TO DO : Load / Save Climatology dataframe into csv
    
    pre_loaded_data, lat_missing, lon_missing, weight_reordered = restore_raw_weather_data(lat_list, lon_list, locations_weights, RAW_WEATHER_STORAGE)
    response = open_meteo_api(lat_missing, lon_missing)
    daily_weather = gps_location_to_weather(response)
    if len(pre_loaded_data)>0:
        daily_weather.append(pre_loaded_data)
    climatology = climatology_build(daily_weather, weight_reordered)
    
    print("✅ get_climatology() done \n")
    
    return climatology


if __name__ == '__main__':
    get_climatology()
    #preprocess(min_date='2009-01-01', max_date='2015-01-01')
    #train(min_date='2009-01-01', max_date='2015-01-01')
    #evaluate(min_date='2009-01-01', max_date='2015-01-01')
    #pred()
    None