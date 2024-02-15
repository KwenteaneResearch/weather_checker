import os
import numpy as np

##################  VARIABLES FROM .env FILE  ##################

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

##################  CONSTANTS  #####################


# local or big_query
RAW_WEATHER_STORAGE='local'

RAW_DATA_PATH = os.path.join(os.getcwd(), "raw_data")

METEO_COLUMNS_DAILY = ["weather_code","precipitation_sum"] #"temperature_2m_mean"

COUNTRY_PRODUCTION = {"CIV":1879953.901,
                      "GHA":895249.9013,
                      "NGA":318102.2002,
                      "CMR":299404.9002,
                      "rest":177288.60,
                      "all":3569999.503}

COUNTRY_MAX_PERCENT={"CIV":0.1195,
                    "GHA":0.3053,
                    "NGA":0.1265,
                    "CMR":0.2878,
                    "SLE":0.3153,
                    "TGO":0.1061,
                    "UGA":0.1128,
                    "GIN":0.1004,
                    "MDG":0.6384,
                    "TZA":0.9721,
                    "LBR":0.2187,
                    "COD":0.3011,
                    "COG":0.1466,
                    "STP":1,
                    "GAB":0.9374,
                    "GNQ":0.1705,
                    "AGO":0.2075,
                    "CAF":0.13,
                    "BEN":1,
                    "SSD":1,
                    "BFA":1,
                    "ZMB":1}

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
    env_value = os.environ.get(env)
    if env_value not in valid_options:
        #raise NameError(f"INSIDE Invalid value for {env}{os.environ[env]} in `.env` file: {env_value} must be in {valid_options}")
        raise NameError(f"env:{env} func:{os.environ[env]} file: {env_value} valid_opt: {valid_options}")


'''def validate_env_value(env, valid_options):
    env_value = os.environ[env]
    if env_value not in valid_options:
        raise NameError(f"Invalid value for {env} in `.env` file: {env_value} must be in {valid_options}")'''


for env, valid_options in env_valid_options.items():
    validate_env_value(env, valid_options)


if __name__=="__main__":
    for env, valid_options in env_valid_options.items():
        validate_env_value(env, valid_options)
