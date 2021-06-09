import numpy as np
import pandas as pd
import pytest

from src.model import cosine_similarity_matrix


def test_cosine_similarity_matrix():
    embeddings_in = np.array([[-.7, .2, .1], [-.2, .6, .9], [.3, -.2, -.7]])
    names_in = ['1', '2', '3']
    df_out = cosine_similarity_matrix(embeddings_in, names_in)
    df_test = pd.DataFrame([['1.0', '0.4329906110980366', '-0.5530409038562268'],
       ['0.4329906110980366', '0.9999999999999998',
        '-0.9351827533650392'],
       ['-0.5530409038562268', '-0.9351827533650392',
        '1.0000000000000002']], columns=['1', '2', '3'])
    df_test.index = ['1', '2', '3']

    df_out = df_out.astype('str')
    assert df_test.equals(df_out)


def test_create_games_csv_type():
    embeddings_in = 'test'
    names_in = ['1', '2', '3']
    with pytest.raises(TypeError):
        df_out = cosine_similarity_matrix(embeddings_in, names_in)