import pandas as pd
import numpy as np


import matplotlib.pyplot as plt
#import plotly.express as px
#import plotly.graph_objects as go

from sklearn.cluster import KMeans
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import MinMaxScaler

from weather_checker.climatology.geo_to_climate import *


def analog_years (country_code:str='CIV',sample_weight:float=0.1):

    min_date = parse(METEO_START_DATE).strftime('%Y-%m-%d') # e.g '2009-01-01'
    max_date = parse(METEO_END_DATE).strftime('%Y-%m-%d')
    cache_path = Path(RAW_DATA_PATH).joinpath("climatologies", f"climatology_{country_code}_{sample_weight}_{min_date}_{max_date}.csv")

    if cache_path.is_file()==False:
        print(f"❌ climatology of weight {sample_weight} from {min_date} to {max_date} not found, please create climatology first")
        return None
    else:
        climatology = save_load_climatology(save=False, country=country_code, sample_weight=np.round(sample_weight,8))

    #calling & fitting the classification model
    km = KMeans(n_clusters=5)
    km.fit(climatology)
    #translating the family groups back into a dictionary with families as keys and years as lists
    cocoa_similar_years = climatology.copy()
    cocoa_similar_years["year_group"] = km.labels_
    year_family = cocoa_similar_years.groupby('year_group')
    year_family = year_family.groups
    print(year_family)

    #associating a weather metric to each family
    weather_classification_dict = {}
    for i in range(len(year_family)):
        crop_years = list(year_family.keys())[i]
        rain_season_type = cocoa_similar_years[cocoa_similar_years.index.isin(year_family[crop_years])]
        weather_classification_dict[i] = rain_season_type["rain_season_weighted"].mean()

    print(weather_classification_dict)

    #returning the two dictionaries
    return year_family, weather_classification_dict



def outliers(country_code:str='CIV',sample_weight:float=0.1):

    min_date = parse(METEO_START_DATE).strftime('%Y-%m-%d') # e.g '2009-01-01'
    max_date = parse(METEO_END_DATE).strftime('%Y-%m-%d')
    cache_path = Path(RAW_DATA_PATH).joinpath("climatologies", f"climatology_{country_code}_{sample_weight}_{min_date}_{max_date}.csv")

    if cache_path.is_file()==False:
        print(f"❌ climatology of weight {sample_weight} from {min_date} to {max_date} not found, please create climatology first")
        return None
    else:
        climatology = save_load_climatology(save=False, country=country_code, sample_weight=np.round(sample_weight,8))

    #detecting outliers from the weather dataset
    sk_outlier = LocalOutlierFactor()
    outliers = sk_outlier.fit_predict(climatology)

    #extracting the list of outliers as years
    cocoa_years = climatology.index.tolist()
    cocoa_years_outliers = []
    for item1, item2 in zip(outliers, cocoa_years):
        if item1 == -1:
            cocoa_years_outliers.append(item2)

    #creating a new dataframe only showing the outlier years weather features
    climatology_outliers = climatology.loc[cocoa_years_outliers]

    print(cocoa_years_outliers)
    return cocoa_years_outliers
