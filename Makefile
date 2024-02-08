#.DEFAULT_GOAL := install
#################### PACKAGE ACTIONS ###################
install:
    @pip install -e .

reinstall_package:
	@pip uninstall -y weather_checker || :
	@pip install -e .

#run_preprocess:
#	python -c 'from taxifare.interface.main import preprocess; preprocess()'

#run_train:
#	python -c 'from taxifare.interface.main import train; train()'

#run_pred:
#	python -c 'from taxifare.interface.main import pred; pred()'

#run_evaluate:
#	python -c 'from taxifare.interface.main import evaluate; evaluate()'

#run_all: run_preprocess run_train run_pred run_evaluate

#run_workflow:
#	PREFECT__LOGGING__LEVEL=${PREFECT_LOG_LEVEL} python -m taxifare.interface.workflow

#run_api:
#	uvicorn taxifare.api.fast:app --reload


################### LOCAL ACTIONS ################
install_requirements:
	@pip install -r requirements.txt

reset_raw_weather:
	rm -rf ${RAW_DATA_FOLDER}/raw_weather
	mkdir -p ${RAW_DATA_FOLDER}/raw_weather
#	mkdir ~/.lewagon/mlops/data/raw
#	mkdir ~/.lewagon/mlops/data/processed
#	mkdir ~/.lewagon/mlops/training_outputs
#	mkdir ~/.lewagon/mlops/training_outputs/metrics
#	mkdir ~/.lewagon/mlops/training_outputs/models
#	mkdir ~/.lewagon/mlops/training_outputs/params

################### DOCKER ACTIONS ################
docker_build:
	docker build --tag=${GAR_IMAGE}:light .

docker_sh_light:
	docker run -it -e PORT=8000 -p 8000:8000 ${GAR_IMAGE}:light sh 

docker_run_light:
	docker run -e PORT=8000 -p 8000:8000 --env-file .env ${GAR_IMAGE}:light
