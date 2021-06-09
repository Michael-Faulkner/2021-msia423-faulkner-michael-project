import numpy as np
import pandas as pd
import pytest
from scipy import sparse

from src.process_data import make_sparse


def test_create_interaction_matrix():
    df_in = pd.DataFrame([['0', '10', 1.0], ['0', '20', 1.0],
                          ['1', '10', 1.0], ['1', '20', 1.0],
                          ['2', '10', 1.0], ['2', '15', 1.0]],
                         columns=['uid', 'id', 'owned'])

    row = np.array([0, 0, 1, 1, 2, 2])
    column = np.array([0, 2, 0, 2, 0, 1])
    data = np.array([1, 1, 1, 1, 1, 1])
    test_matrix = sparse.csr_matrix((data, (row, column)), shape=(3, 3))
    sparse_out = sparse.eye(0, 3)
    for user in make_sparse(df_in, 'uid', 'id', 'owned', 2):
        sparse_out = sparse.vstack([sparse_out, user])
    booleans = sparse_out.todense() == test_matrix.todense()
    assert booleans.all()


def test_create_interaction_matrix_type():
    df_in = 'test'
    with pytest.raises(TypeError):
        sparse_out = sparse.eye(0, 3)
        for user in make_sparse(df_in, 'uid', 'id', 'owned', 2):
            sparse_out = sparse.vstack([sparse_out, user])
