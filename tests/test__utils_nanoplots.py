import numpy as np
import pytest
import polars as pl
from great_tables import GT, nanoplot_options


from typing import Any, Union
from decimal import Decimal
from great_tables._utils_nanoplots import (
    _flatten_list,
    _format_number_compactly,
    _generate_nanoplot,
    _generate_ref_line_from_keyword,
    _get_extreme_value,
    _get_n_intlike,
    _gt_first,
    _gt_last,
    _gt_max,
    _gt_mean,
    _gt_median,
    _gt_min,
    _gt_q1,
    _gt_q3,
    _gt_quantile,
    _is_integerlike,
    _is_intlike,
    _normalize_option_list,
    _normalize_to_dict,
    _normalize_vals,
    _remove_exponent,
    _val_is_numeric,
    _val_is_str,
    calc_ref_value,
)

Y_VALS: list[Union[int, float]] = [-5.3, 6.3, -2.3, 0, 2.3, 6.7, 14.2, 0, 2.3, 13.3]
X_VALS: list[Union[int, float]] = [1.2, 3.4, 4.2, 5.0, 5.8, 6.7, 8.3, 10.2, 10.9, 12.2]

CASES: list[dict[str, Any]] = [
    dict(y_vals=Y_VALS),
    dict(y_vals=Y_VALS, y_ref_line=0),
    dict(y_vals=Y_VALS, y_ref_line="mean"),
    dict(y_vals=Y_VALS, y_ref_area=[0.1, 5.3]),
    # could test that its output is equiv to above
    dict(y_vals=Y_VALS, y_ref_area=[5.3, 0.1]),
    dict(y_vals=Y_VALS, y_ref_area=["min", "median"]),
    # could test that its output is equiv to above
    dict(y_vals=Y_VALS, y_ref_area=["median", "min"]),
    dict(y_vals=Y_VALS, y_ref_area=["median", 0]),
    dict(y_vals=Y_VALS, y_ref_area=[0, "median"]),
    dict(y_vals=Y_VALS, y_ref_line=0, y_ref_area=[2.3, "max"]),
    dict(y_vals=Y_VALS, plot_type="bar"),
    dict(y_vals=Y_VALS, y_ref_line=0, plot_type="bar"),
    dict(y_vals=Y_VALS, y_ref_line="mean", plot_type="bar"),
    dict(y_vals=Y_VALS, y_ref_area=[0.1, 5.3], plot_type="bar"),
    dict(y_vals=Y_VALS, y_ref_area=["min", "median"], plot_type="bar"),
    dict(y_vals=Y_VALS, y_ref_area=["median", 0], plot_type="bar"),
    dict(y_vals=Y_VALS, y_ref_area=[1.2, "max"], plot_type="bar"),
    dict(y_vals=Y_VALS, y_ref_line=0, y_ref_area=[2.3, "max"], plot_type="bar"),
    dict(y_vals=Y_VALS[0], all_single_y_vals=Y_VALS),
    dict(y_vals=3432, all_single_y_vals=Y_VALS),
    dict(y_vals=Y_VALS[0], all_single_y_vals=Y_VALS, plot_type="bar"),
    # below is impossible in fmt_nanoplot, but is possible inside _generate_nanoplot
    dict(y_vals=3432, all_single_y_vals=Y_VALS, plot_type="bar"),
    dict(y_vals=Y_VALS, x_vals=X_VALS),
    dict(y_vals=Y_VALS, x_vals=[]),
]


def test_val_is_numeric():
    # Test case 1: Numeric values
    assert _val_is_numeric(1)
    assert _val_is_numeric(1.0)

    # Test case 2: Non-numeric values
    assert not _val_is_numeric("a")


def test_val_is_numeric_fails_list_input():
    with pytest.raises(ValueError):
        _val_is_numeric([1, 2, 3])


def test_val_is_str():
    # Test case 1: String values
    assert _val_is_str("a")

    # Test case 2: Non-string values
    assert not _val_is_str(1)


def test_val_is_str_fails_list_input():
    with pytest.raises(ValueError):
        _val_is_str(["a", "b", "c"])


# TODO: add tests for _val_is_missing()


def test_is_integerlike():
    # Test case 1: Integer-like values
    assert _is_integerlike([1])
    assert _is_integerlike([-1])
    assert _is_integerlike([0])
    # assert _is_integerlike([1.0, 2.0, 3.0, 6.0]) # TODO: this should pass
    # assert _is_integerlike([-1.0]) # TODO: this should pass
    # assert _is_integerlike([2e15]) # TODO: this should pass
    # assert _is_integerlike([3.2343e15]) # TODO: this should pass
    assert _is_integerlike([0, 79])
    assert _is_integerlike([-234234, 0, 2343, 6342379])

    # Test case 2: Non-integer-like values
    assert not _is_integerlike([1.1])
    assert not _is_integerlike([1e-5])
    assert not _is_integerlike([-3, 4, 5.4])
    assert not _is_integerlike([])


# TODO: add tests for _any_na_in_list()

# TODO: add tests for _check_any_na_in_list()

# TODO: add tests for _remove_na_from_list()


def test_normalize_option_list():
    # Test case 1: Normalization with five values
    x = [1, 2, 3, 4, 5]
    expected_output = [1, 2, 3, 4, 5]
    assert _normalize_option_list(x, num_y_vals=5) == expected_output

    # Test case 2: Normalization with missing values
    x = [1, np.nan, 3, 4, np.nan]
    expected_output = [1, np.nan, 3, 4, np.nan]
    assert _normalize_option_list(x, num_y_vals=5) == expected_output

    # Test case 3: Normalization with all missing values
    x = [np.nan, np.nan, np.nan]
    expected_output = [np.nan, np.nan, np.nan]
    assert _normalize_option_list(x, num_y_vals=3) == expected_output

    # Test case 4: Normalization of single value in list
    x = [1]
    expected_output = [1, 1, 1, 1, 1]
    assert _normalize_option_list(x, num_y_vals=5) == expected_output

    # Test case 5: Normalization of single value (not in list)
    x = 1
    expected_output = [1, 1, 1, 1, 1]
    assert _normalize_option_list(x, num_y_vals=5) == expected_output


