import streamlit as st
import os
import datetime
import pandas as pd
import requests
from pathlib import Path

'''
# Weather checker Streamlit frontend
'''

from_date = datetime.date.today()
to_date = datetime.datetime.today()
top_location_by_country_path = os.path.join(os.getcwd(), 'input_csv', 'top_location_by_country', )
country_data_path = os.path.join(os.getcwd(), 'input_csv', 'country_codes', 'all.csv')
openai_api_key = st.secrets['openai_api_key']


if (Path(country_data_path).is_file()):
    country_df = pd.read_csv(country_data_path)
    country_df = country_df[country_df.region == 'Africa'].copy()
    country_df = country_df.sort_values(by = 'name')[['name', 'alpha-3']]

    country = st.selectbox(
        'Select a country',
        country_df)

    st.write('You selected:', country_df[country_df.name == country]['alpha-3'].values[0])

percentage = 10
percentage = st.slider("Select percentage of country's production", 0, 100, percentage, 1, "%d%%")

weather_events = ['Strong', 'Average daily temperature', 'Precipitation']
weather_event_codes = ['weather_code', 'temperature_2m_mean', 'precipitation_sum']
weather_event = st.selectbox(
    'Select weather event intensity',
    weather_events)
st.write('You selected:', weather_event_codes[weather_events.index(weather_event)])


path = os.path.join(top_location_by_country_path,  'gps_weight_CIV_0.7.csv')
if (percentage <= 7):
   path =  os.path.join(top_location_by_country_path,  'gps_weight_CIV_0.07.csv')
elif (percentage <= 11):
   path =  os.path.join(top_location_by_country_path,  'gps_weight_CIV_0.11.csv')

if (Path(path).is_file()):
    top_producers_df = pd.read_csv(path)
    st.map(top_producers_df)

st.write('Select climatology range')
col1, col2 = st.columns(2)
with col1:
    from_date = st.date_input(
    "From",
    from_date)
with col2:
    to_date = st.date_input(
    'To',
    to_date)

url_location = 'https://weather-checker-ddzfwilp7q-ew.a.run.app/collect_locations'
# url_location = 'http://localhost:8000/collect_locations'
url_climatology = 'https://weather-checker-ddzfwilp7q-ew.a.run.app/compute_climatology'
url_years = 'https://weather-checker-ddzfwilp7q-ew.a.run.app/years_classification'
# url_years = 'localhost:8000/years_classification'
url_monthly_summary = 'https://weather-checker-ddzfwilp7q-ew.a.run.app/get_monthly_summary'

# if url == 'https://taxifare.lewagon.ai/predict':

    # st.markdown('Maybe you want to use your own API for the prediction, not the one provided by Le Wagon...')

if st.button('Get climate!'):
    params = {"country_code": country_df[country_df.name == country]['alpha-3'].values[0],
              "from_date": from_date.strftime("%Y-%m-%d"),
              "to_date": to_date.strftime("%Y-%m-%d"),
              "openai_api_key": openai_api_key,
              "sample_weight": percentage/100,
              "weather_event": weather_event_codes[weather_events.index(weather_event)]
    }
    response = requests.get(url_location, params=params)
    # st.write(f'Status code {response.status_code}')
    st.markdown(f"{response.json()}")

    response = requests.get(url_climatology, params=params)
    # st.write(f'Status code {response.status_code}')
    st.markdown(f"{response.json()}")

    response = requests.get(url_years, params=params)
    # st.write(f'Status code {response.status_code}')
    st.markdown(f"{response.json()}")

    response = requests.get(url_monthly_summary, params=params)
    # st.write(f'Status code {response.status_code}')
    st.markdown(f"{response.json()}")
