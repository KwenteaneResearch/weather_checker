""" Launch manually the full process """

import numpy as np
import pandas as pd

from pathlib import Path
from colorama import Fore, Style

from weather_checker.params import *
from weather_checker.climatology.geo_to_climate import *


def get_climatology(lat_list:list = [ 5.390770,  5.392571,  5.324686,   5.323670],
                    lon_list:list = [-6.505318, -6.427247, -6.502779,  -6.427451],
                    locations_weights:list = [1/4 for i in range(4)]):
    
    print(f"Running get_climatology() :\n lat_list:{lat_list}\n lon_list:{lon_list}\n locations_weights:{locations_weights}")
    
    # TO DO : Load / Save Climatology dataframe into csv
    
    pre_loaded_data, lat_missing, lon_missing = restore_raw_weather_data(lat_list, lon_list, RAW_WEATHER_STORAGE)
    daily_weather = pd.DataFrame()
    if len(lat_missing) > 0 :
        daily_weather = api_gps_location_to_weather(lat_missing, lon_missing)
    if len(pre_loaded_data)>0:
        daily_weather = pd.concat([daily_weather, pre_loaded_data])
    #print(daily_weather.head())
    #print(f"lat_list:{lat_list}\n lon_list:{lon_list}\n locations_weights:{locations_weights}")
    climatology = climatology_build(daily_weather, lat_list, lon_list, locations_weights)
    
    print("✅ get_climatology() done \n")
    
    return climatology


if __name__ == '__main__':
    climatology = get_climatology()
    print(climatology)
    None