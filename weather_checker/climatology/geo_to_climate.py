"""From geo_data lists, compute the historical climatology for the weighted GPS coordonates"""
import openmeteo_requests
import requests_cache
import numpy as np
import pandas as pd
from retry_requests import retry
import json
import time

from colorama import Fore, Style
from dateutil.parser import parse
from pathlib import Path

import matplotlib.pyplot as plt

from sklearn.cluster import KMeans

from weather_checker.params import *

def restore_raw_weather_data(lat_list:list, lon_list:list, prod_list:list, raw_storage:str='local'):
    if len(lat_list) != len(lon_list):
        print(f"❌ restore_raw_weather_data function doesn't have same lenght for lat_list:{len(lat_list)} and lon_list:{len(lat_list)}")
        return None

    lat_missing = lat_list.copy()
    lon_missing = lon_list.copy()
    prod_missing = prod_list.copy()
    loaded = 0

    pre_loaded_data = pd.DataFrame()

    min_date = parse(METEO_START_DATE).strftime('%Y-%m-%d') # e.g '2009-01-01'
    max_date = parse(METEO_END_DATE).strftime('%Y-%m-%d') # e.g '2009-01-01'

    if raw_storage == "local":
        for i in range(len(lat_list)):
            lat = round(lat_list[i],4)
            lon = round(lon_list[i],4)
            cache_path = Path(RAW_DATA_PATH).joinpath("raw_weather", f"daily_weather_{lat}_{lon}_{min_date}_{max_date}.csv")
            if cache_path.is_file():
                df = pd.read_csv(cache_path)
                df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
                pre_loaded_data = pd.concat([pre_loaded_data,df])
                lat_missing.remove(lat_list[i])
                lon_missing.remove(lon_list[i])
                prod_missing.remove(prod_list[i])
                loaded =+ 1


    elif raw_storage == "big_query":
        print(f"❌ restore_raw_weather_data with big_query is not developed yet, fallback on local")
        return restore_raw_weather_data(lat_list, lon_list, "local")
    else :
        print(f"❌ restore_raw_weather_data RAW_WEATHER_STORAGE is not correct")
        return None

    if len(pre_loaded_data) > 0:
        print(f"✅ restore_raw_weather_data return {loaded} weather data")
    else :
        print(f"❌ Not able to restore any raw weather data")

    return pre_loaded_data, lat_missing, lon_missing, prod_missing, loaded




def api_gps_location_to_weather(lat_list:list, lon_list:list, prod_list:list, raw_storage = 'local'):
    if len(lat_list) != len(lon_list):
        print(f"❌ open_meteo_api function doesn't have same lenght for lat_list:{len(lat_list)} and lon_list:{len(lat_list)}")
        return None

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    url = OPEN_METEO_URL
    api_response = []
    #1 by 1 location api call
    #for i in range(len(lat_list)):
    params = {
        "latitude": lat_list, #lat_list[i]
        "longitude": lon_list, #lon_list[i]
        "start_date": METEO_START_DATE,
        "end_date": METEO_END_DATE,
        "daily": METEO_COLUMNS_DAILY,
        "timezone": "GMT"
    }
    try :
        #api_response.append(openmeteo.weather_api(url, params=params)[0])
        api_response = openmeteo.weather_api(url, params=params)

    except Exception:
        print(f"❌ openmeteo.weather_api return api error")
        if len(api_response) == 0:
            print(f"❌ openmeteo.weather_api didn't return any data")
            return pd.DataFrame()

        #time.sleep(5)

    print(f"✅ api_gps_location_to_weather return api response for {len(api_response)} GPS coordonates")

    actual_weather =pd.DataFrame()
    for i in range(len(api_response)):
        response = api_response[i]
        #print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
        #print(f"Elevation {response.Elevation()} m asl")
        #print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        #print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_mean = daily.Variables(2).ValuesAsNumpy()
        #daily_temperature_2m_max = daily.Variables(3).ValuesAsNumpy()
        #daily_temperature_2m_min = daily.Variables(4).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
        	start = pd.to_datetime(daily.Time(), unit = "s"),
        	end = pd.to_datetime(daily.TimeEnd(), unit = "s"),
        	freq = pd.Timedelta(seconds = daily.Interval()),
        	inclusive = "left"
        )}
        daily_data["weather_code"] = daily_weather_code
        daily_data["precipitation_sum"] = daily_precipitation_sum
        daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
        #daily_data["temperature_2m_max"] = daily_temperature_2m_max
        #daily_data["temperature_2m_min"] = daily_temperature_2m_min

        daily_df = pd.DataFrame(daily_data)

        #Find the closest position from weather api to match the pixel
        lat = lat_list[i]   #min(lat_list, key=lambda x:abs(x-response.Latitude()))
        lon = lon_list[i]   #min(lon_list, key=lambda x:abs(x-response.Longitude()))
        prod = prod_list[i]

        #print(lat, response.Latitude())
        #print(lon, response.Longitude())

        daily_df['lat'] = lat
        daily_df['lon'] = lon
        daily_df['prod'] = prod

        #Save historical daily data in cache
        lat = round(lat,4)
        lon = round(lon,4)
        min_date = parse(METEO_START_DATE).strftime('%Y-%m-%d') # e.g '2009-01-01'
        max_date = parse(METEO_END_DATE).strftime('%Y-%m-%d') # e.g '2009-01-01'
        if raw_storage == "local":
            cache_path = Path(RAW_DATA_PATH).joinpath("raw_weather", f"daily_weather_{lat}_{lon}_{min_date}_{max_date}.csv")
            #cache_path = f"/home/alexandreline/code/KwenteaneResearch/weather_checker/raw_data/daily_weather_{lat}_{lon}_{min_date}_{max_date}.csv"
            if daily_df.shape[0] > 1:
                daily_df.to_csv(cache_path, header=True)

        elif raw_storage == "big_query":
            print(f"❌ gps_location_to_weather storage with big_query is not developed yet, store locally")
            cache_path = Path(RAW_DATA_PATH).joinpath("raw_weather", f"daily_weather_{lat}_{lon}_{min_date}_{max_date}.csv")
            #cache_path = f"/home/alexandreline/code/KwenteaneResearch/weather_checker/raw_data/daily_weather_{lat}_{lon}_{min_date}_{max_date}.csv"
            if daily_df.shape[0] > 1:
                daily_df.to_csv(cache_path, header=True)

        actual_weather = pd.concat([actual_weather,daily_df])

    print(f"✅ gps_location_to_weather return weather history for {len(actual_weather)} GPS coordinates")

    return actual_weather, len(api_response)

