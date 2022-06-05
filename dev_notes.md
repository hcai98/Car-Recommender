

## Modeling

### Archive Data
```Shell
TBD
```

### Clean Data
```shell
python run_model.py clean --input data/raw/table/Ad_table.csv --config config/config_modeling.yml --output data/processed/clean_cars.csv
```

### Featurize
```shell
python run_model.py featurize --input data/processed/clean_cars.csv --config config/config_modeling.yml --output data/processed/feature.csv
```

### Train model (get cluster centroid)
```shell
python run_model.py train --input data/processed/feature.csv --config config/config_modeling.yml --output models/kmeans_50    
```

### Label the cars
```shell
python run_model.py label --input models/kmeans_50 --config config/config_modeling.yml --output data/processed/labels.csv
```

## Database
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

### Ingestiong

Local
```shell
python run_db.py ingest --input data/processed/labels.csv --engine_string 'sqlite:///data/cars.db'      
```