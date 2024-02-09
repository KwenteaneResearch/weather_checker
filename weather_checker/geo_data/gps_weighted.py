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
