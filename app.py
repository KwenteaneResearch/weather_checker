import streamlit as st
import os
import datetime
import numpy as np
import pandas as pd
import requests
from pathlib import Path

'''
# Weather checker Streamlit frontend
'''

market_reports_date = datetime.date.today() - datetime.timedelta(days=8*365+2)
top_location_by_country_path = os.path.join(os.getcwd(), 'input_csv', 'top_location_by_country', )
country_data_path = os.path.join(os.getcwd(), 'input_csv', 'country_codes', 'all.csv')
openai_api_key = st.secrets['openai_api_key']


if (Path(country_data_path).is_file()):
    country_df = pd.read_csv(country_data_path)
    country_df = country_df[country_df.region == 'Africa'].copy()
    country_df = country_df.sort_values(by = 'name')[['name', 'alpha-3']]

    default_country_index = 0
    if(country_df.size > 14):
        default_country_index = 14 # "Côte d'Ivoire"
    country = st.selectbox(
        'Select a country',
        country_df,
        index = default_country_index)

percentage = 10
col1, col2 = st.columns(2)
with col1:
    percentage = st.slider("Select percentage of country's production", 0, 100, percentage, 1, "%d%%")
with col2:
    market_reports_date = st.date_input(
    "Market report summary for the month",
    market_reports_date)

url_location = 'https://weather-checker-ddzfwilp7q-ew.a.run.app/collect_locations'
url_climatology = 'https://weather-checker-ddzfwilp7q-ew.a.run.app/compute_climatology'
url_years = 'https://weather-checker-ddzfwilp7q-ew.a.run.app/years_classification'
url_monthly_summary = 'https://weather-checker-ddzfwilp7q-ew.a.run.app/get_monthly_summary'

if st.button('Get climate!'):
    params = {"country_code": country_df[country_df.name == country]['alpha-3'].values[0],
              "year": market_reports_date.year,
              "month": f'{market_reports_date.month:02d}',
              "openai_api_key": openai_api_key,
              "sample_weight": percentage/100
    }

    response = requests.get(url_location, params=params)
    if(response.status_code == 200):
        # longitude = response.json()['longitude']
        # latitude = response.json()['latitude']
        # st.markdown(f"{response.json()}")
        st.markdown(f'### Top {percentage}% production locations in {country}:')
        st.map(pd.DataFrame.from_dict(response.json()))
        # st.markdown(f"{longitude}")

    response = requests.get(url_climatology, params=params)
    if(response.status_code == 200):
        st.markdown(f'### Climatology for top {percentage}% production locations in {country}:')
        st.markdown(f"{response.json()['climatology']}")

    response = requests.get(url_years, params=params)
    if(response.status_code == 200):
        st.markdown(f'### Classifying the years and identifying outliers:')
        st.markdown(f'#### Analog years:')
        for element in response.json()['families_of_years']:
            for el in element:
                st.write(f'{el} -> {element[str(el)]}')
        st.markdown(f'#### family_rain_season_rainfall:')
        for element in response.json()['family_rain_season_rainfall']:
            st.write(f"{element} -> {response.json()['family_rain_season_rainfall'][str(element)]}")
        st.markdown(f'#### Outlier years:')
        st.markdown(f"{response.json()['outlier_years']}")

    response = requests.get(url_monthly_summary, params=params)
    if(response.status_code == 200):
        st.markdown(f'### Weather reports for {market_reports_date.strftime("%B %Y")} summarized by OpenAI:')
        st.markdown(f"{response.json()['monthly_summary']}")
