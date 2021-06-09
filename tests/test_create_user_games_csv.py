import pandas as pd
import pytest

from src.process_data import create_user_games_csv


def test_create_user_games_csv():
    df_in = pd.DataFrame([[0, [{"item_id": "10"}, {"item_id": "20"}]]], columns=['uid', 'items'])
    df2 = pd.DataFrame([[10, 'game1', 'action', '2013', 'google.com'],
                        [20, 'game2', '', '2013', 'google.com'],
                        [30, 'game3', 'action', '', 'google.com'],
                        [40, 'game4', 'action', '2013', '']],
                       columns=['id', 'app_name', 'genres', 'release_date', 'url'])
    df_out = create_user_games_csv(df_in, df2, 'items', 'uid', 'id', 'owned', 'app_name', 'item_id')
    df_test = pd.DataFrame([[0, 10, 1.0], [0, 20, 1.0]], columns=['uid', 'id', 'owned'])

    assert df_test.equals(df_out)


def test_create_user_games_csv_type():
    df_in = 'test'
    df2 = pd.DataFrame([[10, 'game1', 'action', '2013', 'google.com'],
                        [20, 'game2', '', '2013', 'google.com'],
                        [30, 'game3', 'action', '', 'google.com'],
                        [40, 'game4', 'action', '2013', '']],
                       columns=['id', 'app_name', 'genres', 'release_date', 'url'])
    with pytest.raises(TypeError):
        df_in = create_user_games_csv(df_in, df2, 'items', 'uid', 'id', 'owned', 'app_name', 'item_id')