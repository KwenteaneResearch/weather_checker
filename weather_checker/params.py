import os
import numpy as np

##################  VARIABLES FROM .env FILE  ##################

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

##################  CONSTANTS  #####################


# local or big_query
RAW_WEATHER_STORAGE="local"

RAW_DATA_PATH = os.path.join(os.getcwd(), "raw_data")

METEO_COLUMNS_DAILY = ["weather_code","precipitation_sum"] #"temperature_2m_mean"

COUNTRY_PRODUCTION = {"CIV":1879953.901,
                      "GHA":895249.9013,
                      "NGA":318102.2002,
                      "CMR":299404.9002,
                      "rest":177288.60,
                      "all":3569999.503}

# Geo Data Params
# Percentage of cumulative weight processed
DATA_SIZE = 0.05
COUNTRY = "CIV" 

# Open Meteo API
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
METEO_START_DATE = "1940-01-01"
METEO_END_DATE = "2023-12-31"


REPORTS_YEAR = 2016
REPORTS_MONTH = 2

################## VALIDATIONS #################

env_valid_options = dict(
    #DATA_SIZE=["1k", "200k", "all"],
    RAW_WEATHER_STORAGE=["local", "big_query"],
    COUNTRY=["CIV","GHA","NGA","CMR","rest","all"]
)

def validate_env_value(env, valid_options):
    env_value = os.environ[env]
    if env_value not in valid_options:
        raise NameError(f"Invalid value for {env} in `.env` file: {env_value} must be in {valid_options}")


for env, valid_options in env_valid_options.items():
    validate_env_value(env, valid_options)
