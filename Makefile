#.DEFAULT_GOAL := install
#################### PACKAGE ACTIONS ###################
install:
	@pip install -e .

reinstall_package:
	@pip uninstall -y weather_checker || :
	@pip install -e .

get_daily_data:
	python -c 'from weather_checker.climatology.open_meteo_api import get_daily_data; get_daily_data()'

run_get_climatology:
	python -c 'from weather_checker.interface.main import get_climatology; get_climatology()'


run_all: run_get_climatology



#run_workflow:
#	PREFECT__LOGGING__LEVEL=${PREFECT_LOG_LEVEL} python -m taxifare.interface.workflow

#run_api:
#	uvicorn taxifare.api.fast:app --reload


################### LOCAL ACTIONS ################
install_requirements:
	@pip install -r requirements.txt

init_raw_data_folders:
#	rm -rf raw_data
	mkdir -p raw_data
	mkdir -p raw_data/raw_weather
	mkdir -p raw_data/climatologies
	mkdir -p raw_data/gps_locations

#reset_raw_weather:
#	rm -rf raw_data/raw_weather
#	mkdir -p raw_data/raw_weather

reset_climatologies:
#	rm -rf raw_data/climatologies
	mkdir -p raw_data/climatologies

reset_gps_locations:
#	rm -rf raw_data/gps_locations
	mkdir -p raw_data/gps_locations
	mkdir -p raw_data/gps_locations/to_be_processed
	mkdir -p raw_data/gps_locations/doing
	mkdir -p raw_data/gps_locations/done


################### DOCKER ACTIONS ################
docker_build:
	docker build --tag=${GAR_IMAGE}:light .

docker_sh_light:
	docker run -it -e PORT=8000 -p 8000:8000 ${GAR_IMAGE}:light sh 

docker_run_light:
	docker run -e PORT=8000 -p 8000:8000 --env-file .env ${GAR_IMAGE}:light
