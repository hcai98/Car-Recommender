import logging
import sys
from typing import List, Dict, Optional, Union
from joblib import dump, load

import sklearn
import pandas as pd
import yaml

logger = logging.getLogger(__name__)


def read_pandas(input_path: str) -> Optional[Union[pd.DataFrame,
                                                   pd.Series]]:
    """Read csv to pandas data frame or series.

    Args:
        input_path (str): Path of the data

    Returns:
        Union[pd.DataFrame, pd.Series]: Output data.
    """

    if input_path is None:
        logger.warning("Input path is None. Nothing loaded")
        return None

    logger.info("Reading csv from %s", input_path)
    try:
        # read csv to data frame
        data = pd.read_csv(input_path)

        logger.info("Loaded data from %s Size: n_row: %s n_col: %s", input_path,
                    data.shape[0],
                    data.shape[1])
        return data
    except OSError as err_os:
        logger.error("Fail to read data due to OSError. Error message: %s",
                     err_os)
        raise err_os


def write_pandas_to_csv(df_output: Optional[Union[pd.DataFrame,
                                                  pd.Series]],
                        output_path: str) -> None:
    """Save pandas data frame to output path.

    Args:
        df_output (pd.DataFrame, pd.Series): Data to be saved.
        output_path (str): Path to save the data.
    """

    if df_output is None:
        logger.warning("Data frame is None. Nothing saved")
        return

    logger.info("Saving output to %s", output_path)
    try:
        # save data frame to csv
        df_output.to_csv(output_path, index=False)
    except OSError as err_os:
        logger.error("Fail to save data due to OSError. Error message: %s",
                     err_os)
        raise err_os
    logger.info("Output saved to %s", output_path)


def read_yml(path: str) -> Union[Dict, List]:
    """Read YAML file from path and return a dictionary or list.

    Args:
        path (str): Path to the YAML file.

    Returns:
        Union[Dict, List]
    """
    with open(path, "r", encoding="utf-8") as file:
        return_dict = yaml.load(file, Loader=yaml.FullLoader)
        logger.info("YAML file loaded from %s", path)
        return return_dict


def save_model(model: sklearn.base.BaseEstimator,
               output_dir: str) -> None:
    """Save an sklearn model to local directory.

    Args:
        model (sklearn.base.BaseEstimator): An `sklearn` model.
        output_dir (str): Where the model will be saved.
    """
    logger.info("Saving model to %s ...", output_dir)

    # pickle the model and save to local directory
    if output_dir is not None:
        try:
            dump(model, output_dir)
            logger.info("Model saved to %s", output_dir)
        except FileNotFoundError as err_fnf:
            logger.error("Output path not valid: %s", output_dir)
            raise err_fnf
    else:
        logger.error("Output path is None. Model not saved")
        sys.exit(1)


def load_model(input_dir: str) -> sklearn.base.BaseEstimator:
    """Load an sklearn model from local directory.

    Args:
        model (sklearn.base.BaseEstimator): An `sklearn` model.
        input_dir (str): Where the model is saved.
    """
    logger.info("Try loading model from %s ...", input_dir)

    # load the pickled model from local directory
    if input_dir is not None:
        try:
            model = load(input_dir)
            logger.info("Model loaded.")
            return model
        except FileNotFoundError as err_fnf:
            logger.error("Input path not valid: %s", input_dir)
            raise err_fnf
    else:
        logger.error("Input path is None. Model not loaded")
        sys.exit(1)
