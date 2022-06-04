import logging
from typing import Union, Callable

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src import utils_io

logger = logging.getLogger(__name__)


def clean(df: pd.DataFrame,
          transformation: dict,
          aggregation: dict,
          rename_map: dict,
          new_index: str) -> pd.DataFrame:
    """Clean the original data for modeling use. User can specify
    the transformation, aggregation and renaming strategies and 
    inform the function using the dictionaries. 


    Args:
        df (pd.DataFrame): Raw data.
        transformation (dict): Transformations strategy. The keys are 
            the types of transformation. The values are lists of columns 
            to be transformed.
        aggregation (dict): Aggregation strategy. The keys are `key_cols`
            (key columns), `key_path` (path the save the keys for later use), 
            and `agg_cols_transforms` (a dictionary specifying how to summarize
            different columns).
        rename_map (dict): Keys are the columns to be renamed. Values are the new 
            names.
        new_index (str): Name of the new index.

    Returns:
        pd.DataFrame: _description_
    """
    logger.info('Start Cleaning...')
    logger.debug('Raw data dimension %s', df.shape)

    # rename original columns
    df = df.rename(columns=rename_map)

    # perform transformation of specified variables
    df = transform_vars(df, transformation)

    # drop na's
    df = df.dropna()

    # aggregate raw data by keys
    df_output = aggregate_by_keys(df, aggregation, new_index)

    logger.info('Finish Cleaning.')
    return df_output


def transform_vars(df: pd.DataFrame,
                   transformation: dict) -> pd.DataFrame:
    """Transform variables based on user's specification

    Args:
        df (pd.DataFrame): Raw data.
        transformation (dict): User specified transformations (in config.yml).

    Returns:
        pd.DataFrame: Data with transformed columns.
    """
    logger.info('Transforming variables...')

    # strip the numerical engine size from string
    logger.debug('Stripping numerical data from string.')
    for var_strip_numeric in transformation['vars_strip_numeric']:
        df[var_strip_numeric] = (df[var_strip_numeric]
                                 .str.replace('[^\d.]', '').astype(float))

    # drop rows that doesn't have numeric value
    logger.debug('Dropping row that does not have numerical value.')
    for var_drop_non_numeric_rows in transformation['vars_drop_non_numeric_rows']:
        df = df[df[var_drop_non_numeric_rows].astype(str).str.isnumeric()]
        df[var_drop_non_numeric_rows] = df[var_drop_non_numeric_rows].astype(
            int)

    logger.info('Transformation completed.')
    return df


def aggregate_by_keys(df: pd.DataFrame,
                      aggregation: dict,
                      new_index: str) -> pd.DataFrame:
    """Aggregating the data by key columns and specified summary
    methods. 

    Args:
        df (pd.DataFrame): Raw data.
        aggregation (dict): A dictionary specifying how each column will be transformed.
        new_index (str): Name of the index of the aggregated data.

    Returns:
        pd.DataFrame: Aggregated data.
    """
    logger.info('Aggregating data by specified keys.')

    # map transform methods to transform functions
    agg_cols_transforms_funcs = {k: method_to_func(
        v) for k, v in aggregation['agg_cols_transforms'].items()}

    # aggregate raw data by keys
    df_output = (
        df
        .groupby(aggregation['key_cols'])
        .agg(agg_cols_transforms_funcs)
        .reset_index()
        .reset_index(drop=False)
        .rename(columns={'index': new_index})
    )

    # archive key_columns
    utils_io.write_pandas_to_csv(pd.Series(aggregation['key_cols']),
                                 aggregation['key_path'])

    logger.info('Aggregation completed.')

    return df_output


def method_to_func(method_string: str) -> Union[Callable, str]:
    """Map transformation method strings to transformation functions.

    Args:
        method_string (str): Name of transformation.

    Returns:
        Union[Callable, str]: The transformation function.
    """
    if method_string == 'mean':
        return 'mean'
    elif method_string == 'first':
        return 'first'
    elif method_string == 'mode':
        # return pd.Series.mode
        return lambda x: pd.Series.mode(x)[0]