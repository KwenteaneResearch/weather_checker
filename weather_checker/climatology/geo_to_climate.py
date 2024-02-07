"""From geo_data lists, compute the historical climatology for the weighted GPS coordonates"""
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import json

from colorama import Fore, Style
from dateutil.parser import parse
from pathlib import Path

import matplotlib.pyplot as plt

from sklearn.cluster import KMeans

from weather_checker.params import *

def restore_raw_weather_data(lat_list:list, lon_list:list, locations_weights:list, raw_storage:str='local'):
    if len(lat_list) != len(lon_list):
        print(f"❌ restore_raw_weather_data function doesn't have same lenght for lat_list:{len(lat_list)} and lon_list:{len(lat_list)}")
        return None
    
    lat_missing = lat_list.copy()
    lon_missing = lon_list.copy()
    weight_missing = locations_weights.copy()
    lat_preloaded = []
    lon_preloaded = []
    weight_preloaded = []
    pre_loaded_data = []
    
    min_date = parse(METEO_START_DATE).strftime('%Y-%m-%d') # e.g '2009-01-01'
    max_date = parse(METEO_END_DATE).strftime('%Y-%m-%d') # e.g '2009-01-01'

    if raw_storage == "local":
        for i in range(len(lat_list)):
            lat = round(lat_list[i],4)
            lon = round(lon_list[i],4)
            cache_path = Path(RAW_METEO_PATH).joinpath("raw_weather", f"daily_weather_{lat}_{lon}_{min_date}_{max_date}.json")
            if cache_path.is_file():
                pre_loaded_data.append(pd.read_json(cache_path))
                lat_preloaded.append(lat)
                lon_preloaded.append(lat)
                weight_preloaded.append(weight_missing[i])
                lat_missing.remove(lat)
                lat_missing.remove(lon)
                weight_missing.remove(weight_missing[i])
    
            
    elif raw_storage == "big_query":
        print(f"❌ restore_raw_weather_data with big_query is not developed yet, fallback on local")
        return restore_raw_weather_data(lat_list, lon_list, locations_weights, "local")
    else :
        print(f"❌ restore_raw_weather_data RAW_WEATHER_STORAGE is not correct")
        return None
    
    if len(pre_loaded_data) > 0:
        print(f"✅ restore_raw_weather_data return {len(pre_loaded_data)} weather data")
        weight_reordered = weight_missing.append(weight_preloaded)
    else :
        print(f"Not able to restore any raw weather data")
        weight_reordered = weight_missing
        
    return pre_loaded_data, lat_missing, lon_missing, weight_reordered

def open_meteo_api(lat_list:list, lon_list:list):
    if len(lat_list) != len(lon_list):
        print(f"❌ open_meteo_api function doesn't have same lenght for lat_list:{len(lat_list)} and lon_list:{len(lat_list)}")
        return None
    
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    url = OPEN_METEO_URL
    params = {
        "latitude": lat_list,
        "longitude": lon_list,
        "start_date": METEO_START_DATE,
        "end_date": METEO_END_DATE,
        "daily": METEO_COLUMNS_DAILY,
        "timezone": "GMT"
    }
    response = openmeteo.weather_api(url, params=params)
    print(f"✅ open_meteo_api return api response for {len(response)} GPS coordonates")
    
    return response

# Processing locations into a list
def gps_location_to_weather(api_response, raw_storage = 'local'):
    actual_weather =[]
    for i in range(len(api_response)):
        response = api_response[i]
        #print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
        #print(f"Elevation {response.Elevation()} m asl")
        #print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        #print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
    
        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
        daily_temperature_2m_mean = daily.Variables(3).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(4).ValuesAsNumpy()
        daily_rain_sum = daily.Variables(5).ValuesAsNumpy()
        
        daily_data = {"date": pd.date_range(
        	start = pd.to_datetime(daily.Time(), unit = "s"),
        	end = pd.to_datetime(daily.TimeEnd(), unit = "s"),
        	freq = pd.Timedelta(seconds = daily.Interval()),
        	inclusive = "left"
        )}
        daily_data["weather_code"] = daily_weather_code
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
        daily_data["precipitation_sum"] = daily_precipitation_sum
        daily_data["rain_sum"] = daily_rain_sum
    
        actual_weather.append(daily_data)
        
        #Save historical daily data in cache
        lat = round(response.Latitude(),4)
        lon = round(response.Longitude(),4)
        min_date = parse(METEO_START_DATE).strftime('%Y-%m-%d') # e.g '2009-01-01'
        max_date = parse(METEO_END_DATE).strftime('%Y-%m-%d') # e.g '2009-01-01'
        if raw_storage == "local":
            cache_path = Path(RAW_METEO_PATH).joinpath("raw_weather", f"daily_weather_{lat}_{lon}_{min_date}_{max_date}.json")
            # Convertir et écrire l'objet JSON dans un fichier
            with open(cache_path, "w") as outfile:
                json.dump(daily_data, outfile)
        elif raw_storage == "big_query":
            print(f"❌ gps_location_to_weather storage with big_query is not developed yet, store locally")
            cache_path = Path(RAW_METEO_PATH).joinpath("raw_weather", f"daily_weather_{lat}_{lon}_{min_date}_{max_date}.json")
            daily_data.to_json(cache_path)
            
            
    print(f"✅ gps_location_to_weather return weather history for {len(actual_weather)} GPS coordonates")
    
    return actual_weather

#Building a country climatology from all gps locations
def climatology_build(weather_per_location, weights):

    country_weather = pd.DataFrame()
    for locations in range(len(weather_per_location)):
        weather_point = pd.DataFrame(weather_per_location[locations])
        
        #adding year column and month_number column
        weather_point['month_number'] = weather_point['date'].dt.month
        weather_point['year'] = weather_point['date'].dt.year
        
        #creating rain_season rainfall, dry_season rainfall and total rainfall per year
        weather_grouped = weather_point.groupby(['year', weather_point['month_number'].isin([5, 6, 7, 8, 9])])['precipitation_sum'].sum().unstack(fill_value=0)
        weather_grouped.columns = weather_grouped.columns = ['dry_season', 'rain_season']
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
        weather_total["latitude"] = locations.Latitude()            #Not optimized
        weather_total["longitude"] = locations.Longitude()          #Not optimized
        weather_total["location_weight"] = weights[locations]       #Not optimized
        weather_total["dry_season_weighted"] = weather_total["dry_season"] * weather_total["location_weight"]
        weather_total["rain_season_weighted"] = weather_total["rain_season"] * weather_total["location_weight"]
        weather_total["total_rain_year_weighted"] = weather_total["total_year_rain"] * weather_total["location_weight"]
        weather_total["intense_rain_days_weighted"] = weather_total["intense_rain_days"] * weather_total["location_weight"]
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