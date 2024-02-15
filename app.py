import streamlit as st
import os
import datetime
import numpy as np
import pandas as pd
import requests
from pathlib import Path

st.markdown('# Climatology Classifier for Top Cocoa Producers')
st.markdown('## Selected crop for the project: cocoa')

market_reports_date = datetime.date.today() - datetime.timedelta(days=8*365+2)
country_data_path = os.path.join(os.getcwd(), 'input_csv', 'country_codes', 'all.csv')
openai_api_key = st.secrets['openai_api_key']


if (Path(country_data_path).is_file()):
    country_df = pd.read_csv(country_data_path)
    country_df = country_df[country_df.region == 'Africa'].copy()
    country_df = country_df.sort_values(by = 'name')[['name', 'alpha-3']]

    default_country_index = 0
    if(country_df.size > 10):
        default_country_index = 10 # "Côte d'Ivoire"
    percentage = 10
    col1, col2 = st.columns(2)
    with col1:
        country = st.selectbox(
            'Select a cocoa producer country',
            country_df,
            index = default_country_index)
    with col2:
        market_reports_date = st.date_input(
        "Market report summary for the month",
        market_reports_date)

col1, col2 = st.columns(2)
with col1:
    percentage = st.slider("Select percentage of country's cocoa production", 0, 100, percentage, 1, "%d%%")
with col2:
    run_openai = st.checkbox('Run OpenAI reports')

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
        st.markdown(f'### Top {percentage}% production locations in {country}:')
        st.map(pd.DataFrame.from_dict(response.json()))

    response = requests.get(url_climatology, params=params)
    if(response.status_code == 200):
        st.markdown(f'### Precipitation climatology for top {percentage}% production locations in {country}:')
        st.markdown(f"{response.json()['climatology']}")

    response = requests.get(url_years, params=params)
    if(response.status_code == 200):
        series_list = []
        st.markdown(f'### Classifying the years and identifying outliers:')
        st.markdown(f'#### Analog years:')
        for element in response.json()['families_of_years']:
            for el in element:
                # st.write(f'{el} -> {element[str(el)]}')
                new_line = pd.Series(' '.join(str(x) for x in element[str(el)]), name=el)
                series_list.append(new_line)
        years_df = pd.DataFrame(series_list)
        years_df.rename(columns = {0: 'Analog years'}, inplace=True)
        st.table(years_df)

        series_list = []
        st.markdown(f'#### Total rain season rainfall (mm) for each analog group:')
        for element in response.json()['family_rain_season_rainfall']:
            # st.write(f"{element} -> {response.json()['family_rain_season_rainfall'][str(element)]}")
            new_line = pd.Series(response.json()['family_rain_season_rainfall'][str(element)], name=element)
            series_list.append(new_line)
        perception_df = pd.DataFrame(series_list)
        perception_df.rename(columns = {0: 'Precipitation in mm'}, inplace=True)
        col1, col2 = st.columns(2)
        with col1:
            st.table(perception_df)
        with col2:
            st.write('')

        st.markdown(f'#### Outlier years based on precipitation amount and intensity:')
        st.markdown(f"{response.json()['outlier_years']}")

    if(run_openai):
        response = requests.get(url_monthly_summary, params=params)
        if(response.status_code == 200):
            st.markdown(f'### Cocoa Market reports for {market_reports_date.strftime("%B %Y")} summarized by OpenAI:')
            st.markdown(f"{response.json()['monthly_summary']}")
