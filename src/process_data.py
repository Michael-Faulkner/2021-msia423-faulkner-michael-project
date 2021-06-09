import json
import logging
import pickle
import sys

import numpy as np
import pandas as pd
from scipy import sparse


logger = logging.getLogger(__name__)


def json_generator(file_name):
    """Generator function that yields one line of the json file at a time"""
    try:
        with open(file_name) as fh:
            for line in json.load(fh):
                yield line
    except OSError:
        logger.error("Could not read json file: %s", fh)
        sys.exit(3)
    except Exception as e:
        logger.error(e)
        sys.exit(3)



def create_games_csv(df, game_columns, game_id_column):
    """
    Reads the json file into a pandas dataframe. Removes duplicate games to prepare for data ingestion, subsets the
    columns that are needed for the database and fills the NA values with strings to prevent errors during data
    ingestion.

    Args:
        input_json_filepath :obj:`String` Filepath to the games json file downloaded from S3
        output_csv_filepath :obj:`String` Filepath to where the games csv file will be saved locally
        game_columns :obj:`List[String]` Names of the columns needed for data ingestion
        game_id_column :obj:`String` String that specifies the name of the column that contains the steam game id.

    Returns:
        None
    """
    orig_df_len = len(df)
    if not isinstance(df, pd.DataFrame):
        logger.error("%s is not a Pandas Dataframe object", df)
        raise TypeError("Provided argument `df` is not a Panda's DataFrame object")
    try:
        df = df[game_columns]
        df = df.dropna(subset=[game_id_column])
        df = df.drop_duplicates(game_id_column)
        df = df.fillna('')

    except KeyError:
        logger.error("%s not found in dataframe columns, make sure it is spelled correctly", game_id_column)
        sys.exit(3)

    except Exception as e:
        logger.error(e)

    logger.debug("Dropped %d rows from the original dataframe", orig_df_len-len(df))
    return df



def create_user_games_csv(df, df2, old_item_column, user_column, new_item_column,
                          rating_column, title_column, temp_column):
    """
    Reads the input json file in to create the user_games dataframe. Due to the size of the file, the parse generator
    function is used to go row by row and avoid RAM limitations. The newly created user_games dataframe is changed into
    a long format where each row contains a user id, game id, and whether the game is owned or not. The long dataframe
    is filtered by games in the game json file to remove rows where the game id is missing. The resulting dataframe is
    then saved as a csv file.

    Args:
        input_json_filepath :obj:`String` Filepath to the users_games json file downloaded from S3
        output_csv_filepath :obj:`String` Filepath to where the users_games csv file will be saved locally
        old_item_column :obj:`String` String specifying the name of the column that contains the list of owned game ids
        user_column :obj:`String` String that specifies the name of the column that contains the steam user id
        new_item_column :obj:`String` String that specifies the name of the new column containing individual game ids
        rating_column :obj:`String` String that specifies the name of the column representing if a game is owned
        games_json_filepath :obj:`String` Filepath to the games json file downloaded from S3
        title_column :obj:`String` String that specifies the name of the columns that contains the game name
        temp_column :obj:`String` Temporary column name that is used in calculations and renamed to new_item_column
    Returns:
        None
    """
    if not isinstance(df, pd.DataFrame):
        logger.error("%s is not a Pandas Dataframe object", df)
        raise TypeError("Provided argument `df` is not a Panda's DataFrame object")
    try:
        df[temp_column] = df[old_item_column].apply(lambda x: [x[index][temp_column] for index, _ in enumerate(x)])
        df[user_column] = np.arange(len(df))
        df = df[[user_column, temp_column]]
        lst_col = temp_column
        logger.debug("Creating long dataframe from user_games data")
        df = pd.DataFrame({col: np.repeat(df[col].values, df[lst_col].str.len())
                           for col in df.columns.difference([lst_col])
                           }).assign(**{lst_col: np.concatenate(df[lst_col].values)})[
            df.columns.tolist()]
        df[rating_column] = np.ones(shape=df.shape[0])
        df[temp_column] = df[temp_column].astype(int)
        df = df.rename(columns={temp_column: new_item_column})
    except KeyError:
        logger.error("One of the column names specified in the users/games processing step is incorrect")

    df_orig_len = len(df)
    logger.debug("Merging games data and user_games data to filter games that don't exist in games data")
    df = pd.merge(df, df2, on=new_item_column)
    df = df.dropna(axis=0, subset=[title_column])
    logger.debug("Dropped %d rows from the original dataset", df_orig_len-len(df))
    df = df[[user_column, new_item_column, rating_column]]
    return df



