FROM tensorflow/tensorflow:2.10.0
WORKDIR /test

# First, pip install dependencies
COPY requirements.txt requirements.txt
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
RUN make dl_all_data


CMD uvicorn weather_checker.api.fast:app --host 0.0.0.0