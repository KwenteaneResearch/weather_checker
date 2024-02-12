FROM tensorflow/tensorflow:2.10.0
WORKDIR /dev

# First, pip install dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Then only, install weather_checker!
COPY weather_checker weather_checker
COPY setup.py setup.py
RUN pip install .

# Initialize folder 
COPY Makefile Makefile
RUN make init_all_data_folders

# Get all data from GDrive shared folders
COPY cookies.txt cookies.txt
RUN make init_gdown
#RUN make dl_raw_weather
#RUN make dl_input_csv
#RUN make dl_gps_locations


CMD uvicorn weather_checker.api.fast:app --host 0.0.0.0