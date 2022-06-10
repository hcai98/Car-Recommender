from typing import List
import logging
import sys

import pandas as pd
from sklearn.metrics import silhouette_score
from src.utils.io import load_model, read_pandas


logger = logging.getLogger(__name__)


def evaluate(model_path: str,
             feature_path: str,
             metrics: List[str]) -> pd.DataFrame:
    """Evaluate model performance using user specified metrics. Load model from
    model path. Load feature from feature path. Then calculate all evaluation metrics.

    Args:
        model_path (str): Path where the model is saved.
        feature_path (str): Path where the feature is saved.
        metrics (List[str]): A list of metrics to be computed

    Returns:
        pd.DataFrame: Evaluation results.
    """

    # load model
    model = load_model(model_path)
    logger.info('Model loaded.')

    # get all the features from feature_path
    feature = read_pandas(feature_path)
    logger.info('Features loaded.')

    # get cluster assignment
    cluster_assignment = model.predict(feature)
    logger.info('Retrieving cluster assignments from model.')

    # check if metrics are specified.
    logger.debug('The following metrics will be computed: %s', metrics)
    if len(metrics) == 0:
        logger.error(
            'You must specify at least one evaluation metric. Program exiting...')
        sys.exit(1)

    # get evaluation results for all metrics
    result_list = []
    if 'silhouette' in metrics:
        logger.info('Calculating silhouettes statistics.')
        result_list.append(
            ['silhouette', silhouette_score(feature, cluster_assignment)])

    # return all evaluation results
    df_result = pd.DataFrame(result_list, columns=['metric name', 'score'])
    logger.info('Evaluation wrapped into data frame.')

    return df_result