#Building a country climatology from all gps locations
def climatology_build(weather_per_location, lat_list, lon_list, prod):
    if len(lat_list) != len(lon_list) or len(lon_list) != len(prod):
        print(f"❌ climatology_build function doesn't have same lenght for lat_list:{len(lat_list)}, lon_list:{len(lat_list)} and weights:{len(prod)}")
        return None


    country_weather = pd.DataFrame()
    for locations in range(len(lat_list)):
        lat_mask = weather_per_location['lat']==lat_list[locations]
        lon_mask = weather_per_location['lon']==lon_list[locations]
        weather_point = weather_per_location[lat_mask & lon_mask].copy()

        #############
        #TO DO Add a condition if weather_point is empty to BREAK
        ############

        #adding year column and month_number column
        weather_point['year'] = weather_point['date'].dt.year

        #creating rain_season rainfall, dry_season rainfall and total rainfall per year
        weather_grouped = weather_point.groupby(['year', weather_point['date'].dt.month.isin([5, 6, 7, 8, 9])])['precipitation_sum'].sum().unstack(fill_value=0)
        weather_grouped.columns = ['dry_season', 'rain_season']
        weather_grouped["total_year_rain"] = weather_grouped["dry_season"] + weather_grouped["rain_season"]

        # counting the number of rain days for each year
        yearly_rain_day = weather_point.groupby(weather_point["date"].dt.to_period('Y')).agg({'precipitation_sum': lambda x: (x > 1.0).sum()})
        yearly_rain_day = yearly_rain_day.rename(columns={"precipitation_sum":"rain_days"})
        yearly_rain_day.index = yearly_rain_day.index.year.astype("int")
        #counting the days with intense rain (ie weather code = 64 or 65
        intense_rain_day = weather_point.groupby(weather_point["date"].dt.to_period('Y')).agg({"weather_code": lambda x: (x.isin([64, 65])).sum()})
        intense_rain_day.index = intense_rain_day.index.year.astype("int")
        intense_rain_day = intense_rain_day.rename(columns={"weather_code":"intense_rain_days"})

        #creating the final dataframe for the location
        weather_total = pd.concat([weather_grouped, yearly_rain_day,intense_rain_day], axis=1)
        weather_total["dry_season_weighted"] = weather_total["dry_season"] * prod[locations]/sum(prod)  #weather_total["location_weight"]
        weather_total["rain_season_weighted"] = weather_total["rain_season"] * prod[locations]/sum(prod)   #weather_total["location_weight"]
        weather_total["total_rain_year_weighted"] = weather_total["total_year_rain"] * prod[locations]/sum(prod)   #weather_total["location_weight"]
        weather_total["intense_rain_days_weighted"] = weather_total["intense_rain_days"] * prod[locations]/sum(prod)   #weather_total["location_weight"]
        #possible to weight the number of rain days

        #concatenating into the country dataframe with details per GPS point
        country_weather = pd.concat([country_weather,weather_total])

        #building a summary dataframe for climatology per year
        country_weather_dry_season = country_weather.groupby(country_weather.index)['dry_season_weighted'].sum()
        country_weather_rain_season = country_weather.groupby(country_weather.index)['rain_season_weighted'].sum()
        country_weather_rain = country_weather.groupby(country_weather.index)['total_rain_year_weighted'].sum()
        country_weather_rain_days = country_weather.groupby(country_weather.index)['rain_days'].mean()
        country_weather_intense_rain = country_weather.groupby(country_weather.index)['intense_rain_days_weighted'].mean()
        country_climatology = pd.concat([country_weather_dry_season, country_weather_rain_season,country_weather_rain,country_weather_rain_days,country_weather_intense_rain], axis=1)

    return country_climatology

def save_load_climatology(save:bool=True, country:str='CIV', sample_weight:float=0.05, climat=pd.DataFrame()):
    min_date = parse(METEO_START_DATE).strftime('%Y-%m-%d') # e.g '2009-01-01'
    max_date = parse(METEO_END_DATE).strftime('%Y-%m-%d') # e.g '2009-01-01'
    cache_path = Path(RAW_DATA_PATH).joinpath("climatologies", f"climatology_{country}_{sample_weight}_{min_date}_{max_date}.csv")
    if save :
        if climat.shape[0] > 1:
            climat.to_csv(cache_path, header=True)
            print(f"✅ climatology of weight {sample_weight} from {min_date} to {max_date} saved")
    else :
        if cache_path.is_file():
            climat = pd.read_csv(cache_path,index_col=[0])
            print(f"✅ climatology of weight {sample_weight} from {min_date} to {max_date} loaded")
            return climat
    return pd.DataFrame()
