#FROM tensorflow/tensorflow:2.10.0
FROM python:3.8.12-buster
WORKDIR /usr/src/app

#WORKDIR /dev

# First, pip install dependencies
COPY requirements.txt requirements.txt
#COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Then only, install weather_checker!
COPY weather_checker weather_checker
COPY setup.py setup.py
COPY raw_data raw_data
#RUN pip install .

# Then only, install weather_checker!
#COPY weather_checker .
#COPY setup.py .
RUN pip install .
# Initialize folder
COPY Makefile .

# Initialize folder
#COPY Makefile Makefile
#RUN make init_all_data_folders
#RUN make run_params

# Initialize folder
COPY Makefile Makefile
#RUN make init_all_data_folders


#COPY cookies.txt cookies.txt
#RUN make init_gdown
#RUN make dl_raw_weather
#RUN make dl_input_csv
#RUN make dl_gps_locations


CMD uvicorn weather_checker.api.fast:app --host 0.0.0.0 --port $PORT


#FROM tensorflow/tensorflow:2.10.0
#WORKDIR /usr/src/app
# First, pip install dependencies
#COPY requirements.txt .
#RUN pip install --upgrade pip
#RUN pip install -r requirements.txt
# Then only, install weather_checker!
#COPY weather_checker .
#COPY setup.py .
#RUN pip install .
# Initialize folder
#COPY Makefile .
#RUN make init_all_data_folders
# Get all data from GDrive shared folders
#COPY cookies.txt .
#RUN make init_gdown
#RUN make dl_raw_weather
#RUN make dl_input_csv
#RUN make dl_gps_locations
