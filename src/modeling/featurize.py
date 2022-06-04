import logging
from typing import List

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def featurize(data: pd.DataFrame,
              feature_cols: List[str],
              is_get_dummies: bool,
              is_standardize: bool) -> pd.DataFrame:
    """Generate features from cleaned data.

    Args:
        data (pd.DataFrame): Cleaned data.
        feature_cols (List[str]): Columns to be used as features.
        is_get_dummies (bool): If true, convert categorical variables to 
            dummies variables.
        is_standardize (bool): If true, standardize the data.

    Returns:
        pd.DataFrame: _description_
    """
    logger.info("Generating features from cleaned data...")

    # keep only the data to be
    feature = data[feature_cols]

    # convert categorical data to dummies
    if is_get_dummies:
        logger.info("Getting dummies...")
        feature = pd.get_dummies(data[feature_cols]).astype(float)

    # standardize the variables
    if is_standardize:
        logger.info("Standardizing variables...")
        scaler_std = StandardScaler()
        feature = pd.DataFrame(scaler_std.fit_transform(feature),
                               columns=feature.columns)

    logger.info("All features generated.")
    return feature
