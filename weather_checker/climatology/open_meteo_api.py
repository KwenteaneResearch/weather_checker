import numpy as np
import pandas as pd

import os
from dateutil.parser import parse
from pathlib import Path

from weather_checker.climatology.geo_to_climate import *
from weather_checker.params import *


def compute_csv_files():
    files = {"next_files_to_process":[]}
    all_gps = Path(RAW_DATA_PATH).joinpath("gps_locations", f"coco_all_group_of_10.csv")
    if all_gps.is_file():
        gps_df = pd.read_csv(all_gps)
    #print(gps_df.info())
    dict_group_10 = {"CIV":241,"GHA":107,"NGA":96,"CMR":111,"REST":655}

    for k, v in dict_group_10.items():
        gps_country = gps_df[gps_df['country'] == k]
        #print(gps_country.info())

        for i in range(1,v+1):
            gps_10_list = gps_country[gps_country['group'] == i]
            gps_path = Path(RAW_DATA_PATH).joinpath("gps_locations", "to_be_processed", f"gps_10_locations_{k}_{i}.csv")
            if gps_10_list.shape[0] > 1:
                gps_10_list[['latitude','longitude','prod']].to_csv(gps_path, header=True, index=False)
                files['next_files_to_process'].append(f"gps_10_locations_{k}_{i}.csv")

    df_files = pd.DataFrame(files)
    files_to_process = Path(RAW_DATA_PATH).joinpath("gps_locations", "doing", "files_to_process.csv")
    if df_files.shape[0] > 1:
        df_files.to_csv(files_to_process, header=True, index=False)
    return None


def get_next_file(to_move:bool=False):
    files_to_process = Path(RAW_DATA_PATH).joinpath("gps_locations", "doing", "files_to_process.csv")
    if files_to_process.is_file():
        df_files = pd.read_csv(files_to_process)
        for i in range(df_files.next_files_to_process.shape[0]):
            file_name = df_files.next_files_to_process.iloc[i]
            file_path = Path(RAW_DATA_PATH).joinpath("gps_locations","to_be_processed", file_name)
            if file_path.is_file():
                print(file_name)
                return file_name
            # test is file is in "doing"
            file_path = Path(RAW_DATA_PATH).joinpath("gps_locations","doing", file_name)
            if file_path.is_file():
                print(file_name)
                return file_name





def get_data_locations(file_name):
    file_path = Path(RAW_DATA_PATH).joinpath("gps_locations","to_be_processed", file_name)
    df_files = pd.DataFrame()
    if file_path.is_file():
        df_files = pd.read_csv(file_path)
        #print(df_files.info())
        if df_files.shape[0] > 1:
            os.rename(file_path,
                Path(RAW_DATA_PATH).joinpath("gps_locations","doing", file_name))
    else:
        file_path = Path(RAW_DATA_PATH).joinpath("gps_locations","doing", file_name)
        if file_path.is_file():
            df_files = pd.read_csv(file_path)
    return df_files

def file_done(file_name):
    files_to_process = Path(RAW_DATA_PATH).joinpath("gps_locations", "doing", file_name)
    df_files = pd.read_csv(files_to_process)

    os.rename(Path(RAW_DATA_PATH).joinpath("gps_locations","doing", file_name)  ,
            Path(RAW_DATA_PATH).joinpath("gps_locations","done", file_name))

    return df_files


def get_daily_data():
    filename = get_next_file()
    df = get_data_locations(filename)
    lat_list = df["latitude"].tolist()
    lon_list = df["longitude"].tolist()
    prod_list = df["prod"].tolist()

    pre_loaded_data, lat_missing, lon_missing, prod_missing, pre_loaded_location = restore_raw_weather_data(lat_list, lon_list, prod_list, RAW_WEATHER_STORAGE)
    daily_weather = pd.DataFrame()
    if len(lat_missing) > 0 :
        print(f"API call for latidudes : {lat_missing} \nlongitudes : {lon_missing}")
        daily_weather,retrieved_locations = api_gps_location_to_weather(lat_missing, lon_missing, prod_missing)
    print(daily_weather.shape[0])
    print(pre_loaded_data.shape[0])

    if retrieved_locations + pre_loaded_location == 10:
        file_done(filename)

    return None



if __name__ == '__main__':
    #compute_csv_files()
    get_daily_data()