@pytest.mark.parametrize(
    "vals,dst",
    [
        ([1, 2, 3, 4], [0.0, 0.3333333333333333, 0.6666666666666666, 1.0]),
        ([1.2, 2.1, 3.4, 4.3], [0.0, 0.29032258064516137, 0.7096774193548389, 1.0]),
        (
            [-4, -4.5, -2, 0, 1, 2, 3, 4],
            [
                0.058823529411764705,
                0.0,
                0.29411764705882354,
                0.5294117647058824,
                0.6470588235294118,
                0.7647058823529411,
                0.8823529411764706,
                1.0,
            ],
        ),
        ([-5.3, -2.3, -23.2, 0], [0.771551724137931, 0.9008620689655172, 0.0, 1.0]),
    ],
)
def test_normalize_vals(
    vals: Union[list[Union[int, float]], list[int], list[float]], dst: list[Union[int, float]]
):
    res = _normalize_vals(vals)
    assert res == dst


def test_normalize_to_dict():
    # Test case 1: Normalization with no missing values
    assert _normalize_to_dict(a=3.5, b=-0.3) == {"a": [1.0], "b": [0.0]}

    # Test case 2: Normalization with missing values
    assert _normalize_to_dict(a=3.5, b=np.nan, c=4.0) == {"a": [0.0], "b": [np.nan], "c": [1.0]}

    # Test case 3: Normalization with negative values
    assert _normalize_to_dict(a=3.5, b=np.nan, c=4.0, werwdf=-5) == {
        "a": [0.9444444444444444],
        "b": [np.nan],
        "c": [1.0],
        "werwdf": [0.0],
    }

    # Test case 4: Normalization with non-unique values
    res = _normalize_to_dict(a=5, b=5, c=5)

    # Get values from res into a list and sort them
    res = sorted(list(res.values()))

    assert res[0][0] == 0.0
    assert res[1][0] > 0.0 and res[1][0] < 1.0
    assert res[2][0] == 1.0


@pytest.mark.parametrize(
    "name,dst",
    [
        ("min", 1),
        ("max", 4),
        ("median", 2.5),
        ("mean", 2.5),
    ],
)
def test_calc_ref_value(name: str, dst: float):
    res = calc_ref_value(name, [3, 1, 4, 2])
    assert res == dst


@pytest.mark.parametrize(
    "num,dst",
    [
        (1e-23, "1.0E−23"),
        (1.2363423e-23, "1.2E−23"),
        (1.9001e-20, "1.9E−20"),
        (1.243234e-10, "1.2E−10"),
        (0.002345322, "2.3E−03"),
        (0.074234, "0.074"),
        (0.32923, "0.33"),
        (0.3, "0.30"),
        (0.1, "0.10"),
        (0.99, "0.99"),
        (0.999999991, "1.0"),
        (0, "0"),
        (0.0000, "0"),
        (1, "1.00"),
        (1.2, "1.20"),
        (23.34, "23.3"),
        (999.823, "1,000"),
        (1002.62, "1.00K"),
        (56256.99345, "56.3K"),
        (262456.632, "262K"),
        (838238.123, "838K"),
        (9237442.4, "9.24M"),
        (23425521.8, "23.4M"),
        (682378385.0, "682M"),
        (7453473217.4, "7.45B"),
        (890236897525, "890B"),
        (3324986945826, "3.32T"),
        (367353689054245, "367T"),
        (8923749826567834, "8.9E15"),
        (90872346782346451237345, "9.1E22"),
        (-1.243234e-10, "−1.2E−10"),
        (-93456734587347958, "−9.3E16"),
    ],
)
def test_format_number_compactly_basic(num: float, dst: str):
    res = _format_number_compactly(val=num)
    assert res == dst


@pytest.mark.parametrize(
    "num,dst",
    [
        (1e-23, "1.0E−23"),
        (1.2363423e-23, "1.2E−23"),
        (1.9001e-20, "1.9E−20"),
        (1.243234e-10, "1.2E−10"),
        (0.002345322, "2.3E−03"),
        (0.074234, "0"),
        (0.32923, "0"),
        (0.3, "0"),
        (0.1, "0"),
        (0.99, "1"),
        (0.999999991, "1"),
        (0, "0"),
        (0.0000, "0"),
        (1, "1"),
        (1.2, "1"),
        (23.34, "23"),
        (999.823, "1,000"),
        (1002.62, "1.00K"),
        (56256.99345, "56.3K"),
        (262456.632, "262K"),
        (838238.123, "838K"),
        (9237442.4, "9.24M"),
        (23425521.8, "23.4M"),
        (682378385.0, "682M"),
        (7453473217.4, "7.45B"),
        (890236897525, "890B"),
        (3324986945826, "3.32T"),
        (367353689054245, "367T"),
        (8923749826567834, "8.9E15"),
        (90872346782346451237345, "9.1E22"),
        (-1.243234e-10, "−1.2E−10"),
        (-93456734587347958, "−9.3E16"),
    ],
)
def test_format_number_compactly_integer(num: float, dst: str):
    res = _format_number_compactly(val=num, as_integer=True)
    assert res == dst


