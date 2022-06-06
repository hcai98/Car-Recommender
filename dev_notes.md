
## Docker Images
```shell
docker build -f dockerfiles/Dockerfile -t final-project .

docker build -f dockerfiles/Dockerfile.app -t final-project-app .

docker build -f dockerfiles/Dockerfile.test -t final-project-tests .
```


## Modeling


### Archive Data
```Shell
TBD
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

## Running the app

```shell
 docker run -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(pwd)"/data,target=/app/data -p 5000:5000 final-project-app  
```
