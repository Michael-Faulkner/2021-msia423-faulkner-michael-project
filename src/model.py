import logging
import sys

import numpy
import numpy as np
import pandas as pd
from lightfm.evaluation import auc_score
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
from lightfm import LightFM

logger = logging.getLogger(__name__)


def run_model(interactions, n_components, loss, epoch, n_jobs, random_state):
    """
    Trains the LightFM interaction model
    Args:
        interactions: obj:`scipy.sparse.scr_matrix` Sparse matrix containing the interactions between users and games
        n_components: obj:`int` number of desired embeddings to create to define item and user
        loss: obj:`string` loss function for LightFM model. Options include warp, logistic, and brp
        epoch: obj:`int`  number of epochs to run
        n_jobs: obj:`int` number of cores used for execution
        random_state: obj:`int` Random state to seed the model
    Returns:
        model: obj:`LightFM.model`  Fitted model that has been trained on the interaction matrix
    """
    logger.debug("Creating model with no_components: %d, loss function: %s, and random state: %d", n_components,
                 loss, random_state)
    model = LightFM(no_components=n_components, loss=loss, random_state=random_state)
    logger.debug("Fitting model with epochs: %d and number of threads: %d", epoch, n_jobs)
    model.fit(interactions, epochs=epoch, num_threads=n_jobs)

    return model


def cosine_similarity_matrix(item_embeddings, item_names):
    """
    Calculates cosine similarities for every game present in the user_games dataframe
    Args:
        item_embeddings :obj:`Numpy Array` Item embeddings created by the model to calculate cosine similarity
        item_names :obj:`List[String]` List of game ids used in the LightFM model
    Returns:
        similarity_matrix :obj:`Pandas DataFrame` DataFrame containing the cosine similarity between each item
    """
    if not isinstance(item_embeddings, numpy.ndarray):
        logger.error("%s is not a numpy array object", item_embeddings)
        raise TypeError("Provided argument `item_embeddings` is not a numpy array object")

    df_item_norm_sparse = sparse.csr_matrix(item_embeddings)
    similarities = cosine_similarity(df_item_norm_sparse)
    similarity_matrix = pd.DataFrame(similarities)

    # Name columns and rows with game ids to match up with game info dataframe after querying
    similarity_matrix.columns = item_names
    similarity_matrix.index = item_names

    if len(similarity_matrix) == 0:
        logger.warning("Cosine similarity Matrix does not contain any rows")

    return similarity_matrix


def evaluate_model(interactions, train_size, n_components, loss, epoch, n_jobs, random_state, splits):
    """
    Splits the data into a training and test set. Then trains the LightFM interaction model on the training set
     and evaluates the AUC on a test set.
    Args:
        interactions: obj:`scipy.sparse.scr_matrix` Sparse matrix containing the interactions between users and games
        train_size: obj:`float` Percentage of rows to be in the training set
        n_components: obj:`int` number of desired embeddings to create to define item and user
        loss: obj:`string` loss function for LightFM model. Options include warp, logistic, and brp
        epoch: obj:`int`  number of epochs to run
        n_jobs: obj:`int` number of cores used for execution
        random_state: obj:`int` Random state to seed the model
        splits: obj:`int` What proportion of the data to consider due to memory constraints
    Returns:
        test_auc: obj:`float`  AUC score achieved by the LightFM model on the test set
    """

    interactions_size = round(interactions.shape[0] / splits)
    interactions = interactions.tocsr()[:interactions_size, :]

    try:
        # Create dense matrix in order to fulfil requirements by LightFM's AUC evaluation
        arr_interactions = interactions.todense()

    except MemoryError:
        logger.error("Too many interactions are being used for modeling, increase the number of splits")
        sys.exit(3)

    except Exception as e:
        logger.error(e)
        sys.exit(3)

    train_cut = round(arr_interactions.shape[0] * train_size)
    logger.debug("Creating training set")
    train = sparse.csr_matrix(arr_interactions[:train_cut, :])

    # Have to make tests set the same size of the train set. Documentation says to add empty rows to top of tests set
    empty_users = np.zeros([(train_cut - (arr_interactions.shape[0] - train_cut)), arr_interactions.shape[1]])
    logger.debug("Creating tests set")
    test = np.vstack((arr_interactions[train_cut:, :], empty_users))
    test = sparse.csr_matrix(test)

    model = run_model(train, n_components, loss, epoch, n_jobs, random_state)
    logger.debug("Calculating AUC for tests set")

    test_auc = auc_score(model, test).mean()
    return test_auc