@pytest.mark.parametrize(
    "num,currency,dst",
    [
        (1.243234e-10, "USD", "$0.00"),
        (0.002345322, "USD", "$0.00"),
        (0.074234, "USD", "$0.07"),
        (0.32923, "USD", "$0.33"),
        (0.3, "USD", "$0.30"),
        (0.1, "USD", "$0.10"),
        (0.99, "USD", "$0.99"),
        (0.999999991, "USD", "$1.00"),
        (0, "USD", "0"),
        (0.0000, "USD", "0"),
        (1, "USD", "$1.00"),
        (1.2, "USD", "$1.20"),
        (23.34, "USD", "$23.34"),
        (999.823, "USD", "$999.82"),
        (1002.62, "USD", "$1,002.62"),
        (56256.99345, "USD", "$56,257.0"),
        (262456.632, "USD", "$262,457"),
        (838238.123, "USD", "$838,238"),
        (9237442.4, "USD", "$9,237,442.4"),
        (23425521.8, "USD", "$23,425,521.8"),
        (682378385.0, "USD", "$682,378,385.0"),
        (7453473217.4, "USD", "$7,453,473,217.4"),
        (890236897525, "USD", "$890,236,897,525.0"),
        (3324986945826, "USD", "$3,324,986,945,826.0"),
        (367353689054245, "USD", "$367,353,689,054,245.0"),
        (8923749826567834, "USD", ">"),
        (90872346782346451237345, "USD", ">"),
        (-1.243234e-10, "USD", "−$0.00"),
        (-93456734587347958, "USD", ">"),
        (-642.34, "USD", "−$642.34"),
        (23534, "EUR", "&#8364;23,534.0"),
        (556.325, "KRW", "&#8361;556"),
        (82.63, "HKD", "HK$82.63"),
        (838238.123, None, "838K"),
    ],
)
def test_format_number_compactly_currency(num: float, currency: Union[str, None], dst: str):
    res = _format_number_compactly(val=num, currency=currency)
    assert res == dst


@pytest.mark.parametrize(
    "num,dst",
    [
        ([1], 1.0),
        ([1, 1], 1.0),
        ([1, 2, 3], 2.0),
        ([-5, 0.1, 5], 0.033333333333333215),
        ([2.1e15, 2342, 5.3e8], 700000176667447.4),
    ],
)
def test_gt_mean(num: list[Union[int, float]], dst: float):
    res = _gt_mean(num)
    assert res == dst


@pytest.mark.parametrize(
    "num,dst",
    [
        ([1], 1.0),
        ([1, 1], 1.0),
        ([1, 2, 3], 1.0),
        ([-5, 0.1, 5], -5.0),
        ([2.1e15, 2342, 5.3e8], 2342),
    ],
)
def test_gt_min(num: list[Union[int, float]], dst: float):
    res = _gt_min(num)
    assert res == dst


@pytest.mark.parametrize(
    "num,dst",
    [
        ([1], 1.0),
        ([1, 1], 1.0),
        ([1, 2, 3], 3.0),
        ([-5, 0.1, 5], 5.0),
        ([2.1e15, 2342, 5.3e8], 2100000000000000.0),
    ],
)
def test_gt_max(num: list[Union[int, float]], dst: float):
    res = _gt_max(num)
    assert res == dst


@pytest.mark.parametrize(
    "num,dst",
    [
        ([1], 1.0),
        ([1, 1], 1.0),
        ([1, 2, 3], 2.0),
        ([1, 2, 3, 4], 2.5),
        ([-5, 0.1, 5], 0.1),
        ([2.1e15, 2342, 5.3e8], 5.3e8),
    ],
)
def test_gt_median(num: list[Union[int, float]], dst: float):
    res = _gt_median(num)
    assert res == dst


@pytest.mark.parametrize(
    "num,dst",
    [
        ([1], 1.0),
        ([1, 1], 1.0),
        ([3, 2, 1], 3.0),
        ([1, 2, 3, 4], 1.0),
        ([-5, 0.1, 5], -5.0),
        ([0, 2.1e15, 2342, 5.3e8, 0, -2343], 0),
    ],
)
def test_gt_first(num: list[Union[int, float]], dst: float):
    res = _gt_first(num)
    assert res == dst


@pytest.mark.parametrize(
    "num,dst",
    [
        ([1], 1.0),
        ([1, 1], 1.0),
        ([3, 2, 1], 1.0),
        ([1, 2, 3, 4], 4.0),
        ([-5, 0.1, 5], 5.0),
        ([0, 2.1e15, 2342, 5.3e8, 0, -2343], -2343.0),
    ],
)
def test_gt_last(num: list[Union[int, float]], dst: float):
    res = _gt_last(num)
    assert res == dst


@pytest.mark.parametrize(
    "num,q,dst",
    [
        ([1], 0, 1.0),
        ([1], 0.5, 1.0),
        # ([1], 1.0, 1.0), # TODO: causes 'IndexError: list index out of range'
        ([1, 1], 0, 1.0),
        ([1, 1], 0.33, 1.0),
        ([1, 1], 0.66, 1.0),
        # ([1, 1], 1.0, 1.0), # TODO: causes 'IndexError: list index out of range'
        ([3, 2, 1], 0, 1.0),
        ([3, 2, 1], 0.2, 1.0),
        ([3, 2, 1], 0.4, 2.0),
        ([3, 2, 1], 0.6, 2.0),
        ([3, 2, 1], 0.8, 3.0),
        # ([3, 2, 1], 1.0, 3.0), # TODO: causes 'IndexError: list index out of range'
        ([1, 3, 3, 5], 0, 1.0),
        ([1, 3, 3, 5], 0.2, 1.0),
        ([1, 3, 3, 5], 0.4, 3.0),
        ([1, 3, 3, 5], 0.6, 3.0),
        ([1, 3, 3, 5], 0.8, 5.0),
        # ([1, 3, 3, 5], 1.0, 5.0), # TODO: causes 'IndexError: list index out of range'
        ([1, 3, 3, 3, 5], 0, 1.0),
        ([1, 3, 3, 3, 5], 0.1, 1.0),
        ([1, 3, 3, 3, 5], 0.2, 3.0),
        ([1, 3, 3, 3, 5], 0.3, 3.0),
        ([1, 3, 3, 3, 5], 0.4, 3.0),
        ([1, 3, 3, 3, 5], 0.5, 3.0),
        ([1, 3, 3, 3, 5], 0.6, 3.0),
        ([1, 3, 3, 3, 5], 0.7, 3.0),
        ([1, 3, 3, 3, 5], 0.8, 5.0),
        ([1, 3, 3, 3, 5], 0.9, 5.0),
        # ([1, 3, 3, 3, 5], 1.0, 5.0), # TODO: causes 'IndexError: list index out of range'
    ],
)
def test_gt_quantile(num: list[Union[int, float]], q: float, dst: float):
    res = _gt_quantile(num, q=q)
    assert res == dst


