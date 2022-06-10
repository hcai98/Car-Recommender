
## Docker Images
```shell
docker build -f dockerfiles/Dockerfile -t final-project .

docker build -f dockerfiles/Dockerfile.app -t final-project-app .

docker build -f dockerfiles/Dockerfile.test -t final-project-tests .
```

## Data Acquisition
```shell
 python run_s3.py --s3path $S3_BUCKET/raw/Ad_table.csv --local_path data/external/Ad_table.csv

 docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="$(pwd)",target=/app final-project run_s3.py --s3path ${S3_BUCKET}/raw/Ad_table.csv --local_path data/external/Ad_table.csv
```


## Modeling


### Acquire Data From S3

```Shell
python run_s3.py --download --s3path $S3_BUCKET/raw/Ad_table.csv --local_path data/raw/Ad_table.csv   

docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="$(pwd)",target=/app final-project run_s3.py --download --s3path $S3_BUCKET/raw/Ad_table.csv --local_path data/raw/Ad_table.csv
```

### Clean Data

```shell
python run_model.py clean --input data/raw/Ad_table.csv --config config/config_modeling.yml --output data/processed/clean_cars.csv

docker run --mount type=bind,source="$(pwd)",target=/app final-project run_model.py clean --input data/raw/Ad_table.csv --config config/config_modeling.yml --output data/processed/clean_cars.csv
```


### Featurize
```shell
python run_model.py featurize --input data/processed/clean_cars.csv --config config/config_modeling.yml --output data/processed/feature.csv

docker run --mount type=bind,source="$(pwd)",target=/app final-project run_model.py featurize --input data/processed/clean_cars.csv --config config/config_modeling.yml --output data/processed/feature.csv
```

### Train model (get cluster centroid)
```shell
python run_model.py train --input data/processed/feature.csv --config config/config_modeling.yml --output models/kmeans_50 

docker run --mount type=bind,source="$(pwd)",target=/app final-project run_model.py train --input data/processed/feature.csv --config config/config_modeling.yml --output models/kmeans_50
```

### Label the cars
```shell
python run_model.py label --input models/kmeans_50 --config config/config_modeling.yml --output data/processed/labels.csv

docker run --mount type=bind,source="$(pwd)",target=/app final-project run_model.py label --input models/kmeans_50 --config config/config_modeling.yml --output data/processed/labels.csv
```

### Evaluate the model
```shell
python run_model.py evaluate --input models/kmeans_50 --config config/config_modeling.yml --output data/evaluation/evaluation_results.csv    
```

## Database

### RDS From Command Line
```shell
docker run \
  -it  \
  --rm \
  mysql:5.7.33 \
  mysql \
  -h${MYSQL_HOST}  \
  -u${MYSQL_USER}  \
  -p${MYSQL_PASSWORD} 
```
### Create Database

Local
```shell
python run_db.py create_db  \
    --engine_string 'sqlite:///data/cars.db'
```

RDS
```shell
python run_db.py create_db  \
    --engine_string mysql+pymysql://$MYSQL_USER:$MYSQL_PASSWORD@$MYSQL_HOST:$MYSQL_PORT/$DATABASE_NAME
```
Any
```shell
docker run --mount type=bind,source="$(pwd)",target=/app -e SQLALCHEMY_DATABASE_URI final-project run_db.py create_db  
```



### Ingestion

Local
```shell
python run_db.py ingest --input data/processed/labels.csv --engine_string 'sqlite:///data/cars.db'      
```

RDS
```shell
python run_db.py ingest --input data/processed/labels.csv \
    --engine_string mysql+pymysql://$MYSQL_USER:$MYSQL_PASSWORD@$MYSQL_HOST:$MYSQL_PORT/$DATABASE_NAME     
```

Any
```shell
docker run --mount type=bind,source="$(pwd)",target=/app -e SQLALCHEMY_DATABASE_URI final-project run_db.py ingest --input data/processed/labels.csv
```

## Running the app

```shell
docker run -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(pwd)"/data,target=/app/data -p 5000:5000 final-project-app  
```


## Deployment on AWS

```shell
docker build -f dockerfiles/Dockerfile.app -t msia423-flask .
```