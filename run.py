import argparse
import logging.config
import pickle
import sys

import pandas as pd
import yaml

from config.flaskconfig import SQLALCHEMY_DATABASE_URI
from src.create_db import create_db
from src.get_data import download, upload, download_s3
from src.ingest_data import ingest_data
from src.model import run_model, cosine_similarity_matrix, evaluate_model
from src.process_data import create_games_csv, create_user_games_csv, create_interaction_matrix, json_generator

logging.config.fileConfig("config/logging/local.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("task", help="Part of the Pipeline to run", choices=['create_db', 'get_data', 'process_data',
                                                                             'ingest', 'model', 'full'])
    parser.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                        help="SQLAlchemy connection URI for database")
    parser.add_argument("--config_file", default='config/config.yaml', help='Path to configuration file')

    args = parser.parse_args()

    task = args.task

    with open(args.config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if task == 'create_db':
        logger.debug("Running database creation portion of model pipeline")
        create_db(args.engine_string, config['create_db']['remove_old'])

    elif task == 'get_data':
        logger.debug("Running data acquisition portion of model pipeline")
        download(**config['get_data']['steam_game_data']['download'])
        #upload(**config['get_data']['steam_game_data']['upload'])
        download(**config['get_data']['steam_user_data']['download'])
        #upload(**config['get_data']['steam_user_data']['upload'])

    elif task == 'process_data':
        logger.debug("Running process portion of model pipeline")
        # download_s3(**config['process_data']['steam_game_data']['s3_download'])
        # download_s3(**config['process_data']['steam_user_data']['s3_download'])
        logger.debug("Creating csv from json for the Steam games data")
        games_df = pd.read_json(config['process_data']['steam_game_data']['input'])
        games_df = create_games_csv(games_df, **config['process_data']['steam_game_data']['create_games_csv'])
        games_df.to_csv(config['process_data']['steam_game_data']['output'])
        logger.info("Games data has been processed successfully and can be found at %s",
                    config['process_data']['steam_game_data']['output'])
        # upload(**config['process_data']['steam_game_data']['upload'])
        logger.debug("Creating csv from json for the Steam user owned games data")

        user_games_df = []
        logger.debug("Converting json to Dataframe with generator function")
        for json_line in json_generator(config['process_data']['steam_user_data']['input']):
            user_games_df.append(json_line)
        user_games_df = pd.DataFrame(user_games_df)
        user_games_df = create_user_games_csv(user_games_df, games_df,
                                              **config['process_data']['steam_user_data']['create_users_games_csv'])
        user_games_df.to_csv(config['process_data']['steam_user_data']['output'])
        logger.info("User_Games data has been processed successfully and can be found at %s",
                    config['process_data']['steam_user_data']['output'])

    elif task == 'ingest':
        ingest_data(args.engine_string, **config['ingest'])

    elif task == 'model':
        logger.debug("Running model portion of model pipeline")
        user_games_df = pd.read_csv(config['model']['only']['user_games_path'])
        interactions = create_interaction_matrix(user_games_df, **config['model']['interactions'])
        logger.info("Training and Evaluating LightFM Model")
        test_auc = evaluate_model(interactions, **config['model']['evaluate_model'])
        logger.info("Test set had AUC score of %s", str(test_auc))
        try:
            with open(config['model']['filepaths']['auc_txt'], 'w') as f:
                f.write(str(test_auc))
        except OSError:
            logger.error("Could not open: %s", f)
            sys.exit(3)
        except Exception as e:
            logger.error(e)
            sys.exit(3)
        logger.info("Training LightFM model on full dataset")
        model = run_model(interactions, **config['model']['run_model'])
        logger.debug("Creating cosine similarity matrix")
        try:
            with open(config['model']['filepaths']['item_names'], 'rb') as f:
                item_names = pickle.load(f)
        except FileNotFoundError as e:
            logger.error(
                "File containing the game ids was not found, please rerun the model section to create the file")
            sys.exit(3)
        cosine_matrix = cosine_similarity_matrix(model.item_embeddings, item_names)
        cosine_matrix.to_csv(config['model']['filepaths']['cosine_matrix'])
        logger.info("Cosine similarity dataframe was created successfully and saved to %s",
                    config['model']['filepaths']['cosine_matrix'])
        # upload(**config['model']['upload'])

    elif task == 'full':
        logger.debug("Running full model pipeline")
        # download_s3(**config['process_data']['steam_game_data']['s3_download'])
        # download_s3(**config['process_data']['steam_user_data']['s3_download'])
        logger.debug("Creating csv from json for the Steam games data")
        games_df = pd.read_json(config['process_data']['steam_game_data']['input'])
        games_df = create_games_csv(games_df, **config['process_data']['steam_game_data']['create_games_csv'])
        games_df.to_csv(config['process_data']['steam_game_data']['output'])
        logger.info("Games data has been processed successfully and can be found at %s",
                    config['process_data']['steam_game_data']['output'])
        # upload(**config['process_data']['steam_game_data']['upload'])
        logger.debug("Creating csv from json for the Steam user owned games data")

        user_games_df = []
        logger.debug("Converting json to Dataframe with generator function")
        for json_line in json_generator(config['process_data']['steam_user_data']['input']):
            user_games_df.append(json_line)
        user_games_df = pd.DataFrame(user_games_df)
        user_games_df = create_user_games_csv(user_games_df, games_df,
                                              **config['process_data']['steam_user_data']['create_users_games_csv'])
        user_games_df.to_csv(config['process_data']['steam_user_data']['output'])
        logger.info("User_Games data has been processed successfully and can be found at %s",
                    config['process_data']['steam_user_data']['output'])

        logger.debug("Creating parse matrix containing interactions between users and games")
        interactions = create_interaction_matrix(user_games_df, **config['model']['interactions'])
        logger.info("Training and Evaluating LightFM Model")
        test_auc = evaluate_model(interactions, **config['model']['evaluate_model'])
        logger.info("Test set had AUC score of %s", str(test_auc))
        try:
            with open(config['model']['filepaths']['auc_txt'], 'w') as f:
                f.write(str(test_auc))
        except OSError:
            logger.error("Could not open: %s", f)
            sys.exit(3)
        except Exception as e:
            logger.error(e)
            sys.exit(3)
        logger.info("Training LightFM model on full dataset")
        model = run_model(interactions, **config['model']['run_model'])
        logger.debug("Creating cosine similarity matrix")
        try:
            with open(config['model']['filepaths']['item_names'], 'rb') as f:
                item_names = pickle.load(f)
        except FileNotFoundError as e:
            logger.error(
                "File containing the game ids was not found, please rerun the model section to create the file")
            sys.exit(3)
        cosine_matrix = cosine_similarity_matrix(model.item_embeddings, item_names)
        cosine_matrix.to_csv(config['model']['filepaths']['cosine_matrix'])
        logger.info("Cosine similarity dataframe was created successfully and saved to %s",
                    config['model']['filepaths']['cosine_matrix'])
        # upload(**config['model']['upload'])

        if config['pipeline_with_ingest']:
            ingest_data(args.engine_string, **config['ingest'])

        logger.info('Finished Pipeline')