def make_sparse(df, user_col, item_col, rating_col, chunk_size):
    """
    Generator function that creates a sparse matrix from the long user_game dataframe. Each yield returns a sparse
    matrix containing the number of users equal to the chunk size

    Args:
        df: The long user_game dataframe to be turned into a sparse matrix
        user_column :obj:`String` String that specifies the name of the column that contains the steam user id
        item_column :obj:`String` String that specifies the name of the new column containing individual game ids
        rating_column :obj:`String` String that specifies the name of the column representing if a game is owned
        chunk_size: obj:`int` How many users to process at one time

    Returns:
        sparse_users: obj:`scipy.sparse.scr_matrix` Sparse matrix containing the interactions between users and games
        with the number of users in the matrix equal to the chunk size

    """
    if not isinstance(df, pd.DataFrame):
        logger.error("%s is not a Pandas Dataframe object", df)
        raise TypeError("Provided argument `df` is not a Panda's DataFrame object")

    items = sorted(df[item_col].unique())
    df_base = pd.DataFrame(columns=[user_col] + items).set_index(user_col)
    users = sorted(df[user_col].unique())
    chunks = len(users) // chunk_size + 1
    logger.debug("Processing data in %d chunks", chunks)
    try:
        for i in range(chunks):
            user_chunk = users[i * chunk_size:(i + 1) * chunk_size]
            user_subset = df[df[user_col].isin(user_chunk)].pivot(index=user_col, columns=item_col, values=rating_col)
            sparse_users = sparse.csr_matrix(df_base.append(user_subset).fillna(0))
            yield sparse_users

    except MemoryError:
        logger.error("Memory error when creating sparse matrix, try making the chunk size smaller")

    except Exception as e:
        logger.error(e)


def create_interaction_matrix(df, user_column, game_column, rating_column, chunk_size,
                              game_id_txt_filepath):

    """
    Creates the interaction sparse matrix from the user_game long dataframe. Due to memory constraints the generator
    function "make_sparse" is used to limit the amount of rows processed at one time. In addition, the game ids are
    saved to a text file in order to name the cosine similarity matrix.

    Args:
        input_csv_filepath: Filepath to the long user_games dataframe
        user_column :obj:`String` String that specifies the name of the column that contains the steam user id
        item_column :obj:`String` String that specifies the name of the new column containing the game ids
        rating_column :obj:`String` String that specifies the name of the column representing if a game is owned
        chunk_size: obj:`int` How many users to process at one time
        game_id_txt_filepath :obj:`String` Filepath to where the game id text file is saved to

    Returns:
        sparse_matrix: obj:`scipy.sparse.scr_matrix` Sparse matrix containing the interactions between users and games
    """
    if not isinstance(df, pd.DataFrame):
        logger.error("%s is not a Pandas Dataframe object", df)
        raise TypeError("Provided argument `df` is not a Panda's DataFrame object")
    try:
        items = sorted(df[game_column].unique())
        num_columns = len(items)
    except KeyError:
        logger.error("%s not found in dataframe, make sure the column name is spelled correctly", game_column)

    with open(game_id_txt_filepath, 'wb') as f:
        pickle.dump(items, f)
        logger.info("Saved game ids to %s", game_id_txt_filepath)

    sparse_matrix = sparse.eye(0, num_columns)
    logger.debug('Creating sparse matrix for model use')
    for user in make_sparse(df, user_column, game_column, rating_column, chunk_size):
        sparse_matrix = sparse.vstack([sparse_matrix, user])

    logger.info('Successfully created sparse interaction matrix')
    return sparse_matrix
