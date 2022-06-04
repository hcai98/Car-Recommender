import logging
import sys
from typing import List, Optional, Union
from joblib import dump, load
import requests
from requests.exceptions import Timeout, MissingSchema, InvalidSchema
from requests.exceptions import ConnectionError as RequestConnectionError

from typing import Union

import sklearn
import pandas as pd

logger = logging.getLogger(__name__)


def read_pandas(input_path: str) -> Union[pd.DataFrame, pd.Series]:
    """Read csv to pandas data frame or series.

    Args:
        input_path (str): Path of the data

    Returns:
        Union[pd.DataFrame, pd.Series]: Output data.
    """

    if input_path is None:
        logger.warning("Input path is None. Nothing loaded")
        return

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


def write_pandas_to_csv(df_output: Optional[Union[pd.DataFrame, pd.Series]],
                        output_path: str):
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
