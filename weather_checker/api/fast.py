import pandas as pd
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from weather_checker.interface.main import *
from weather_checker.nlp.report_summary import *
from weather_checker.params import *


"""
from pydantic import BaseModel


class Item(BaseModel):
    pickup_datetime: list        #= '2013-07-06 17:18:00'
    pickup_longitude: list    #= -73.950655
    pickup_latitude: list     #= 40.783282
    dropoff_longitude: list   #= -73.984365
    dropoff_latitude: list    #= 40.769802
    passenger_count: list       #= 1
"""

app = FastAPI()
#app.state.model = load_model()


# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/collect_locations")
def locations(country_code:str='CIV', sample_weight:float=0.1):
    """
    getting the list of selected locations as gps coordinates to display on the map of the UI
    """
    lat_list, lon_list, prod_list = load_gps(country_code, sample_weight)
    return {"latitude":lat_list,"longitude":lon_list}

@app.get("/compute_climatology")
def climatology(country_code:str='CIV', sample_weight:float=0.1):
    """
    Compute the climatology for a country and a sample_weight.
    """
    # Fallbacks
    errors = {}
    if country_code not in COUNTRY_MAX_PERCENT:
        errors["Incorrect input country_code"] = f"{country_code} not in list {COUNTRY_MAX_PERCENT.keys()}"
    else :
        if sample_weight > COUNTRY_MAX_PERCENT[country_code] :
            climat, returned_weight = get_climatology(country_code,COUNTRY_MAX_PERCENT[country_code])
            return {"Incorrect input sample_weight":f"{sample_weight} should not be above {COUNTRY_MAX_PERCENT[country_code]*100}% for {country_code}",
                    "climatology": f"climatology done for {country_code} on {np.round(returned_weight,6)*100}% of the cocoa production from {min(climat.index)} to {max(climat.index)}"}

    if len(errors) > 0:
        return errors
    else :
        climat, returned_weight = get_climatology(country_code,sample_weight)
        return {"climatology": f"climatology done for {country_code} on {np.round(returned_weight,6)*100}% of the cocoa production from {min(climat.index)} to {max(climat.index)}"}

@app.get("/years_classification")
def regroup_years(country_code:str='CIV',sample_weight:float=0.1):
    """
    running the classification of years and identifying outliers
    """
    # Fallbacks
    errors = {}
    if country_code not in COUNTRY_MAX_PERCENT:
        errors["Incorrect input country_code"] = f"{country_code} not in list {COUNTRY_MAX_PERCENT.keys()}"
    else :
        if sample_weight > COUNTRY_MAX_PERCENT[country_code] :
            year_groups, weather_metric = analog_years(country_code,COUNTRY_MAX_PERCENT[country_code])
            cocoa_years_outliers = outliers(country_code,COUNTRY_MAX_PERCENT[country_code])
            return {"Incorrect input sample_weight":f"{sample_weight} should not be above {COUNTRY_MAX_PERCENT[country_code]*100}% for {country_code}",
                    "families_of_years":year_groups,"family_rain_season_rainfall":weather_metric,"outlier_years":cocoa_years_outliers}
    
    if len(errors) > 0:
        return errors
    else :
        year_groups, weather_metric = analog_years(country_code,sample_weight)
        cocoa_years_outliers = outliers(country_code,sample_weight)
        return {"families_of_years":year_groups,"family_rain_season_rainfall":weather_metric,"outlier_years":cocoa_years_outliers}


@app.get("/get_monthly_summary")
def get_reports(openai_api_key:str, year:int=2016, month:str="02"):
    """
    collecting the reports for a given year and month and storing the extracted text part in a .csv file
    summarising the reports with map_reduce technique using OpenAPI
    """
    # Fallbacks
    errors = {}
    if year != 2016 :
        errors["Incorrect input year"] = f"{year} not 2016"
    month_list = ["01","02","03","04","05","06","07","08","09","10","11","12"]
    if month not in month_list:
        errors["Incorrect input month"] = f"{month} not in list {month_list}"
    
    if len(errors) > 0:
        return errors
    else :
        get_monthly_reports(year,month)
        summary = get_monthly_summary(openai_api_key,year,month)
        return {"month":f"reports collected for{year}-{month}","monthly_summary": summary}

@app.get("/")
def root():
    return {'Hello': 'world !'}
