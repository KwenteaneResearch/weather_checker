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

run_analog_years:
	python -c 'from weather_checker.climatology.models import analog_years; analog_years()'

run_outliers:
	python -c 'from weather_checker.climatology.models import outliers; outliers()'

run_all: run_get_climatology

run_collect_reports:
	python -c 'from weather_checker.nlp.report_summary import get_monthly_reports; get_monthly_reports()'

run_get_summary:
		python -c 'from weather_checker.nlp.report_summary import get_monthly_summary; get_monthly_summary()'

#run_workflow:
#	PREFECT__LOGGING__LEVEL=${PREFECT_LOG_LEVEL} python -m taxifare.interface.workflow

run_api:
	uvicorn weather_checker.api.fast:app --reload


################### LOCAL ACTIONS ################
install_requirements:
	@pip install -r requirements.txt

reset_input_csv:
	rm -rf input_csv
	mkdir -p input_csv

reset_raw_data:
	rm -rf raw_data
	mkdir -p raw_data

reset_raw_weather:
	rm -rf raw_data/raw_weather
	mkdir -p raw_data/raw_weather

reset_climatologies:
	rm -rf raw_data/climatologies
	mkdir -p raw_data/climatologies

reset_gps_locations:
	rm -rf raw_data/gps_locations
	mkdir -p raw_data/gps_locations
	mkdir -p raw_data/gps_locations/to_be_processed
	mkdir -p raw_data/gps_locations/doing
	mkdir -p raw_data/gps_locations/done

reset_pdf_reports:
	rm -rf raw_data/pdf_reports
	mkdir -p raw_data/pdf_reports

init_all_data_folders: reset_input_csv reset_raw_data reset_raw_weather reset_gps_locations reset_pdf_reports

####

init_gdown:
	mkdir -p ~/.cache/gdown/
	mv cookies.txt ~/.cache/gdown/

dl_input_csv:
	mkdir -p input_csv
	gdown "https://drive.google.com/uc?id=1jG1Xh8I34N-zspiAG-8F9DoFNSMVK24U" -O input_csv/coco_all.csv

dl_raw_weather:
	mkdir -p raw_data/raw_weather
	gdown --remaining-ok --folder "https://drive.google.com/drive/folders/1phMlCFtUaj6VCltpeYzU_MOcuvjGh_WT" -O raw_data/raw_weather

dl_gps_locations:
	mkdir -p raw_data/gps_locations
	mkdir -p raw_data/gps_locations/to_be_processed
	gdown --remaining-ok --folder "https://drive.google.com/drive/folders/1SBnpSt1qflznERRmPgSqAV7x2uCwZ2PN" -O raw_data/gps_locations/to_be_processed
	mkdir -p raw_data/gps_locations/doing
	gdown --remaining-ok --folder "https://drive.google.com/drive/folders/1bGgm-BY0RAlREQBDvnVjJqgjd8ymCF28" -O raw_data/gps_locations/doing
	mkdir -p raw_data/gps_locations/done
	gdown --remaining-ok --folder "https://drive.google.com/drive/folders/1QBc6zloba8JNXNU8ClZH2xO3yirRuunQ" -O raw_data/gps_locations/done

#dl_pdf_reports:
#	mkdir -p raw_data/pdf_reports
#	gdown --remaining-ok --folder "https://drive.google.com/drive/folders/1r9vQ2Vj9tg344IEWmt5GTaIEwASjMvP9" -O raw_data/pdf_reports

dl_all_data: init_gdown dl_raw_weather dl_input_csv dl_gps_locations

################### DOCKER ACTIONS ################
docker_build:
	docker build --tag=${GAR_IMAGE}:dev .

docker_sh_dev:
	docker run -it -e PORT=8000 -p 8000:8000 ${GAR_IMAGE}:dev sh

docker_run_dev:
	docker run -e PORT=8000 -p 8000:8000 --env-file .env ${GAR_IMAGE}:dev

########## STREAMLIT ##########

streamlit:
	-@streamlit run app.py
