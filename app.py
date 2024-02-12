import streamlit as st
import os
import datetime
import pandas as pd
import requests

'''
# Weather checker Streamlit frontend
'''

d = datetime.date.today()
t = datetime.datetime.now()
raw_data_path = os.path.join(os.getcwd(), "raw_data")

country_df = pd.read_csv(os.path.join(raw_data_path,  'country_codes/all.csv'))
country_df = country_df[country_df.region == 'Africa'].copy()
country_df = country_df.sort_values(by = 'name')[['name', 'alpha-3']]

country = st.selectbox(
    'Select a country',
    country_df)

st.write('You selected:', country_df[country_df.name == country]['alpha-3'].values[0])

percentage = 10
percentage = st.slider("Select percentage of country's production", 0, 100, percentage, 1, "%d%%")

path = os.path.join(raw_data_path,  'gps_locations/gps_weight_CIV_0.7.csv')
if (percentage <= 7):
   path =  os.path.join(raw_data_path,  'gps_locations/gps_weight_CIV_0.07.csv')
elif (percentage <= 11):
   path =  os.path.join(raw_data_path,  'gps_locations/gps_weight_CIV_0.11.csv')

top_producers_df = pd.read_csv(path)
st.map(top_producers_df)

col1, col2 = st.columns(2)
with col1:
    d = st.date_input(
    "Pick up date",
    d)
with col2:
    t = st.time_input(
    'Pick up time',
    t)

url = 'https://taxifare.lewagon.ai/predict'

# if url == 'https://taxifare.lewagon.ai/predict':

    # st.markdown('Maybe you want to use your own API for the prediction, not the one provided by Le Wagon...')

if st.button('Get climate!'):
    params = {"country": country_df[country_df.name == country]['alpha-3'].values[0],
              "pickup_datetime": datetime.datetime.combine(d, t).strftime("%Y-%m-%d %H:%M:%S"),
              "percentage": percentage
    }
    response = requests.get(url, params=params)
    st.write(f'Status code {response.status_code}')
    st.markdown(f"# $ {response.json()['fare']:.2f}")
