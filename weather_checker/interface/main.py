""" Launch manually the full process """

import numpy as np
import pandas as pd

from pathlib import Path
from colorama import Fore, Style

from weather_checker.params import *
from weather_checker.geo_data.gps_weighted import *
from weather_checker.climatology.geo_to_climate import *


def get_climatology(lat_list:list = [],
                    lon_list:list = [],
                    locations_weights:list = [],
                    total_weight:float = 0.0007137254902): #0.0007137254902 top10 / 0.1 top50
    
    if len(lat_list) == 0 or len(lon_list) == 0 or len(locations_weights)==0:
        lat_list, lon_list, locations_weights = load_gps_weighted(total_weight) 
        #lat_list = [ 5.390770,  5.392571,  5.324686,   5.323670]
        #lon_list =  [-6.505318, -6.427247, -6.502779,  -6.427451]
        #locations_weights = [1/4 for i in range(4)]
        
    
    print(Fore.BLUE + f"Running get_climatology()..." + Style.RESET_ALL)
    print(f"lat_list:{lat_list}\n lon_list:{lon_list}\n locations_weights:{locations_weights}")
    
    climatology = save_load_climatology(save=False, total_weight=np.round(np.sum(locations_weights),8))
    
    if climatology.shape[0] == 0:
        pre_loaded_data, lat_missing, lon_missing = restore_raw_weather_data(lat_list, lon_list, RAW_WEATHER_STORAGE)
        daily_weather = pd.DataFrame()
        if len(lat_missing) > 0 :
            daily_weather = api_gps_location_to_weather(lat_missing, lon_missing)
        if len(pre_loaded_data)>0:
            daily_weather = pd.concat([daily_weather, pre_loaded_data])
        #print(daily_weather.head())
        #print(f"lat_list:{lat_list}\n lon_list:{lon_list}\n locations_weights:{locations_weights}")
        climatology = climatology_build(daily_weather, lat_list, lon_list, locations_weights)
        
        save_load_climatology(save=True, total_weight=np.round(np.sum(locations_weights),8), climat=climatology)
    
    print("✅ get_climatology() done \n")
    
    return climatology


if __name__ == '__main__':
    climatology = get_climatology()
    print(climatology)