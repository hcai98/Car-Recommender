python run_model.py clean --input data/raw/Ad_table.csv --config config/config_modeling.yml --output data/processed/clean_cars.csv

python run_model.py featurize --input data/processed/clean_cars.csv --config config/config_modeling.yml --output data/processed/feature.csv

python run_model.py train --input data/processed/feature.csv --config config/config_modeling.yml --output models/kmeans_50    

python run_model.py label --input models/kmeans_50 --config config/config_modeling.yml --output data/processed/labels.csv

python run_model.py evaluate --input models/kmeans_50 --config config/config_modeling.yml --output data/evaluation/evaluation_results.csv    
