import pandas as pd
import pytest

from src.process_data import create_games_csv


def test_create_games_csv():
    df_in = pd.DataFrame([[10, 'game1', 'action', '2013', 'google.com'],
                       [10, 'game1', 'action', '2013', 'google.com'],
                       [20, 'game2', None, '2013', 'google.com'],
                       [30, 'game3', 'action', None, 'google.com'],
                       [40, 'game4', 'action', '2013', None]],
                      columns=['id', 'app_name', 'genres', 'release_date', 'url'])

    df_test = pd.DataFrame([[10, 'game1', 'action', '2013', 'google.com'],
                       [20, 'game2', '', '2013', 'google.com'],
                       [30, 'game3', 'action', '', 'google.com'],
                       [40, 'game4', 'action', '2013', '']],
                      columns=['id', 'app_name', 'genres', 'release_date', 'url'])
    df_test.index = [0, 2, 3, 4]
    df_out = create_games_csv(df_in, ['id', 'app_name', 'genres', 'release_date', 'url'], 'id')

    assert df_test.equals(df_out)


def test_create_games_csv_type():
    df_in = 'test'
    with pytest.raises(TypeError):
        create_games_csv(df_in, ['id', 'app_name', 'genres', 'release_date', 'url'], 'id')