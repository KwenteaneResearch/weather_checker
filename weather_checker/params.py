import os
import numpy as np

##################  VARIABLES  ##################

DATA_SIZE = os.environ.get("DATA_SIZE")
RAW_WEATHER_STORAGE = os.environ.get("RAW_WEATHER_STORAGE")


OPEN_METEO_URL = os.environ.get("OPEN_METEO_URL")
METEO_START_DATE = os.environ.get("METEO_START_DATE")
METEO_END_DATE = os.environ.get("METEO_END_DATE")


GAR_IMAGE = os.environ.get("GAR_IMAGE")
GAR_MEMORY = os.environ.get("GAR_MEMORY") 


##################  CONSTANTS  #####################

RAW_METEO_PATH = os.path.join(os.path.dirname(os.getcwd()), "raw_data")

METEO_COLUMNS_DAILY = ["weather_code","temperature_2m_max", "temperature_2m_min","temperature_2m_mean", "precipitation_sum", "rain_sum"]



################## VALIDATIONS #################

env_valid_options = dict(
    #DATA_SIZE=["1k", "200k", "all"],
    RAW_WEATHER_STORAGE=["local", "big_query"],
)

def validate_env_value(env, valid_options):
    env_value = os.environ[env]
    if env_value not in valid_options:
        raise NameError(f"Invalid value for {env} in `.env` file: {env_value} must be in {valid_options}")


for env, valid_options in env_valid_options.items():
    validate_env_value(env, valid_options)
