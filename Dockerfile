FROM tensorflow/tensorflow:2.10.0
WORKDIR /prod

# First, pip install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Then only, install taxifare!
COPY weather_checker weather_checker
COPY setup.py setup.py
RUN pip install .

# We already have a make command for that!
COPY Makefile Makefile
#RUN make reset_local_files

CMD uvicorn weather_checker.api.fast:app --host 0.0.0.0