from weather_checker.params import *
import numpy as np
import pandas as pd
from pathlib import Path


def load_gps_weighted(total_weight:float=0):
    if total_weight == 0.0007137254902 or total_weight == 0.1:
        cache_path = Path(RAW_DATA_PATH).joinpath("gps_locations", "top50-gps.csv" if total_weight == 0.1 else "top10-gps.csv")
    else :
        cache_path = Path(RAW_DATA_PATH).joinpath("gps_locations", f"gps_weight_{COUNTRY}_{np.round(total_weight,8)}.csv")

    if not cache_path.is_file():
        print(f"❌ GPS Locations of total weight {np.round(total_weight,8)} not found in {cache_path}")
        return None
    else :
        climat = pd.read_csv(cache_path)
        lat_list = climat.latitude.tolist()
        lon_list = climat.longitude.tolist()
        locations_weights = climat.weight.tolist()

        print(f"✅ GPS Locations of total weight {np.round(total_weight,8)} loaded")
        return lat_list, lon_list, locations_weights

def filter_locations_by_country_weight(country:str, top_percentage:float):
    """
    Filtering 'top_percentage' production locations for iso-code 'country'
    """
    path = os.path.join(os.path.dirname(os.path.realpath('__file__')), 'input_csv/coco_all.csv')
    if (not Path(path).is_file()):
        print(f"❌ Production file fot found in {path}")
        return None
    df = pd.read_csv(path)
    print(f"✅ {path} loaded in pandas")
    df_country = df[df.ISO == country].copy()
    df_country['percentage'] = df_country.Production / df_country.Production.sum()
    df_country = df_country.sort_values(by = "percentage", ascending=False)
    df_country.percentage = df_country.percentage.cumsum()

    df_filter = df_country[df_country.percentage <= top_percentage].copy()
    df_filter.drop(['ID', 'NAME_0', 'X_lon_3857', 'Y_lat_3857', 'percentage'], axis=1, inplace=True)
    df_filter = df_filter.rename(columns={"Production": "prod", "ISO": "country", "X_lon_4326": "longitude", "Y_lat_4326": "latitude"},)
    print(f"✅ dataframe filtered")
    path = os.path.join(RAW_DATA_PATH,  f'gps_locations/gps_weight_{country}_{np.round(top_percentage,8)}.csv')
    df_filter.to_csv(path, index=False)
    print(f"✅ filtered dataframe exported into {path}")
