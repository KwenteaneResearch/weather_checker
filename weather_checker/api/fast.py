import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from weather_checker.interface.main import *

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



# http://127.0.0.1:8000/predict?pickup_datetime=2012-10-06 12:10:20&pickup_longitude=40.7614327&pickup_latitude=-73.9798156&dropoff_longitude=40.6513111&dropoff_latitude=-73.8803331&passenger_count=2
@app.get("/compute_climatology")
def climatology(country_code:str='CIV', sample_weight:float=0.05):      
    """
    Compute the climatology for a country and a sample_weight.
    Assumes `pickup_datetime` is provided as a string by the user in "%Y-%m-%d %H:%M:%S" format
    Assumes `pickup_datetime` implicitly refers to the "US/Eastern" timezone (as any user in New York City would naturally write)
    """
    climat, returned_weight = get_climatology(country_code,sample_weight)
    
    return {'predicted-fare': f"climatology done for {country_code} on {np.round(returned_weight,6)*100}% of the cocoa production from {min(climat.index)} to {max(climat.index)}"}


@app.get("/")
def root():
    return {'greeting': 'Hello'}
