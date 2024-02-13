import os
import numpy as np

##################  VARIABLES  ##################

DATA_SIZE = os.environ.get("DATA_SIZE")
COUNTRY = os.environ.get("COUNTRY")
#COUNTRY_PROD = os.environ.get("COUNTRY_PROD")
RAW_WEATHER_STORAGE = os.environ.get("RAW_WEATHER_STORAGE")


OPEN_METEO_URL = os.environ.get("OPEN_METEO_URL")
METEO_START_DATE = os.environ.get("METEO_START_DATE")
METEO_END_DATE = os.environ.get("METEO_END_DATE")


GAR_IMAGE = os.environ.get("GAR_IMAGE")
GAR_MEMORY = os.environ.get("GAR_MEMORY")

REPORTS_YEAR = os.environ.get("REPORTS_YEAR")


##################  CONSTANTS  #####################

RAW_DATA_PATH = os.path.join(os.getcwd(), "raw_data")

METEO_COLUMNS_DAILY = ["weather_code","precipitation_sum"] #"temperature_2m_mean"

COUNTRY_PRODUCTION = {"CIV":1879953.901,
                      "GHA":895249.9013,
                      "NGA":318102.2002,
                      "CMR":299404.9002,
                      "rest":177288.60,
                      "all":3569999.503}

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
