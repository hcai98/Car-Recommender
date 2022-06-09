SOURCEDATA_PATH = data/external/Ad_table.csv

# build images
image-model:
	docker build -f dockerfiles/Dockerfile -t final-project . 

image-app:
	docker build -f dockerfiles/Dockerfile.app -t final-project-app .

image-test:
	docker build -f dockerfiles/Dockerfile.test -t final-project-tests .

.PHONY: image-model image-app image-test

# data acquisition
raw-to-s3: ${SOURCEDATA_PATH}
	docker run --mount type=bind,source="$(shell pwd)",target=/app \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		final-project \
		run_s3.py \
		--s3path ${S3_BUCKET}/raw/Ad_table.csv \
		--local_path ${SOURCEDATA_PATH}


# modeling pipeline
## acquire raw data from s3
data/raw/Ad_table.csv:
	docker run --mount type=bind,source="$(shell pwd)",target=/app \
	-e AWS_ACCESS_KEY_ID \
	-e AWS_SECRET_ACCESS_KEY \
	final-project \
	run_s3.py \
	--download \
	--s3path ${S3_BUCKET}/raw/Ad_table.csv \
	--local_path data/raw/Ad_table.csv

acquire-from-s3: data/raw/Ad_table.csv

## clean the raw data
data/processed/clean_cars.csv: config/config_modeling.yml data/raw/Ad_table.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app final-project \
	run_model.py \
	clean \
	--input data/raw/Ad_table.csv \
	--config config/config_modeling.yml \
	--output data/processed/clean_cars.csv

cleaned: data/processed/clean_cars.csv

## create features from raw data
data/processed/feature.csv: config/config_modeling.yml data/processed/clean_cars.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app \
		final-project \
		run_model.py \
		featurize \
		--input data/processed/clean_cars.csv \
		--config config/config_modeling.yml \
		--output data/processed/feature.csv

features: data/processed/feature.csv

## train model
models/kmeans_50: config/config_modeling.yml data/processed/feature.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app \
		final-project \
		run_model.py \
		train \
		--input data/processed/feature.csv \
		--config config/config_modeling.yml \
		--output models/kmeans_50

trained_model: models/kmeans_50

## label the raw data
data/processed/labels.csv: config/config_modeling.yml models/kmeans_50
	docker run --mount type=bind,source="$(shell pwd)",target=/app \
	final-project \
	run_model.py \
	label \
	--input models/kmeans_50 \
	--config config/config_modeling.yml \
	--output data/processed/labels.csv

label: data/processed/labels.csv

## evaluate model
data/evaluation/evaluation_results.csv: models/kmeans_50 config/config_modeling.yml
	docker run --mount type=bind,source="$(shell pwd)",target=/app \
		final-project \
		run_model.py \
		evaluate \
		--input models/kmeans_50 \
		--config config/config_modeling.yml \
		--output data/evaluation/evaluation_results.csv    

evaluate: data/evaluation/evaluation_results.csv

## entire model pipeline
all: label evaluate
pipeline: label evaluate

.PHONY: raw-to-s3 acquire-from-s3 cleaned features trained_model label evaluate all pipeline


# database
create-db:
	docker run --mount type=bind,source="$(shell pwd)",target=/app \
	-e SQLALCHEMY_DATABASE_URI \
	final-project \
	run_db.py \
	create_db 

ingest: create-db data/processed/labels.csv
	docker run --mount type=bind,source="$(shell pwd)",target=/app \
	-e SQLALCHEMY_DATABASE_URI \
	final-project \
	run_db.py \
	ingest \
	--input data/processed/labels.csv

# web app
webapp:
	docker run --mount type=bind,source="$(shell pwd)"/data,target=/app/data -p 5000:5000 \
	-e SQLALCHEMY_DATABASE_URI \
	final-project-app  

# clean up
clean-processed:
	rm -f data/evaluation/* 
	rm -f data/processed/* 

clean-raw:
	rm -f data/raw/*

clean-db:
	rm -f data/*db

clean: clean-raw clean-processed clean-db


.PHONY: clean clean-raw
