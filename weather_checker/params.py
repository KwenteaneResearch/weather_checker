import os
import numpy as np

##################  VARIABLES FROM .env FILE  ##################

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

##################  CONSTANTS  #####################


# local or big_query
RAW_WEATHER_STORAGE='local'

RAW_DATA_PATH = os.path.join(os.getcwd(), "raw_data")

METEO_COLUMNS_DAILY = ["weather_code","precipitation_sum"] #"temperature_2m_mean"

COUNTRY_PRODUCTION = {"CIV":1879953.9012,
                    "GHA":895249.9013,
                    "NGA":318102.2001,
                    "CMR":299404.9001,
                    "SLE":48671.6,
                    "TGO":42369.2,
                    "UGA":28079.9,
                    "GIN":17018.5,
                    "MDG":11080.1,
                    "TZA":8524.8,
                    "LBR":8056.6999,
                    "COD":3957.2,
                    "COG":3701.4,
                    "STP":3172.7,
                    "GAB":1241.7999,
                    "GNQ":689.5,
                    "AGO":444.2,
                    "CAF":115.3,
                    "BEN":113.0999,
                    "SSD":29.9999,
                    "BFA":11.1,
                    "ZMB":6.7999}

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

COUNTRY_NAMES={"AGO":"Angola",
                "BEN":"Benin",
                "BFA":"Burkina Faso",
                "CMR":"Cameroon",
                "CAF":"Central African Republic",
                "COD":"Democratic Republic of the Congo",
                "CIV":"Ivory Coast",
                "GNQ":"Equatorial Guinea",
                "GAB":"Gabon",
                "GHA":"Ghana",
                "GIN":"Guinea",
                "LBR":"Liberia",
                "MDG":"Madagascar",
                "NGA":"Nigeria",
                "STP":"Sao Tome and Principe",
                "SEN":"Senegal",
                "SLE":"Sierra Leone",
                "TZA":"Tanzania",
                "TGO":"Togo",
                "UGA":"Uganda",
                "ZMB":"Zambia",
                "ZWE":"Zimbabwe"}

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
