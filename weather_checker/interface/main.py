""" Launch manually the full process """

import numpy as np
import pandas as pd


from colorama import Fore, Style

from weather_checker.params import *
from weather_checker.geo_data.gps_weighted import *
from weather_checker.climatology.geo_to_climate import *
from weather_checker.climatology.models import *


def get_climatology(country_code:str='CIV', sample_weight:float=0.05): 

    reduced = False
    retrieved_locations = 0
    loaded = 0
    
    print(Fore.BLUE + f"Running get_climatology()..." + Style.RESET_ALL)
    #print(f"lat_list:{lat_list}\n lon_list:{lon_list}\n locations_weights:{locations_weights}")
    lat_list, lon_list, prod_list = load_gps(country_code, np.round(sample_weight,8))
    
    
    climatology = save_load_climatology(save=False, country=country_code, sample_weight=np.round(sample_weight,8))


    if climatology.shape[0] == 0:
        pre_loaded_data, lat_missing, lon_missing, prod_missing, loaded = restore_raw_weather_data(lat_list, lon_list, prod_list, RAW_WEATHER_STORAGE)
        daily_weather = pd.DataFrame()
        if len(lat_missing) > 0 &  len(lat_missing) <= 12:
            daily_weather, retrieved_locations = api_gps_location_to_weather(lat_missing, lon_missing, prod_missing)
        if len(lat_missing) > 12:
            actual_percent = np.sum(pre_loaded_data["prod"])/ COUNTRY_PRODUCTION[country_code]
            print(f"❌ Limited Open Weather API ressources, we will compute the climatology on a reduced dataset")
            reduced=True
        if loaded>0:
            daily_weather = pd.concat([daily_weather, pre_loaded_data])
        #print(daily_weather.head())
        #print(f"lat_list:{lat_list}\n lon_list:{lon_list}\n locations_weights:{locations_weights}")
        if daily_weather.shape[0] == 0 or retrieved_locations + loaded == 0:
            print(f"❌ No weather data computed - QUIT")
            return None
        else :
            climatology = climatology_build(daily_weather, lat_list, lon_list, prod_list)

        if reduced :
            save_load_climatology(save=True, country=country_code, sample_weight=np.round(actual_percent,8), climat=climatology)
        else :
            save_load_climatology(save=True, country=country_code, sample_weight=np.round(sample_weight,8), climat=climatology)

    print("✅ get_climatology() done")

    """
    rain_season_cumul, grouped_index_lists = k_means(climatology)
    print(rain_season_cumul)
    print(grouped_index_lists)

    climatology_outliers_scaled, cocoa_years_outliers = outliers(climatology)
    print(climatology_outliers_scaled)
    print(cocoa_years_outliers)
    """

    return climatology, np.round(sample_weight,8) if not reduced else np.round(actual_percent,8)



if __name__ == '__main__':
    climatology = get_climatology('CIV',0.05)
