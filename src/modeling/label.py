import logging

import pandas as pd

from src import utils_io

logger = logging.getLogger(__name__)


def label(model_save_path: str,
          feature_path: str,
          clean_data_path: str,
          col_cluster: str) -> pd.DataFrame:
    """Using the clustering model to label all cars in the data set.
    Return the clean data set with cluster assignment appended.

    Args:
        model_save_path (str): Path to the clustering model.
        feature_path (str): Path to the feature data.
        clean_data_path (str): Path to the clean data.
        col_cluster (str): Name of the cluster assignment column.

    Returns:
        pd.DataFrame: Clean data with the assignment column appended.
    """
    # load model from path
    model = utils_io.load_model(model_save_path)
    logger.info('Model loaded.')

    # load feature
    feature = utils_io.read_pandas(feature_path)
    logger.info('Features loaded.')

    # label: get cluster assignment
    cluster_assignment = model.predict(feature)
    logger.info('Cluster assigned.')

    # load clean data
    data = utils_io.read_pandas(clean_data_path)
    logger.info('Clean data loaded.')

    # append cluster assignment to every car
    labels = data.copy()
    labels[col_cluster] = cluster_assignment
    logger.info('Cluster assignment appended to the clean data set.')
    logger.debug('Number of cars in each clusters: \n%s',
                 labels[col_cluster].value_counts())

    return labels
