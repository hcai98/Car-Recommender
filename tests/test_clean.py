import pytest
import pandas as pd

from src.modeling.clean import aggregate_by_keys, transform_vars, method_to_func

df_in = pd.DataFrame([['3.0L', '24995'],
                      ['3.0L', 10995],
                      ['3.0L', '57990'],
                      ['1.0L', 5107],
                      ['2.0L', 23000],
                      ['2.2L', 11999],
                      ['1.6L', 1295],
                      ['2.2L', 17990],
                      ['2.0L', 2865],
                      ['3.0L', 2490],
                      ['2.2L', 2694],
                      ['1.9L', 1290],
                      ['1.2L', 13795],
                      ['2.0L', '25989'],
                      ['1.33L', '5950'],
                      ['2.4L', '7495'],
                      ['1.8L', '2795'],
                      ['1.7L', '4799'],
                      ['1.4L', 14791],
                      ['1.6L', 6995]], columns=['engin_size', 'price'])
transformation = {'vars_strip_numeric': ['engin_size'],
                  'vars_drop_non_numeric_rows': ['price']}

df_in_2 = pd.DataFrame([['Hyundai', 2018, 5.0, 4.0],
                        ['Dacia', 2018, 5.0, 5.0],
                        ['Volkswagen', 2018, 5.0, 5.0],
                        ['Jaguar', 2017, 5.0, 4.0],
                        ['Mercedes-Benz', 2021, 5.0, 5.0],
                        ['Mitsubishi', 2018, 5.0, 3.0],
                        ['Land Rover', 2018, 5.0, 5.0],
                        ['MINI', 2018, 2.0, 2.0],
                        ['Renault', 2020, 5.0, 5.0],
                        ['Peugeot', 2018, 5.0, 5.0],
                        ['Land Rover', 2021, 5.0, 5.0],
                        ['Subaru', 2018, 5.0, 5.0],
                        ['Peugeot', 2018, 5.0, 5.0],
                        ['Renault', 2018, 5.0, 5.0],
                        ['Mercedes-Benz', 2018, 5.0, 5.0],
                        ['Kia', 2018, 5.0, 3.0],
                        ['Jaguar', 2018, 2.0, 2.0],
                        ['Jaguar', 2018, 5.0, 4.0],
                        ['Ford', 2018, 7.0, 5.0],
                        ['Ford', 2018, 5.0, 5.0]], columns=['maker', 'year', 'seat_num', 'door_num'])
aggregation = {
    'key_cols': ['maker', 'year'],
    'key_path': 'data/processed/teskeys.csv',
    'agg_cols_transforms': {
        'seat_num': 'first',
        'door_num': 'mode'
    }
}


def test_transform_vars_expected() -> None:
    """
    Test if `transform_vars` works as expected.
    """
    df_true = pd.DataFrame([[3.0000e+00, 2.4995e+04],
                            [3.0000e+00, 1.0995e+04],
                            [3.0000e+00, 5.7990e+04],
                            [1.0000e+00, 5.1070e+03],
                            [2.0000e+00, 2.3000e+04],
                            [2.2000e+00, 1.1999e+04],
                            [1.6000e+00, 1.2950e+03],
                            [2.2000e+00, 1.7990e+04],
                            [2.0000e+00, 2.8650e+03],
                            [3.0000e+00, 2.4900e+03],
                            [2.2000e+00, 2.6940e+03],
                            [1.9000e+00, 1.2900e+03],
                            [1.2000e+00, 1.3795e+04],
                            [2.0000e+00, 2.5989e+04],
                            [1.3300e+00, 5.9500e+03],
                            [2.4000e+00, 7.4950e+03],
                            [1.8000e+00, 2.7950e+03],
                            [1.7000e+00, 4.7990e+03],
                            [1.4000e+00, 1.4791e+04],
                            [1.6000e+00, 6.9950e+03]],
                           columns=['engin_size', 'price'])
    df_true['price'] = df_true['price'].astype(int)

    df_out = transform_vars(data=df_in, transformation=transformation)

    # Test that the true and test are the same
    pd.testing.assert_frame_equal(df_true, df_out)


def test_transform_vars_unexpected() -> None:
    """
    Test if `transform_vars` raises error when encountering unexpected input.
    We expect a type error when input is not a data frame.
    """
    df_in_str = 'I am not a dataframe'

    with pytest.raises(TypeError):
        transform_vars(data=df_in_str, transformation=transformation)


def test_aggregate_by_keys_expected() -> None:
    """
    Test if `aggregate_by_keys` works as expected.
    """
    df_true = pd.DataFrame([[0, 'Dacia', 2018, 5.0, 5.0],
                            [1, 'Ford', 2018, 7.0, 5.0],
                            [2, 'Hyundai', 2018, 5.0, 4.0],
                            [3, 'Jaguar', 2017, 5.0, 4.0],
                            [4, 'Jaguar', 2018, 2.0, 2.0],
                            [5, 'Kia', 2018, 5.0, 3.0],
                            [6, 'Land Rover', 2018, 5.0, 5.0],
                            [7, 'Land Rover', 2021, 5.0, 5.0],
                            [8, 'MINI', 2018, 2.0, 2.0],
                            [9, 'Mercedes-Benz', 2018, 5.0, 5.0],
                            [10, 'Mercedes-Benz', 2021, 5.0, 5.0],
                            [11, 'Mitsubishi', 2018, 5.0, 3.0],
                            [12, 'Peugeot', 2018, 5.0, 5.0],
                            [13, 'Renault', 2018, 5.0, 5.0],
                            [14, 'Renault', 2020, 5.0, 5.0],
                            [15, 'Subaru', 2018, 5.0, 5.0],
                            [16, 'Volkswagen', 2018, 5.0, 5.0]],
                           columns=['newcol', 'maker', 'year', 'seat_num', 'door_num'])

    df_out = aggregate_by_keys(
        data=df_in_2,
        aggregation=aggregation,
        new_index='newcol'
    )

    # Test that the true and test are the same
    pd.testing.assert_frame_equal(df_true, df_out)


def test_aggregate_by_keys_unexpected() -> None:
    """
    Test if `aggregate_by_keys` raises error when encountering unexpected input.
    We expect a key error when key column does not exist.
    """
    df_in_3 = pd.DataFrame([[0, 1, 2, 3]], columns=[
                         'col1', 'col2', 'col3', 'col4'])

    with pytest.raises(KeyError):
        aggregate_by_keys(
            data=df_in_3,
            aggregation=aggregation,
            new_index='newcol'
        )


def test_method_to_func_expected_mean() -> None:
    """
    Test if `method_to_func` works as expected for mean.
    """
    assert method_to_func('mean') == 'mean'


def test_method_to_func_expected_first() -> None:
    """
    Test if `method_to_func` works as expected for first.
    """
    assert method_to_func('first') == 'first'


def test_method_to_func_unexpected() -> None:
    """
    Test if `method_to_func` return None when receiving unexpected input.
    """
    assert method_to_func('not_a_method') is None
