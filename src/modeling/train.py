import logging

import pandas as pd
from sklearn.cluster import KMeans

from src import utils_io

logger = logging.getLogger(__name__)


def train(feature: pd.DataFrame,
          model_save_path: str,
          model_config: dict):
    """Train a clustering model and save to local directory.

    Args:
        feature (pd.DataFrame): Data frame with all the features column.
        model_save_path (str): Path to save the trained model.
        model_config (dict): Model configurations
    """

    logger.info('Fitting model... Model config: %s', model_config)

    # fit model
    model = KMeans(**model_config).fit(feature)
    logger.info('Model fitted.')

    # save model to local directory
    utils_io.save_model(model, model_save_path)
