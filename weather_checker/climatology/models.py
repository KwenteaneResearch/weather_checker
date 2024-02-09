import pandas as pd
import numpy as np


import matplotlib.pyplot as plt
#import plotly.express as px
#import plotly.graph_objects as go

from sklearn.cluster import KMeans
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import MinMaxScaler

#from tslearn.utils import to_time_series_dataset
#from tslearn.clustering import TimeSeriesKMeans
#from tslearn.preprocessing import TimeSeriesScalerMeanVariance



def group_index_to_list(group):
    """ Translating the family groups back into lists of years"""
    return list(group.index)


def k_means(cocoa_climatology):
    km = KMeans(n_clusters=5)
    km.fit(cocoa_climatology)
    
    cocoa_similar_years = cocoa_climatology.copy()
    cocoa_similar_years["year_group"] = km.labels_
    grouped_index_lists = cocoa_similar_years.groupby('year_group').apply(group_index_to_list, include_groups = False)

    for i in range(len(grouped_index_lists)):
        print(f"{i} {grouped_index_lists[i]}")
        
    #building a dictionary showing a weather characteristic for each family
    rain_season_cumul = {}
    for i in range(len(grouped_index_lists)):
        crop_years = grouped_index_lists[i]
        rain_season_type = cocoa_similar_years[cocoa_climatology.index.isin(crop_years)]
        rain_season_cumul[i] = rain_season_type["rain_season_weighted"].mean()
    rain_season_cumul
        
    return rain_season_cumul, grouped_index_lists

def outliers(cocoa_climatology):
    #detecting outliers from the weather dataset
    sk_outlier = LocalOutlierFactor()
    outliers = sk_outlier.fit_predict(cocoa_climatology)
    
    #extracting the list of outliers as years
    cocoa_years = cocoa_climatology.index.tolist()
    cocoa_years_outliers = []
    for item1, item2 in zip(outliers, cocoa_years):
        if item1 == -1:
            cocoa_years_outliers.append(item2)
    #cocoa_years_outliers
    
    #creating a new dataframe only showing the outlier years weather features
    climatology_outliers = cocoa_climatology.loc[cocoa_years_outliers]

    #scaling the features for better display in a chart
    scaler = MinMaxScaler(feature_range=(0, 5))
    climatology_outliers_scaled = pd.DataFrame(scaler.fit_transform(climatology_outliers))
    
    #putting back the index as the outlier years
    climatology_outliers_scaled = climatology_outliers_scaled.set_index(keys = [cocoa_years_outliers])
    #climatology_outliers_scaled

    return climatology_outliers_scaled, cocoa_years_outliers