@pytest.mark.parametrize(
    "num,dst",
    [
        ([1], 1.0),
        ([1, 1], 1.0),
        ([3, 2, 1], 1.0),
        ([1, 2, 3, 4], 2.0),
        ([1, 2, 2, 3, 4], 2.0),
        ([1, 2, 2, 3, 3, 3, 4, 4], 2.0),
        ([0.01, 0.5, 0.25, 1, 2, 2, 3, 3, 3, 4, 4], 0.5),
        ([-5, 0.1, 5], -5.0),
        ([1, 1, 1, 0.5, 1.2], 1.0),
        ([0, 2.1e15, 2342, 5.3e8, 0, -2343], 0.0),
    ],
)
def test_gt_q_1(num: list[Union[int, float]], dst: float):
    res = _gt_q1(num)
    assert res == dst


@pytest.mark.parametrize(
    "num,dst",
    [
        ([1], 1.0),
        ([1, 1], 1.0),
        ([3, 2, 1], 3.0),
        ([1, 2, 3, 4], 4.0),
        ([1, 2, 2, 3, 4], 3.0),
        ([1, 2, 2, 3, 3, 3, 4, 4], 4.0),
        ([0.01, 0.5, 0.25, 1, 2, 2, 3, 3, 3, 4, 4], 3.0),
        ([-5, 0.1, 5], 5.0),
        ([1, 1, 1, 0.5, 1.2], 1.0),
        ([0, 2.1e15, 2342, 5.3e8, 0, -2343], 5.3e8),
    ],
)
def test_gt_q_3(num: list[Union[int, float]], dst: float):
    res = _gt_q3(num)
    assert res == dst


@pytest.mark.parametrize(
    "lst,dst",
    [
        ([1], [1]),
        ([1, 1.0], [1, 1.0]),
        ([3, 2.2, 1], [3, 2.2, 1]),
        ([3, 2.2, None, [None]], [3, 2.2, None, None]),
        ([1, 2, 3, [22, -3.4], 4], [1, 2, 3, 22, -3.4, 4]),
        ([1, 2.2, [9.2], 2.2, 3, 4, []], [1, 2.2, 9.2, 2.2, 3, 4]),
        ([[], 1.2, [], [], 2.2, [9.2], 2.2, [3, 4], []], [1.2, 2.2, 9.2, 2.2, 3, 4]),
        ([], []),
    ],
)
def test_flatten_list(lst: list[Any], dst: list[Any]):
    res = _flatten_list(lst)
    assert res == dst


@pytest.mark.parametrize(
    "lst,stat,dst",
    [
        ([1], "min", 1),
        ([1], "max", 1),
        ([[1]], "min", 1),
        ([[1]], "max", 1),
        ([1, 5.6], "min", 1),
        ([1, 5.6], "max", 5.6),
        ([1, None, 5.6], "min", 1),
        ([1, None, 5.6], "max", 5.6),
        ([[1], [3, 2, 3], [None], None, 0.5, 9.2], "min", 0.5),
        ([[1], [3, 2, 3], [None], None, 0.5, 9.2], "max", 9.2),
        ([[3, 2.2, 1], [3, 2.2, 1]], "min", 1),
        ([[3, 2.2, 1], [3, 2.2, 1]], "max", 3),
        ([[-13.2, 2.2, None, 14.3], [None, None]], "min", -13.2),
        ([[-13.2, 2.2, None, 14.3], [None, None]], "max", 14.3),
    ],
)
def test_get_extreme_value(lst: list[Any], stat: str, dst: list[Any]):
    res = _get_extreme_value(*lst, stat=stat)
    assert res == dst


@pytest.mark.parametrize(
    "num,keyword,dst",
    [
        ([1], "mean", 1),
        ([1], "median", 1),
        ([1], "min", 1),
        ([1], "max", 1),
        ([1], "q1", 1),
        ([1], "q3", 1),
        # ([1], "first", 1), # TODO: error results due to restrictive keyword check
        # ([1], "last", 1), # TODO: error results due to restrictive keyword check
        ([1, 5.6], "mean", 3.3),
        ([1, 5.6], "median", 3.3),
        ([1, 5.6], "min", 1),
        ([1, 5.6], "max", 5.6),
        ([1, 5.6], "q1", 1),
        ([1, 5.6], "q3", 5.6),
        # ([1, 5.6], "first", 1), # TODO: error results due to restrictive keyword check
        # ([1, 5.6], "last", 5.6), # TODO: error results due to restrictive keyword check
        (
            [-13.2, 2.2, 14.3, 2.3, 25.3, -3.1, 0, 3.93, 6.23, 0.92, -3.2],
            "mean",
            3.2436363636363637,
        ),
        ([-13.2, 2.2, 14.3, 2.3, 25.3, -3.1, 0, 3.93, 6.23, 0.92, -3.2], "median", 2.2),
        ([-13.2, 2.2, 14.3, 2.3, 25.3, -3.1, 0, 3.93, 6.23, 0.92, -3.2], "min", -13.2),
        ([-13.2, 2.2, 14.3, 2.3, 25.3, -3.1, 0, 3.93, 6.23, 0.92, -3.2], "max", 25.3),
        ([-13.2, 2.2, 14.3, 2.3, 25.3, -3.1, 0, 3.93, 6.23, 0.92, -3.2], "q1", -3.1),
        ([-13.2, 2.2, 14.3, 2.3, 25.3, -3.1, 0, 3.93, 6.23, 0.92, -3.2], "q3", 6.23),
        # TODO: errors below due to restrictive keyword check
        # ([-13.2, 2.2, 14.3, 2.3, 25.3, -3.1, 0, 3.93, 6.23, 0.92, -3.2], "first", -13.2),
        # ([-13.2, 2.2, 14.3, 2.3, 25.3, -3.1, 0, 3.93, 6.23, 0.92, -3.2], "last", -3.2),
    ],
)
def test_generate_ref_line_from_keyword(
    num: list[Union[int, float]], keyword: str, dst: Union[int, float]
):
    res = _generate_ref_line_from_keyword(num, keyword=keyword)
    assert res == dst


