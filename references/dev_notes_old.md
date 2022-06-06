# Some notes I took during development

## Data Extraction


### Build data upload image

```bash
docker build -t s3upload -f dockerfiles/Dockerfile.s3 . 
```

```bash
docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY s3upload upload_data.py \
    --directory \
    --s3path=s3://2022-msia423-cai-haoyang/raw/ \
    --local_path data/raw/  
```

```bash
python upload_data.py \
    --directory \
    --s3path=s3://2022-msia423-cai-haoyang/raw/ \
    --local_path data/raw/    
```

### Create table 
```bash
python create_database.py create_db  \
    --engine_string mysql+pymysql://$MYSQL_USER:$MYSQL_PASSWORD@$MYSQL_HOST:$MYSQL_PORT/$DATABASE_NAME
```