import argparse
import logging.config

import pandas as pd
import yaml

from config import modelconfig
from src.modeling import acquire, clean, featurize, train, label
from src import utils_io

# configure logger
logging.config.fileConfig(modelconfig.LOGGING_CONFIG)
logger = logging.getLogger()


if __name__ == '__main__':

    # parse arguments from user input
    parser = argparse.ArgumentParser(
        description='Acquire, clean, create features, and generate clusters from car data')

    parser.add_argument('step', help='Which step to run',
                        choices=['acquire', 'clean', 'featurize', 'train', 'label', 'evaluate'])
    parser.add_argument('--input', '-i', default=None,
                        help='Path to input data')
    parser.add_argument('--config', default='config/local/config_modeling.yml',
                        help='Path to configuration file')
    parser.add_argument('--output', '-o', default=None,
                        help='Path to save output CSV (optional, default = None)')
    parser.add_argument('--model_save_path', default=None,
                        help='Path where the trained model is saved (optional, default = None)')
    args = parser.parse_args()

    # what step are we performing using this script?
    logger.info("Current Step: %s", args.step)

    # Load configuration file for parameters and tmo path
    config = utils_io.read_yml(path=args.config)
    logger.info('Configuration file loaded from %s', args.config)   

    # input data
    if (args.input is not None) and (args.step != 'label'):
        df_input = utils_io.read_pandas(args.input)
        logger.info('Input data loaded from %s', args.input)

    # perform modeling steps
    if args.step == 'acquire':
        pass
        # acquire.acquire(**config['acquire'], output_dir=args.output)
    elif args.step == 'clean':
        # Extract cloud data from raw data file based on the user's specification.
        df_output = clean.clean(df=df_input, **config['clean'])
    elif args.step == 'featurize':
        # Create new features based on user specification.
        df_output = featurize.featurize(data=df_input, **config['featurize'])
    elif args.step == 'train':
        # Train model using features generated. Trained model
        # will be saved to local directory.
        train.train(feature=df_input, model_save_path=args.output, **config['train'])
    elif args.step == 'label':
        # Use the clustering model to label all cars into different classes. 
        # User should also specify the path the clean data and features data 
        # in the config file.
        df_output = label.label(model_save_path=args.input, **config['label'])
    elif args.step == 'evaluate':
        pass
    #     # User should specify pyath to ground truth and prediction in config file
    #     evaluate.evaluate(args.output, **config['evaluate'])

    # Save results of the previous processing step
    # however, if step is "acquire" or "train", we don't save data here
    # as it is handled within the acquire.acquire function.
    if (args.output is not None) and (args.step not in ('acquire', 'train', 'evaluate')):
        utils_io.write_pandas_to_csv(df_output, args.output)