def _is_nanoplot_output(nanoplot_str: str):
    import re

    return bool(re.match("^<div><svg.*</svg></div>$", nanoplot_str))


def _nanoplot_has_tag_attrs(nanoplot_str: str, tag: str, attrs: list[tuple[str, str]]) -> bool:
    import re

    found: list[bool] = []

    for i, _ in enumerate(attrs):
        attrs_i = attrs[i]
        attr_str = f'{attrs_i[0]}="{attrs_i[1]}"'

        found_i = bool(re.search(f"<{tag}.*?{attr_str}.*?</{tag}>", nanoplot_str))

        found.append(found_i)

    return all(found)


#
# Tests of _generate_nanoplot() output
#


# Test case 1: Simple line-based nanoplot with no missing values and no additional options
def test_nanoplot_out_data_lines():
    out_data_lines = _generate_nanoplot(**CASES[0])

    assert _is_nanoplot_output(out_data_lines)

    assert _nanoplot_has_tag_attrs(
        out_data_lines,
        tag="pattern",
        attrs=[
            ("width", "8"),
            ("height", "8"),
            ("patternUnits", "userSpaceOnUse"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_data_lines,
        tag="path",
        attrs=[
            ("class", "area-closed"),
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill-opacity", "0.7"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_data_lines,
        tag="circle",
        attrs=[
            ("cx", "50.0"),
            ("cy", "115.0"),
            ("r", "10"),
            ("stroke", "#FFFFFF"),
            ("stroke-width", "4"),
            ("fill", "#FF0000"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_data_lines,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_data_lines,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_data_lines,
        tag="g",
        attrs=[
            ("class", "vert-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_data_lines,
        tag="g",
        attrs=[
            ("class", "y-axis-line"),
        ],
    )


# Test case 2: Line-based nanoplot w/ reference line (using static numeric value)
def test_nanoplot_out_with_num_ref_line():
    out_with_num_ref_line = _generate_nanoplot(**CASES[1])

    assert _is_nanoplot_output(out_with_num_ref_line)

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_line,
        tag="pattern",
        attrs=[
            ("width", "8"),
            ("height", "8"),
            ("patternUnits", "userSpaceOnUse"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_line,
        tag="path",
        attrs=[
            ("class", "area-closed"),
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill-opacity", "0.7"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_line,
        tag="circle",
        attrs=[
            ("cx", "50.0"),
            ("cy", "115.0"),
            ("r", "10"),
            ("stroke", "#FFFFFF"),
            ("stroke-width", "4"),
            ("fill", "#FF0000"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_line,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_line,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_line,
        tag="g",
        attrs=[
            ("class", "vert-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_line,
        tag="g",
        attrs=[
            ("class", "y-axis-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_line,
        tag="line",
        attrs=[
            ("class", "ref-line"),
            ("x1", "50.0"),
            ("x2", "550"),
            ("stroke", "#75A8B0"),
            ("stroke-width", "1"),
            ("stroke-dasharray", "4 3"),
            ("stroke-linecap", "round"),
            ("vector-effect", "non-scaling-stroke"),
        ],
    )


# Test case 3: Line-based nanoplot w/ reference line (using keyword to generate value)
def test_nanoplot_out_with_kword_ref_line():
    out_with_kword_ref_line = _generate_nanoplot(**CASES[2])

    assert _is_nanoplot_output(out_with_kword_ref_line)

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_line,
        tag="pattern",
        attrs=[
            ("width", "8"),
            ("height", "8"),
            ("patternUnits", "userSpaceOnUse"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_line,
        tag="path",
        attrs=[
            ("class", "area-closed"),
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill-opacity", "0.7"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_line,
        tag="circle",
        attrs=[
            ("cx", "50.0"),
            ("cy", "115.0"),
            ("r", "10"),
            ("stroke", "#FFFFFF"),
            ("stroke-width", "4"),
            ("fill", "#FF0000"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_line,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_line,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_line,
        tag="g",
        attrs=[
            ("class", "vert-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_line,
        tag="g",
        attrs=[
            ("class", "y-axis-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_line,
        tag="line",
        attrs=[
            ("class", "ref-line"),
            ("x1", "50.0"),
            ("x2", "550"),
            ("stroke", "#75A8B0"),
            ("stroke-width", "1"),
            ("stroke-dasharray", "4 3"),
            ("stroke-linecap", "round"),
            ("vector-effect", "non-scaling-stroke"),
        ],
    )


# Test case 4: Line nanoplot w/ ref area (using numbers to define limits)
def test_nanoplot_out_with_num_ref_area():
    out_with_num_ref_area = _generate_nanoplot(**CASES[3])

    assert _is_nanoplot_output(out_with_num_ref_area)

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_area,
        tag="pattern",
        attrs=[
            ("width", "8"),
            ("height", "8"),
            ("patternUnits", "userSpaceOnUse"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_area,
        tag="path",
        attrs=[
            ("class", "area-closed"),
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill-opacity", "0.7"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_area,
        tag="circle",
        attrs=[
            ("cx", "50.0"),
            ("cy", "115.0"),
            ("r", "10"),
            ("stroke", "#FFFFFF"),
            ("stroke-width", "4"),
            ("fill", "#FF0000"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_area,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_area,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_area,
        tag="g",
        attrs=[
            ("class", "vert-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_area,
        tag="g",
        attrs=[
            ("class", "y-axis-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_num_ref_area,
        tag="path",
        attrs=[
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill", "#A6E6F2"),
            ("fill-opacity", "0.8"),
        ],
    )


# Test case 5: Line nanoplot w/ ref area (using numbers, descending order, to define limits)
def test_nanoplot_out_with_num_ref_area_rev():
    out_with_num_ref_area_rev = _generate_nanoplot(**CASES[4])

    assert _is_nanoplot_output(out_with_num_ref_area_rev)

    assert out_with_num_ref_area_rev == _generate_nanoplot(**CASES[3])


# Test case 6: Line nanoplot w/ ref area (using two keywords to define limits)
def test_nanoplot_out_with_kword_ref_area():
    out_with_kword_ref_area = _generate_nanoplot(**CASES[5])

    assert _is_nanoplot_output(out_with_kword_ref_area)

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_area,
        tag="pattern",
        attrs=[
            ("width", "8"),
            ("height", "8"),
            ("patternUnits", "userSpaceOnUse"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_area,
        tag="path",
        attrs=[
            ("class", "area-closed"),
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill-opacity", "0.7"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_area,
        tag="circle",
        attrs=[
            ("cx", "50.0"),
            ("cy", "115.0"),
            ("r", "10"),
            ("stroke", "#FFFFFF"),
            ("stroke-width", "4"),
            ("fill", "#FF0000"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_area,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_area,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_area,
        tag="g",
        attrs=[
            ("class", "vert-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_area,
        tag="g",
        attrs=[
            ("class", "y-axis-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_kword_ref_area,
        tag="path",
        attrs=[
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill", "#A6E6F2"),
            ("fill-opacity", "0.8"),
        ],
    )


# Test case 7: Line nanoplot w/ ref area (using two keywords to define limits; reversed order)
def test_nanoplot_out_with_kword_ref_area_rev():
    out_with_kword_ref_area_rev = _generate_nanoplot(**CASES[6])

    assert _is_nanoplot_output(out_with_kword_ref_area_rev)

    assert out_with_kword_ref_area_rev == _generate_nanoplot(**CASES[5])


# Test case 8: Line nanoplot w/ ref area (using keywords + literal int value to define limits)
def test_nanoplot_out_with_mixed_ref_area_1():
    out_with_mixed_ref_area_1 = _generate_nanoplot(**CASES[7])

    assert _is_nanoplot_output(out_with_mixed_ref_area_1)

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_1,
        tag="pattern",
        attrs=[
            ("width", "8"),
            ("height", "8"),
            ("patternUnits", "userSpaceOnUse"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_1,
        tag="path",
        attrs=[
            ("class", "area-closed"),
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill-opacity", "0.7"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_1,
        tag="circle",
        attrs=[
            ("cx", "50.0"),
            ("cy", "115.0"),
            ("r", "10"),
            ("stroke", "#FFFFFF"),
            ("stroke-width", "4"),
            ("fill", "#FF0000"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_1,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_1,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_1,
        tag="g",
        attrs=[
            ("class", "vert-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_1,
        tag="g",
        attrs=[
            ("class", "y-axis-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_1,
        tag="path",
        attrs=[
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill", "#A6E6F2"),
            ("fill-opacity", "0.8"),
        ],
    )


# Test case 9: Line nanoplot w/ ref area (using keywords + literal int value to define limits)
def test_nanoplot_out_with_mixed_ref_area_2():
    out_with_mixed_ref_area_2 = _generate_nanoplot(**CASES[8])

    assert _is_nanoplot_output(out_with_mixed_ref_area_2)

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_2,
        tag="pattern",
        attrs=[
            ("width", "8"),
            ("height", "8"),
            ("patternUnits", "userSpaceOnUse"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_2,
        tag="path",
        attrs=[
            ("class", "area-closed"),
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill-opacity", "0.7"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_2,
        tag="circle",
        attrs=[
            ("cx", "50.0"),
            ("cy", "115.0"),
            ("r", "10"),
            ("stroke", "#FFFFFF"),
            ("stroke-width", "4"),
            ("fill", "#FF0000"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_2,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_2,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_2,
        tag="g",
        attrs=[
            ("class", "vert-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_2,
        tag="g",
        attrs=[
            ("class", "y-axis-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_mixed_ref_area_2,
        tag="path",
        attrs=[
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill", "#A6E6F2"),
            ("fill-opacity", "0.8"),
        ],
    )


# Test case 10: Line nanoplot w/ ref area and ref line
def test_nanoplot_out_with_ref_line_and_area():
    out_with_ref_line_and_area = _generate_nanoplot(**CASES[9])

    assert _is_nanoplot_output(out_with_ref_line_and_area)

    assert _nanoplot_has_tag_attrs(
        out_with_ref_line_and_area,
        tag="pattern",
        attrs=[
            ("width", "8"),
            ("height", "8"),
            ("patternUnits", "userSpaceOnUse"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_ref_line_and_area,
        tag="path",
        attrs=[
            ("class", "area-closed"),
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill-opacity", "0.7"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_ref_line_and_area,
        tag="circle",
        attrs=[
            ("cx", "50.0"),
            ("cy", "115.0"),
            ("r", "10"),
            ("stroke", "#FFFFFF"),
            ("stroke-width", "4"),
            ("fill", "#FF0000"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_ref_line_and_area,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_ref_line_and_area,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_ref_line_and_area,
        tag="g",
        attrs=[
            ("class", "vert-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_ref_line_and_area,
        tag="g",
        attrs=[
            ("class", "y-axis-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_ref_line_and_area,
        tag="path",
        attrs=[
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill", "#A6E6F2"),
            ("fill-opacity", "0.8"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_with_ref_line_and_area,
        tag="line",
        attrs=[
            ("class", "ref-line"),
            ("x1", "50.0"),
            ("x2", "550"),
            ("stroke", "#75A8B0"),
            ("stroke-width", "1"),
            ("stroke-dasharray", "4 3"),
            ("stroke-linecap", "round"),
            ("vector-effect", "non-scaling-stroke"),
        ],
    )


# Test case 11: Simple bar-based nanoplot
def test_nanoplot_out_data_bars():
    out_data_bars = _generate_nanoplot(**CASES[10])

    assert _is_nanoplot_output(out_data_bars)

    assert _nanoplot_has_tag_attrs(
        out_data_bars,
        tag="rect",
        attrs=[
            ("x", "30.0"),
            ("width", "40"),
            ("height", "27.179487179487168"),
            ("stroke", "#CC3243"),
            ("stroke-width", "4"),
            ("fill", "#D75A68"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_data_bars,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_data_bars,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )


# Test case 12: Bar nanoplot with a reference line (static numeric value)
def test_nanoplot_out_bars_with_num_ref_line():
    out_bars_with_num_ref_line = _generate_nanoplot(**CASES[11])

    assert _is_nanoplot_output(out_bars_with_num_ref_line)

    assert _nanoplot_has_tag_attrs(
        out_bars_with_num_ref_line,
        tag="rect",
        attrs=[
            ("x", "30.0"),
            ("width", "40"),
            ("height", "27.179487179487168"),
            ("stroke", "#CC3243"),
            ("stroke-width", "4"),
            ("fill", "#D75A68"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_num_ref_line,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_num_ref_line,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_num_ref_line,
        tag="line",
        attrs=[
            ("class", "ref-line"),
            ("x1", "50.0"),
            ("x2", "550"),
            ("stroke", "#75A8B0"),
            ("stroke-width", "1"),
            ("stroke-dasharray", "4 3"),
            ("stroke-linecap", "round"),
            ("vector-effect", "non-scaling-stroke"),
        ],
    )


# Test case 13: Bar nanoplot with a reference line (keyword to generate value)
def test_nanoplot_out_bars_with_kword_ref_line():
    out_bars_with_kword_ref_line = _generate_nanoplot(**CASES[12])

    assert _is_nanoplot_output(out_bars_with_kword_ref_line)

    assert _nanoplot_has_tag_attrs(
        out_bars_with_kword_ref_line,
        tag="rect",
        attrs=[
            ("x", "30.0"),
            ("width", "40"),
            ("height", "27.179487179487168"),
            ("stroke", "#CC3243"),
            ("stroke-width", "4"),
            ("fill", "#D75A68"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_kword_ref_line,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_kword_ref_line,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_kword_ref_line,
        tag="line",
        attrs=[
            ("class", "ref-line"),
            ("x1", "50.0"),
            ("x2", "550"),
            ("stroke", "#75A8B0"),
            ("stroke-width", "1"),
            ("stroke-dasharray", "4 3"),
            ("stroke-linecap", "round"),
            ("vector-effect", "non-scaling-stroke"),
        ],
    )


# Test case 14: Bar nanoplot with a reference area (using numbers to define limits)
def test_nanoplot_out_bars_with_num_ref_area():
    out_bars_with_num_ref_area = _generate_nanoplot(**CASES[13])

    assert _is_nanoplot_output(out_bars_with_num_ref_area)

    assert _nanoplot_has_tag_attrs(
        out_bars_with_num_ref_area,
        tag="rect",
        attrs=[
            ("x", "30.0"),
            ("width", "40"),
            ("height", "27.179487179487168"),
            ("stroke", "#CC3243"),
            ("stroke-width", "4"),
            ("fill", "#D75A68"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_num_ref_area,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_num_ref_area,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_num_ref_area,
        tag="path",
        attrs=[
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill", "#A6E6F2"),
            ("fill-opacity", "0.8"),
        ],
    )


# Test case 15: Bar nanoplot with a reference area (using keywords)
def test_nanoplot_out_bars_with_kword_ref_area():
    out_bars_with_kword_ref_area = _generate_nanoplot(**CASES[14])

    assert _is_nanoplot_output(out_bars_with_kword_ref_area)

    assert _nanoplot_has_tag_attrs(
        out_bars_with_kword_ref_area,
        tag="rect",
        attrs=[
            ("x", "30.0"),
            ("width", "40"),
            ("height", "27.179487179487168"),
            ("stroke", "#CC3243"),
            ("stroke-width", "4"),
            ("fill", "#D75A68"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_kword_ref_area,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_kword_ref_area,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_kword_ref_area,
        tag="path",
        attrs=[
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill", "#A6E6F2"),
            ("fill-opacity", "0.8"),
        ],
    )


# Test case 16: Bar nanoplot with a reference area (using keyword + literal int value)
def test_nanoplot_out_bars_with_mixed_ref_area_1():
    out_bars_with_mixed_ref_area_1 = _generate_nanoplot(**CASES[15])

    assert _is_nanoplot_output(out_bars_with_mixed_ref_area_1)

    assert _nanoplot_has_tag_attrs(
        out_bars_with_mixed_ref_area_1,
        tag="rect",
        attrs=[
            ("x", "30.0"),
            ("width", "40"),
            ("height", "27.179487179487168"),
            ("stroke", "#CC3243"),
            ("stroke-width", "4"),
            ("fill", "#D75A68"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_mixed_ref_area_1,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_mixed_ref_area_1,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_mixed_ref_area_1,
        tag="path",
        attrs=[
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill", "#A6E6F2"),
            ("fill-opacity", "0.8"),
        ],
    )


# Test case 17: Bar nanoplot with a reference area (using keyword + literal float value)
def test_nanoplot_out_bars_with_mixed_ref_area_2():
    out_bars_with_mixed_ref_area_2 = _generate_nanoplot(**CASES[16])

    assert _is_nanoplot_output(out_bars_with_mixed_ref_area_2)

    assert _nanoplot_has_tag_attrs(
        out_bars_with_mixed_ref_area_2,
        tag="rect",
        attrs=[
            ("x", "30.0"),
            ("width", "40"),
            ("height", "27.179487179487168"),
            ("stroke", "#CC3243"),
            ("stroke-width", "4"),
            ("fill", "#D75A68"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_mixed_ref_area_2,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_mixed_ref_area_2,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_mixed_ref_area_2,
        tag="path",
        attrs=[
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill", "#A6E6F2"),
            ("fill-opacity", "0.8"),
        ],
    )


# Test case 18: Bar nanoplot with a reference line and area
def test_nanoplot_out_bars_with_ref_line_and_area():
    out_bars_with_ref_line_and_area = _generate_nanoplot(**CASES[17])

    assert _is_nanoplot_output(out_bars_with_ref_line_and_area)

    assert _nanoplot_has_tag_attrs(
        out_bars_with_ref_line_and_area,
        tag="rect",
        attrs=[
            ("x", "30.0"),
            ("width", "40"),
            ("height", "27.179487179487168"),
            ("stroke", "#CC3243"),
            ("stroke-width", "4"),
            ("fill", "#D75A68"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_ref_line_and_area,
        tag="rect",
        attrs=[
            ("x", "0"),
            ("y", "0"),
            ("width", "65"),
            ("height", "130"),
            ("stroke", "transparent"),
            ("stroke-width", "0"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_ref_line_and_area,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_ref_line_and_area,
        tag="path",
        attrs=[
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill", "#A6E6F2"),
            ("fill-opacity", "0.8"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_bars_with_ref_line_and_area,
        tag="line",
        attrs=[
            ("class", "ref-line"),
            ("x1", "50.0"),
            ("x2", "550"),
            ("stroke", "#75A8B0"),
            ("stroke-width", "1"),
            ("stroke-dasharray", "4 3"),
            ("stroke-linecap", "round"),
            ("vector-effect", "non-scaling-stroke"),
        ],
    )


# Test case 19: Horizontal line-based nanoplot
def test_nanoplot_out_horizontal_line():
    out_horizontal_line = _generate_nanoplot(**CASES[18])

    assert _is_nanoplot_output(out_horizontal_line)

    assert _nanoplot_has_tag_attrs(
        out_horizontal_line,
        tag="line",
        attrs=[
            ("x1", "0.0"),
            ("y1", "65.0"),
            ("stroke", "#4682B4"),
            ("stroke-width", "8"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_horizontal_line,
        tag="g",
        attrs=[
            ("class", "horizontal-line"),
        ],
    )


# Test case 20: Horizontal line-based nanoplot with value not in `vals` list
def test_nanoplot_out_horizontal_line_non_incl():
    out_horizontal_line_non_incl = _generate_nanoplot(**CASES[19])

    assert _is_nanoplot_output(out_horizontal_line_non_incl)

    assert _nanoplot_has_tag_attrs(
        out_horizontal_line_non_incl,
        tag="line",
        attrs=[
            ("stroke", "#4682B4"),
            ("stroke-width", "8"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        out_horizontal_line_non_incl,
        tag="g",
        attrs=[
            ("class", "horizontal-line"),
        ],
    )


# Test case 21: Horizontal bar-based nanoplot
def test_nanoplot_out_horizontal_bar():
    out_horizontal_bar = _generate_nanoplot(**CASES[20])

    assert _is_nanoplot_output(out_horizontal_bar)

    assert _nanoplot_has_tag_attrs(
        out_horizontal_bar,
        tag="svg",
        attrs=[
            ("role", "img"),
            ("viewBox", "0 0 600 130"),
        ],
    )


# Test case 22: Horizontal bar-based nanoplot with value not in `vals` list
def test_nanoplot_out_horizontal_bar_non_incl():
    out_horizontal_bar_non_incl = _generate_nanoplot(**CASES[21])

    assert _is_nanoplot_output(out_horizontal_bar_non_incl)

    assert _nanoplot_has_tag_attrs(
        out_horizontal_bar_non_incl,
        tag="svg",
        attrs=[
            ("role", "img"),
            ("viewBox", "0 0 600 130"),
        ],
    )


# Test case 23: Line-based nanoplot with x-values
def test_nanoplot_out_data_lines_x_vals():
    out_data_lines_x_vals = _generate_nanoplot(**CASES[22])
    assert _is_nanoplot_output(out_data_lines_x_vals)


# Test case 24: Line-based nanoplot with no x-values (generates an empty string)
def test_nanoplot_out_data_lines_x_vals_empty():
    out_data_lines_x_vals_empty = _generate_nanoplot(**CASES[23])
    assert out_data_lines_x_vals_empty == ""


def test_nanoplot_x_y_vals_diff_length():
    with pytest.raises(ValueError):
        _generate_nanoplot(y_vals=[5.3, 6.3, 7.2], x_vals=[1, 2.5])


@pytest.mark.xfail
def test_nanoplot_unknown_plot_type():
    with pytest.raises(ValueError):
        _generate_nanoplot(y_vals=[1, 2, 3], plot_type="unknown")


@pytest.mark.parametrize(
    "n, bool_",
    [
        (0, True),
        (0.0, True),
        (1, True),
        (1.0, True),
        (-12, True),
        (-12.0, True),
        ("-12", True),
        ("−12", True),  # not regular `-`
        (Decimal("1"), True),
        (Decimal("1.0"), True),
        (2.151515, False),
        (-12.49849, False),
        ("-12.49849", False),
        ("−12.49849", False),  # not regular `-`
        (Decimal("2.151515"), False),
        ("abc", False),
        (["abc"], False),
        (tuple("abc"), False),
        (set("abc"), False),
        (dict.fromkeys("abc", object), False),
    ],
)
def test_is_intlike(n: Any, bool_: bool):
    assert _is_intlike(n) is bool_


@pytest.mark.parametrize(
    "nums, n",
    [
        (["1.0", 2.0, 3.00, Decimal(4), "-5.0"], 5),
        (["1.1", 2.2, 3.03, "abc", "−12.49849"], 0),  # not regular `-`
    ],
)
def test_get_n_intlike(nums: list[Any], n: int):
    assert _get_n_intlike(nums) == n


@pytest.mark.parametrize(
    "n, result",
    [
        ("1.0", "1"),
        (2.0, "2"),
        (3.00, "3"),
        (Decimal(4), "4"),
        ("-5.0", "-5"),
        ("−5.0", "-5"),  # not regular `-`
        ("-7.04K", "-7.04K"),  # not regular `-`
    ],
)
def test_remove_exponent(n: "int | float | str", result: int):
    assert _remove_exponent(n) == result


def test_noerror_list_of_strings() -> None:
    random_numbers_df = pl.DataFrame(
        {
            "example": ["Row " + str(x) for x in range(1, 5)],
            "numbers": [
                "20 23 6",
                "2.3 6.8 9.2",
                "-12 -5 6",
                "2 0 15",
            ],
        }
    )

    GT(random_numbers_df).fmt_nanoplot(
        columns="numbers",
        options=nanoplot_options(
            data_point_radius=5,
            data_point_stroke_color=["black", "red", "black"],
            show_data_area=False,
        ),
    )
