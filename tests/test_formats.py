import re
from typing import Any, Union

import pandas as pd
import polars as pl
import pytest
import sys
from great_tables import GT, _locale
from great_tables._data_color.base import _html_color
from great_tables._formats import (
    FmtImage,
    _expand_exponential_to_full_string,
    _format_number_n_sigfig,
    _format_number_fixed_decimals,
    _get_currency_str,
    _get_locale_currency_code,
    _get_locale_dec_mark,
    _get_locale_sep_mark,
    _normalize_locale,
    _validate_locale,
    fmt,
)
from great_tables._utils_render_html import create_body_component_h
from great_tables.data import exibble
from great_tables.gt import _get_column_of_values


def assert_rendered_body(snapshot, gt):
    built = gt._build_data("html")
    body = create_body_component_h(built)

    assert snapshot == body


def assert_repr_html(snapshot, gt):
    body = gt._repr_html_()
    body = re.sub(r"^.*?<table (.*?)</table>.*$", r"\1", body, flags=re.DOTALL)

    assert snapshot == body


def strip_windows_drive(x):
    # this is a hacky approach to ensuring fmt_image path tests succeed
    # on our windows build. On linux root is just "/". On windows its a
    # drive name. Assumes our windows runner uses D:\
    return x.replace('src="D:\\', 'src="/')


def test_format_fns():
    df = pd.DataFrame({"x": [1, 2]})
    gt = GT(df)
    new_gt = fmt(gt, fns=lambda x: str(x + 1), columns=["x"])

    formats_fn = new_gt._formats[0]

    res = list(map(formats_fn.func.default, df["x"]))
    assert res == ["2", "3"]


def test_format_multi_fns():
    df = pd.DataFrame({"x": [1, 2]})
    gt = GT(df)
    new_gt = fmt(gt, fns=[lambda x: str(x + 1), lambda x: str(x + 2)], columns=["x"])

    formats_fn = new_gt._formats[0]

    res = list(map(formats_fn.func.default, df["x"]))
    assert res == ["2", "3"]

    formats_fn = new_gt._formats[1]

    res = list(map(formats_fn.func.default, df["x"]))
    assert res == ["3", "4"]


def test_format_snap(snapshot):
    new_gt = (
        GT(exibble)
        .fmt_currency(columns="currency")
        .fmt_scientific(columns="num")
        .fmt_date(columns="date", date_style="day_month_year")
    )

    assert_rendered_body(snapshot, new_gt)


def test_format_repr_snap(snapshot):
    new_gt = (
        GT(exibble)
        .fmt_currency(columns="currency")
        .fmt_scientific(columns="num")
        .fmt_date(columns="date", date_style="day_month_year")
    )

    assert_repr_html(snapshot, new_gt)


@pytest.mark.parametrize("expr", [[0, -1], pl.selectors.exclude("y")])
def test_format_col_selection_multi(expr: Any):
    df = pd.DataFrame({"x": [1], "y": [2], "z": [3]})

    if isinstance(expr, pl.Expr):
        gt = GT(pl.from_pandas(df))
    else:
        gt = GT(df)

    res = gt.fmt(lambda x: x, columns=expr, rows=None)
    assert len(res._formats) == 1
    assert res._formats[0].cells.cols == ["x", "z"]


@pytest.mark.parametrize("expr", [1, pl.selectors.by_name("y"), "y"])
def test_formt_col_selection_single(expr: Any):
    df = pd.DataFrame({"x": [1], "y": [2], "z": [3]})

    if isinstance(expr, pl.Expr):
        gt = GT(pl.from_pandas(df))
    else:
        gt = GT(df)

    res = gt.fmt(lambda x: x, columns=expr, rows=None)
    assert len(res._formats) == 1
    assert res._formats[0].cells.cols == ["y"]


@pytest.mark.parametrize(
    "expr",
    [
        [1, 2],
        pl.col("x") > 0,
        lambda D: D["x"] > 0,
    ],
)
def test_format_row_selection(expr):
    df = pd.DataFrame({"x": [0, 1, 2]})

    if isinstance(expr, pl.Expr):
        gt = GT(pl.from_pandas(df))
    else:
        gt = GT(df)

    res = gt.fmt(lambda x: x, columns=[], rows=expr)
    assert len(res._formats) == 1
    assert res._formats[0].cells.rows == [1, 2]


@pytest.mark.parametrize(
    "scale_values,placement,incl_space,force_sign,x_out",
    [
        (
            True,
            "right",
            False,
            False,
            [
                "0.05%",
                "0.46%",
                "4.56%",
                "45.60%",
                "456.00%",
                "4,560.00%",
                "45,600.00%",
                "\u2212" + "4.68%",
                "0.00%",
            ],
        ),
        (
            False,
            "right",
            False,
            False,
            [
                "0.00%",
                "0.00%",
                "0.05%",
                "0.46%",
                "4.56%",
                "45.60%",
                "456.00%",
                "\u2212" + "0.05%",
                "0.00%",
            ],
        ),
        (
            False,
            "left",
            False,
            False,
            [
                "%0.00",
                "%0.00",
                "%0.05",
                "%0.46",
                "%4.56",
                "%45.60",
                "%456.00",
                "\u2212" + "%0.05",
                "%0.00",
            ],
        ),
        (
            False,
            "right",
            True,
            False,
            [
                "0.00 %",
                "0.00 %",
                "0.05 %",
                "0.46 %",
                "4.56 %",
                "45.60 %",
                "456.00 %",
                "\u2212" + "0.05 %",
                "0.00 %",
            ],
        ),
        (
            False,
            "left",
            True,
            False,
            [
                "% 0.00",
                "% 0.00",
                "% 0.05",
                "% 0.46",
                "% 4.56",
                "% 45.60",
                "% 456.00",
                "\u2212" + "% 0.05",
                "% 0.00",
            ],
        ),
        (
            False,
            "left",
            True,
            True,
            [
                "+% 0.00",
                "+% 0.00",
                "+% 0.05",
                "+% 0.46",
                "+% 4.56",
                "+% 45.60",
                "+% 456.00",
                "\u2212" + "% 0.05",
                "% 0.00",
            ],
        ),
        (
            False,
            "left",
            False,
            True,
            [
                "+%0.00",
                "+%0.00",
                "+%0.05",
                "+%0.46",
                "+%4.56",
                "+%45.60",
                "+%456.00",
                "\u2212" + "%0.05",
                "%0.00",
            ],
        ),
        (
            False,
            "right",
            True,
            True,
            [
                "+0.00 %",
                "+0.00 %",
                "+0.05 %",
                "+0.46 %",
                "+4.56 %",
                "+45.60 %",
                "+456.00 %",
                "\u2212" + "0.05 %",
                "0.00 %",
            ],
        ),
        (
            False,
            "right",
            False,
            True,
            [
                "+0.00%",
                "+0.00%",
                "+0.05%",
                "+0.46%",
                "+4.56%",
                "+45.60%",
                "+456.00%",
                "\u2212" + "0.05%",
                "0.00%",
            ],
        ),
    ],
)
def test_fmt_percent_basic_0(
    scale_values: bool, placement: str, incl_space: bool, force_sign: bool, x_out: str
):
    df = pd.DataFrame({"x": [0.000456, 0.00456, 0.0456, 0.456, 4.56, 45.6, 456, -0.0468, 0]})

    # Expect that values in `x` are formatted correctly when varying the
    # number of fixed decimal places (`decimals`)
    gt = GT(df).fmt_percent(
        columns="x",
        scale_values=scale_values,
        force_sign=force_sign,
        placement=placement,
        incl_space=incl_space,
    )
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == x_out


@pytest.mark.parametrize(
    "decimals,x_out",
    [
        (0, ["1", "1", "1", "1", "1", "1", "1", "1", "1"]),
        (1, ["1.0", "1.2", "1.2", "1.2", "1.2", "1.2", "1.2", "1.2", "1.2"]),
        (2, ["1.00", "1.20", "1.23", "1.23", "1.23", "1.23", "1.23", "1.23", "1.23"]),
        (3, ["1.000", "1.200", "1.230", "1.234", "1.234", "1.235", "1.235", "1.235", "1.235"]),
        (
            4,
            [
                "1.0000",
                "1.2000",
                "1.2300",
                "1.2340",
                "1.2345",
                "1.2346",
                "1.2346",
                "1.2346",
                "1.2346",
            ],
        ),
        (
            5,
            [
                "1.00000",
                "1.20000",
                "1.23000",
                "1.23400",
                "1.23450",
                "1.23456",
                "1.23457",
                "1.23457",
                "1.23457",
            ],
        ),
        (
            6,
            [
                "1.000000",
                "1.200000",
                "1.230000",
                "1.234000",
                "1.234500",
                "1.234560",
                "1.234567",
                "1.234568",
                "1.234568",
            ],
        ),
        (
            7,
            [
                "1.0000000",
                "1.2000000",
                "1.2300000",
                "1.2340000",
                "1.2345000",
                "1.2345600",
                "1.2345670",
                "1.2345678",
                "1.2345679",
            ],
        ),
        (
            8,
            [
                "1.00000000",
                "1.20000000",
                "1.23000000",
                "1.23400000",
                "1.23450000",
                "1.23456000",
                "1.23456700",
                "1.23456780",
                "1.23456789",
            ],
        ),
        (
            9,
            [
                "1.000000000",
                "1.200000000",
                "1.230000000",
                "1.234000000",
                "1.234500000",
                "1.234560000",
                "1.234567000",
                "1.234567800",
                "1.234567890",
            ],
        ),
    ],
)
def test_fmt_number_basic_0(decimals: int, x_out: str):
    df = pd.DataFrame(
        {
            "x": [
                1,
                1.2,
                1.23,
                1.234,
                1.2345,
                1.23456,
                1.234567,
                1.2345678,
                1.23456789,
            ]
        }
    )

    # Expect that values in `x` are formatted correctly when varying the
    # number of fixed decimal places (`decimals`)
    gt = GT(df).fmt_number(columns="x", decimals=decimals)
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == x_out


@pytest.mark.parametrize(
    "decimals,x_out",
    [
        (0, ["0", "0", "0", "0", "0", "0", "0", "0", "0"]),
        (1, ["0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0"]),
        (2, ["0.00", "0.00", "0.00", "0.00", "0.00", "0.00", "0.00", "0.00", "0.00"]),
        (
            3,
            [
                "0.000",
                "0.000",
                "0.000",
                "0.000",
                "0.000",
                "0.000",
                "0.000",
                "0.000",
                "0.000",
            ],
        ),
        (
            4,
            [
                "0.0000",
                "0.0000",
                "0.0000",
                "0.0000",
                "0.0000",
                "0.0000",
                "0.0000",
                "0.0000",
                "0.0000",
            ],
        ),
        (
            5,
            [
                "0.00000",
                "0.00000",
                "0.00000",
                "0.00000",
                "0.00000",
                "0.00000",
                "0.00000",
                "0.00000",
                "0.00000",
            ],
        ),
        (
            6,
            [
                "0.000001",
                "0.000001",
                "0.000001",
                "0.000001",
                "0.000001",
                "0.000001",
                "0.000001",
                "0.000001",
                "0.000001",
            ],
        ),
        (
            7,
            [
                "0.0000010",
                "0.0000012",
                "0.0000012",
                "0.0000012",
                "0.0000012",
                "0.0000012",
                "0.0000012",
                "0.0000012",
                "0.0000012",
            ],
        ),
        (
            8,
            [
                "0.00000100",
                "0.00000120",
                "0.00000123",
                "0.00000123",
                "0.00000123",
                "0.00000123",
                "0.00000123",
                "0.00000123",
                "0.00000123",
            ],
        ),
        (
            9,
            [
                "0.000001000",
                "0.000001200",
                "0.000001230",
                "0.000001234",
                "0.000001234",
                "0.000001235",
                "0.000001235",
                "0.000001235",
                "0.000001235",
            ],
        ),
    ],
)
def test_fmt_number_basic_1(decimals: int, x_out: str):
    df = pd.DataFrame(
        {
            "x": [
                0.000001,
                0.0000012,
                0.00000123,
                0.000001234,
                0.0000012345,
                0.00000123456,
                0.000001234567,
                0.0000012345678,
                0.00000123456789,
            ]
        }
    )

    # Expect that the smaller values in `x` are formatted correctly when
    # varying the number of fixed decimal places (`decimals`)
    gt = GT(df).fmt_number(columns="x", decimals=decimals)
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == x_out


@pytest.mark.parametrize(
    "n_sigfig,x_out",
    [
        (
            1,
            [
                "0.000001",
                "0.000001",
                "0.000001",
                "0.000001",
                "0.000001",
                "100,000",
                "100,000",
                "100,000",
                "100,000",
                "100,000",
            ],
        ),
        (
            2,
            [
                "0.0000010",
                "0.0000012",
                "0.0000012",
                "0.0000012",
                "0.0000012",
                "120,000",
                "120,000",
                "120,000",
                "120,000",
                "120,000",
            ],
        ),
        (
            3,
            [
                "0.00000100",
                "0.00000120",
                "0.00000123",
                "0.00000123",
                "0.00000123",
                "123,000",
                "123,000",
                "123,000",
                "123,000",
                "123,000",
            ],
        ),
        (
            4,
            [
                "0.000001000",
                "0.000001200",
                "0.000001230",
                "0.000001234",
                "0.000001234",
                "123,400",
                "123,500",
                "123,500",
                "123,500",
                "123,500",
            ],
        ),
        (
            5,
            [
                "0.0000010000",
                "0.0000012000",
                "0.0000012300",
                "0.0000012340",
                "0.0000012345",
                "123,450",
                "123,460",
                "123,460",
                "123,460",
                "123,460",
            ],
        ),
        (
            6,
            [
                "0.00000100000",
                "0.00000120000",
                "0.00000123000",
                "0.00000123400",
                "0.00000123450",
                "123,450",
                "123,457",
                "123,457",
                "123,457",
                "123,457",
            ],
        ),
        (
            7,
            [
                "0.000001000000",
                "0.000001200000",
                "0.000001230000",
                "0.000001234000",
                "0.000001234500",
                "123,450.0",
                "123,456.7",
                "123,456.8",
                "123,456.8",
                "123,456.8",
            ],
        ),
        (
            8,
            [
                "0.0000010000000",
                "0.0000012000000",
                "0.0000012300000",
                "0.0000012340000",
                "0.0000012345000",
                "123,450.00",
                "123,456.70",
                "123,456.76",
                "123,456.76",
                "123,456.77",
            ],
        ),
        (
            9,
            [
                "0.00000100000000",
                "0.00000120000000",
                "0.00000123000000",
                "0.00000123400000",
                "0.00000123450000",
                "123,450.000",
                "123,456.700",
                "123,456.760",
                "123,456.765",
                "123,456.765",
            ],
        ),
        (
            10,
            [
                "0.000001000000000",
                "0.000001200000000",
                "0.000001230000000",
                "0.000001234000000",
                "0.000001234500000",
                "123,450.0000",
                "123,456.7000",
                "123,456.7600",
                "123,456.7650",
                "123,456.7654",
            ],
        ),
        (
            11,
            [
                "0.0000010000000000",
                "0.0000012000000000",
                "0.0000012300000000",
                "0.0000012340000000",
                "0.0000012345000000",
                "123,450.00000",
                "123,456.70000",
                "123,456.76000",
                "123,456.76500",
                "123,456.76540",
            ],
        ),
        (
            12,
            [
                "0.00000100000000000",
                "0.00000120000000000",
                "0.00000123000000000",
                "0.00000123400000000",
                "0.00000123450000000",
                "123,450.000000",
                "123,456.700000",
                "123,456.760000",
                "123,456.765000",
                "123,456.765400",
            ],
        ),
    ],
)
def test_fmt_number_n_sigfig(n_sigfig: int, x_out: str):
    df = pd.DataFrame(
        {
            "x": [
                0.000001,
                0.0000012,
                0.00000123,
                0.000001234,
                0.0000012345,
                123450,
                123456.7,
                123456.76,
                123456.765,
                123456.7654,
            ]
        }
    )

    # Expect that values in `x` are formatted correctly when varying the
    # number of significant digits (`n_sigfig`)
    gt = GT(df).fmt_number(columns="x", n_sigfig=n_sigfig)
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == x_out


# TODO: Expect that the `drop_trailing_zeros` argument is ignored when formatting
# to a fixed number of signficant digits


@pytest.mark.parametrize(
    "decimals,drop_trailing_zeros,drop_trailing_dec_mark,x_out",
    [
        (0, False, False, ["1.", "2."]),
        (0, False, True, ["1", "2"]),
        (0, True, False, ["1.", "2."]),
        (0, True, True, ["1", "2"]),
        (1, False, False, ["1.2", "2.3"]),
        (1, False, True, ["1.2", "2.3"]),
        (1, True, False, ["1.2", "2.3"]),
        (1, True, True, ["1.2", "2.3"]),
        (2, False, False, ["1.23", "2.35"]),
        (2, False, True, ["1.23", "2.35"]),
        (2, True, False, ["1.23", "2.35"]),
        (2, True, True, ["1.23", "2.35"]),
        (3, False, False, ["1.230", "2.345"]),
        (3, False, True, ["1.230", "2.345"]),
        (3, True, False, ["1.23", "2.345"]),
        (3, True, True, ["1.23", "2.345"]),
        (4, False, False, ["1.2300", "2.3450"]),
        (4, False, True, ["1.2300", "2.3450"]),
        (4, True, False, ["1.23", "2.345"]),
        (4, True, True, ["1.23", "2.345"]),
        (5, False, False, ["1.23000", "2.34500"]),
        (5, False, True, ["1.23000", "2.34500"]),
        (5, True, False, ["1.23", "2.345"]),
        (5, True, True, ["1.23", "2.345"]),
        (10, False, False, ["1.2300000000", "2.3450000000"]),
        (10, False, True, ["1.2300000000", "2.3450000000"]),
        (10, True, False, ["1.23", "2.345"]),
        (10, True, True, ["1.23", "2.345"]),
        # (20, False, False, ["1.23000000000000000000", "2.34500000000000000000"]), # <- doesn't work
        # (20, False, True, ["1.23000000000000000000", "2.34500000000000000000"]), # <- doesn't work
        # (20, True, False, ["1.23", "2.345"]), # <- doesn't work
        # (20, True, True, ["1.23", "2.345"]), # <- doesn't work
    ],
)
def test_fmt_number_drop_trailing_00(
    decimals: int, drop_trailing_zeros: bool, drop_trailing_dec_mark: bool, x_out: str
):
    df = pd.DataFrame({"x": [1.23, 2.345]})

    gt = GT(df).fmt_number(
        columns="x",
        decimals=decimals,
        drop_trailing_zeros=drop_trailing_zeros,
        drop_trailing_dec_mark=drop_trailing_dec_mark,
    )
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == x_out


@pytest.mark.parametrize(
    "n_sigfig,drop_trailing_zeros,drop_trailing_dec_mark,x_out",
    [
        (1, False, False, ["1.", "2."]),
        (1, False, True, ["1", "2"]),
        (1, True, False, ["1.", "2."]),
        (1, True, True, ["1", "2"]),
        (2, False, False, ["1.2", "2.3"]),
        (2, False, True, ["1.2", "2.3"]),
        (2, True, False, ["1.2", "2.3"]),
        (2, True, True, ["1.2", "2.3"]),
        (3, False, False, ["1.23", "2.35"]),
        (3, False, True, ["1.23", "2.35"]),
        (3, True, False, ["1.23", "2.35"]),
        (3, True, True, ["1.23", "2.35"]),
    ],
)
def test_fmt_number_drop_trailing_01(
    n_sigfig: int, drop_trailing_zeros: bool, drop_trailing_dec_mark: bool, x_out: str
):
    df = pd.DataFrame({"x": [1.23, 2.345]})

    gt = GT(df).fmt_number(
        columns="x",
        n_sigfig=n_sigfig,
        drop_trailing_zeros=drop_trailing_zeros,
        drop_trailing_dec_mark=drop_trailing_dec_mark,
    )
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == x_out


@pytest.mark.parametrize(
    "n_sigfig,use_seps,sep_mark,dec_mark,x_out",
    [
        (1, True, ",", ".", ["1,000,000", "\u2212" + "5,000"]),
        (1, True, ".", ",", ["1.000.000", "\u2212" + "5.000"]),
        (1, True, "  ", "/", ["1  000  000", "\u2212" + "5  000"]),
        (1, True, "", "", ["1000000", "\u2212" + "5000"]),
        (1, False, ",", ".", ["1000000", "\u2212" + "5000"]),
        (1, False, ".", ",", ["1000000", "\u2212" + "5000"]),
        (1, False, "  ", "/", ["1000000", "\u2212" + "5000"]),
        (1, False, "", "", ["1000000", "\u2212" + "5000"]),
        (3, True, ",", ".", ["1,230,000", "\u2212" + "5,430"]),
        (3, True, ".", ",", ["1.230.000", "\u2212" + "5.430"]),
        (3, True, "  ", "/", ["1  230  000", "\u2212" + "5  430"]),
        (3, True, "", "", ["1230000", "\u2212" + "5430"]),
        (3, False, ",", ".", ["1230000", "\u2212" + "5430"]),
        (3, False, ".", ",", ["1230000", "\u2212" + "5430"]),
        (3, False, "  ", "/", ["1230000", "\u2212" + "5430"]),
        (3, False, "", "", ["1230000", "\u2212" + "5430"]),
        (5, True, ",", ".", ["1,234,600", "\u2212" + "5,432.4"]),
        (5, True, ".", ",", ["1.234.600", "\u2212" + "5.432,4"]),
        (5, True, "  ", "/", ["1  234  600", "\u2212" + "5  432/4"]),
        (5, True, "", "", ["1234600", "\u2212" + "54324"]),
        (5, False, ",", ".", ["1234600", "\u2212" + "5432.4"]),
        (5, False, ".", ",", ["1234600", "\u2212" + "5432,4"]),
        (5, False, "  ", "/", ["1234600", "\u2212" + "5432/4"]),
        (5, False, "", "", ["1234600", "\u2212" + "54324"]),
        (7, True, ",", ".", ["1,234,567", "\u2212" + "5,432.370"]),
        (7, True, ".", ",", ["1.234.567", "\u2212" + "5.432,370"]),
        (7, True, "  ", "/", ["1  234  567", "\u2212" + "5  432/370"]),
        (7, True, "", "", ["1234567", "\u2212" + "5432370"]),
        (7, False, ",", ".", ["1234567", "\u2212" + "5432.370"]),
        (7, False, ".", ",", ["1234567", "\u2212" + "5432,370"]),
        (7, False, "  ", "/", ["1234567", "\u2212" + "5432/370"]),
        (7, False, "", "", ["1234567", "\u2212" + "5432370"]),
        (9, True, ",", ".", ["1,234,567.00", "\u2212" + "5,432.37000"]),
        (9, True, ".", ",", ["1.234.567,00", "\u2212" + "5.432,37000"]),
        (9, True, "  ", "/", ["1  234  567/00", "\u2212" + "5  432/37000"]),
        (9, True, "", "", ["123456700", "\u2212" + "543237000"]),
        (9, False, ",", ".", ["1234567.00", "\u2212" + "5432.37000"]),
        (9, False, ".", ",", ["1234567,00", "\u2212" + "5432,37000"]),
        (9, False, "  ", "/", ["1234567/00", "\u2212" + "5432/37000"]),
        (9, False, "", "", ["123456700", "\u2212" + "543237000"]),
    ],
)
def test_fmt_number_n_sigfig_seps(
    n_sigfig: int, use_seps: bool, sep_mark: str, dec_mark: str, x_out: str
):
    df = pd.DataFrame({"x": [1234567, -5432.37]})

    gt = GT(df).fmt_number(
        columns="x",
        n_sigfig=n_sigfig,
        use_seps=use_seps,
        sep_mark=sep_mark,
        dec_mark=dec_mark,
    )
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == x_out


@pytest.mark.parametrize(
    "force_sign,x_out",
    [
        (
            False,
            [
                "\u2212" + "234.654",
                "\u2212" + "0.001",
                "\u2212" + "0.100",
                "0.000",
                "12,354.300",
                "9,939,293,923.230",
            ],
        ),
        (
            True,
            [
                "\u2212" + "234.654",
                "\u2212" + "0.001",
                "\u2212" + "0.100",
                "0.000",
                "+12,354.300",
                "+9,939,293,923.230",
            ],
        ),
    ],
)
def test_fmt_number_force_sign(force_sign: bool, x_out: str):
    df = pd.DataFrame({"x": [-234.654, -0.000634, -0.1, 0, 12354.3, 9939293923.23]})

    gt = GT(df).fmt_number(columns="x", decimals=3, force_sign=force_sign)
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == x_out


@pytest.mark.parametrize(
    "pattern,x_out",
    [
        ("{x}", ["\u2212" + "234.65", "0.00", "25,342.00"]),
        ("a{x}b", ["a" + "\u2212" + "234.65b", "a0.00b", "a25,342.00b"]),
        (
            "  a {x} b {x} c  ",
            [
                "  a " + "\u2212" + "234.65 b " + "\u2212" + "234.65 c  ",
                "  a 0.00 b 0.00 c  ",
                "  a 25,342.00 b 25,342.00 c  ",
            ],
        ),
        ("{x}{x}", ["\u2212" + "234.65" + "\u2212" + "234.65", "0.000.00", "25,342.0025,342.00"]),
        (
            "#4$!|-_+%^&$*#{x}",
            [
                "#4$!|-_+%^&$*#" + "\u2212" + "234.65",
                "#4$!|-_+%^&$*#0.00",
                "#4$!|-_+%^&$*#25,342.00",
            ],
        ),
        (
            "{xx}{{x}}{xx}",
            ["{xx}{" + "\u2212" + "234.65}{xx}", "{xx}{0.00}{xx}", "{xx}{25,342.00}{xx}"],
        ),
    ],
)
def test_fmt_number_pattern(pattern: str, x_out: str):
    df = pd.DataFrame({"x": [-234.654, 0, 25342]})

    gt = GT(df).fmt_number(columns="x", decimals=2, pattern=pattern)
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == x_out


# Test `_format_number_fixed_decimals()` util function
@pytest.mark.parametrize(
    "value,x_out",
    [
        (8234252645325, "8,234,252,645,325.00"),
        (234252645325, "234,252,645,325.00"),
        (34252645325, "34,252,645,325.00"),
        (4252645325, "4,252,645,325.00"),
        (252645325, "252,645,325.00"),
        (52645325, "52,645,325.00"),
        (2645325, "2,645,325.00"),
        (645325, "645,325.00"),
        (45325, "45,325.00"),
        (5325, "5,325.00"),
        (325, "325.00"),
        (25, "25.00"),
        (5, "5.00"),
        (0, "0.00"),
        (2645325.234523, "2,645,325.23"),
        (645325.234523, "645,325.23"),
        (45325.234523, "45,325.23"),
        (5325.234523, "5,325.23"),
        (325.234523, "325.23"),
        (25.234523, "25.23"),
        (5.234523, "5.23"),
        (0, "0.00"),
        (0.1, "0.10"),
        (0.01, "0.01"),
        (0.00023, "0.00"),
        (0.000033, "0.00"),
        (0.00000000446453, "0.00"),
        (-325, "-325.00"),
    ],
)
def test_format_number_fixed_decimals(value: Union[int, float], x_out: str):
    x = _format_number_fixed_decimals(value=value, decimals=2, sep_mark=",")
    assert x == x_out


@pytest.mark.parametrize(
    "value, out",
    [
        (325, "325"),
        (-325, "-325"),
        (-1320, "-1,320"),
    ],
)
def test_format_number_n_sigfig_3(value, out: str):
    assert _format_number_n_sigfig(value, 3) == out


@pytest.mark.parametrize(
    "str_number,x_out",
    [
        ("1e-5", "0.00001"),
        ("1.5e-5", "0.000015"),
        ("-1e-5", "-0.00001"),
        ("-1.5e-5", "-0.000015"),
        ("1E-5", "0.00001"),
        ("1.5E-5", "0.000015"),
        ("-1E-5", "-0.00001"),
        ("-1.5E-5", "-0.000015"),
        ("4.46453E-9", "0.00000000446453"),
        ("1E+5", "100000"),
        ("1.5E+5", "150000"),
        ("150000", "150000"),
    ],
)
def test_expand_exponential_to_full_string(str_number: str, x_out: str):
    x = _expand_exponential_to_full_string(str_number=str_number)
    assert x == x_out


def test_format_number_with_sigfig():
    df = pd.DataFrame({"x": [1.23, 2.345]})
    gt = GT(df).fmt_number(
        columns="x",
        n_sigfig=2,
        drop_trailing_zeros=True,
        drop_trailing_dec_mark=False,
    )
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == ["1.2", "2.3"]


def test_format_number_with_sigfig_2():
    df = pd.DataFrame({"x": [0.000000000000000534, 9.123]})
    gt = GT(df).fmt_number(
        columns="x",
        n_sigfig=2,
        drop_trailing_zeros=True,
        drop_trailing_dec_mark=False,
    )
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == ["0.00000000000000053", "9.1"]


def test_format_number_with_sep_dec_marks():
    df = pd.DataFrame({"x": [12345678.12345678, 1.0, 0, -12345678.12345678]})
    gt = GT(df).fmt_number(columns="x", decimals=5, sep_mark=".", dec_mark=",")
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == ["12.345.678,12346", "1,00000", "0,00000", "\u2212" + "12.345.678,12346"]


# ------------------------------------------------------------------------------
# Tests of `fmt_currency()`
# ------------------------------------------------------------------------------

FMT_CURRENCY_CASES: list[tuple[dict[str, Any], list[str]]] = [
    (dict(), ["$1,234,567.00", "−$5,432.37"]),
    (dict(currency="USD"), ["$1,234,567.00", "−$5,432.37"]),
    (dict(currency="EUR"), ["&#8364;1,234,567.00", "−&#8364;5,432.37"]),
    (dict(use_subunits=False), ["$1,234,567", "−$5,432"]),
    (dict(use_subunits=False, decimals=4), ["$1,234,567.0000", "−$5,432.3700"]),
    (dict(decimals=4), ["$1,234,567.0000", "−$5,432.3700"]),
    (
        dict(decimals=0, drop_trailing_dec_mark=False),
        ["$1,234,567.", "−$5,432."],
    ),
    (dict(use_seps=False), ["$1234567.00", "−$5432.37"]),
    (dict(placement="right"), ["1,234,567.00$", "−5,432.37$"]),
    (dict(placement="right", incl_space=True), ["1,234,567.00 $", "−5,432.37 $"]),
    (dict(incl_space=True), ["$ 1,234,567.00", "−$ 5,432.37"]),
]


@pytest.mark.parametrize("fmt_currency_kwargs,x_out", FMT_CURRENCY_CASES)
def test_fmt_currency_case(fmt_currency_kwargs: dict[str, Any], x_out: list[str]):
    df = pd.DataFrame({"x": [1234567, -5432.37]})
    gt = GT(df).fmt_currency(columns="x", **fmt_currency_kwargs)
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == x_out


def test_fmt_currency_force_sign():
    df = pd.DataFrame({"x": [-234.654, -0.0001, 0, 2352.23, 12354.3, 9939293923.23]})

    gt = GT(df).fmt_currency(columns="x", force_sign=True)
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == [
        "−$234.65",
        "−$0.00",
        "$0.00",
        "+$2,352.23",
        "+$12,354.30",
        "+$9,939,293,923.23",
    ]


# ------------------------------------------------------------------------------
# Test `fmt_time()`
# ------------------------------------------------------------------------------

df_fmt_time = pd.DataFrame({"x": ["10:59:59", "13:23:59", "23:15"]})


def test_fmt_time_iso():
    gt = GT(df_fmt_time).fmt_time(columns="x", time_style="iso")
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == ["10:59:59", "13:23:59", "23:15:00"]


def test_fmt_time_iso_short():
    gt = GT(df_fmt_time).fmt_time(columns="x", time_style="iso-short")
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == ["10:59", "13:23", "23:15"]


def test_fmt_time_h_m_s_p():
    gt = GT(df_fmt_time).fmt_time(columns="x", time_style="h_m_s_p")
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == ["10:59:59 AM", "1:23:59 PM", "11:15:00 PM"]


def test_fmt_time_h_m_p():
    gt = GT(df_fmt_time).fmt_time(columns="x", time_style="h_m_p")
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == ["10:59 AM", "1:23 PM", "11:15 PM"]


def test_fmt_time_h_p():
    gt = GT(df_fmt_time).fmt_time(columns="x", time_style="h_p")
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == ["10 AM", "1 PM", "11 PM"]


# ------------------------------------------------------------------------------
# Test `fmt_date()`
# ------------------------------------------------------------------------------


def test_fmt_date():
    df = pd.DataFrame(
        {
            "x": [
                "2020-05-20",
                "2020-05-20 22:30",
                "2020-05-20T22:30",
                "2020-05-20 22:30:05",
                "2020-05-20 22:30:05.824",
            ]
        }
    )

    gt = GT(df).fmt_date(columns="x", date_style="wd_m_day_year")
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == [
        "Wed, May 20, 2020",
        "Wed, May 20, 2020",
        "Wed, May 20, 2020",
        "Wed, May 20, 2020",
        "Wed, May 20, 2020",
    ]


# ------------------------------------------------------------------------------
# Test `fmt_datetime()`
# ------------------------------------------------------------------------------


def test_fmt_datetime():
    df = pd.DataFrame(
        {
            "x": [
                "2023-01-05 00:00:00",
                "2013-05-15 23:15",
                "2020-05-20",
                "2020-05-20 22:30",
                "2020-05-20T22:30",
                "2020-05-20 22:30:05",
                "2020-05-20T22:30:05.232",
            ]
        }
    )

    gt = GT(df).fmt_datetime(
        columns="x", date_style="wday_month_day_year", time_style="h_m_s_p", sep=" at "
    )
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == [
        "Thursday, January 5, 2023 at 12:00:00 AM",
        "Wednesday, May 15, 2013 at 11:15:00 PM",
        "Wednesday, May 20, 2020 at 12:00:00 AM",
        "Wednesday, May 20, 2020 at 10:30:00 PM",
        "Wednesday, May 20, 2020 at 10:30:00 PM",
        "Wednesday, May 20, 2020 at 10:30:05 PM",
        "Wednesday, May 20, 2020 at 10:30:05 PM",
    ]


def test_fmt_datetime_bad_date_style_raises():
    df = pd.DataFrame(
        {
            "x": [
                "2023-01-05 00:00:00",
                "2013-05-15 23:15",
            ]
        }
    )

    with pytest.raises(ValueError) as exc_info:
        gt = GT(df).fmt_datetime(
            columns="x", date_style="quarter_month_day_year", time_style="h_m_s_p", sep=" at "
        )

    assert "date_style must be one of:" in exc_info.value.args[0]


# ------------------------------------------------------------------------------
# Test `fmt_bytes()`
# ------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "src,dst",
    [
        (-3, "−3 B"),
        (0, "0 B"),
        (0.9, "0 B"),
        (1, "1 B"),
        (994, "994 B"),
        (1000, "1 kB"),
        (1024, "1 kB"),
        (2346345274.3, "2.3 GB"),
        (902487216348759693489128343269, "902,487.2 YB"),
    ],
)
def test_fmt_bytes_default(src: float, dst: str):
    df = pd.DataFrame({"x": [src]})
    gt = GT(df).fmt_bytes(columns="x")
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == [dst]


@pytest.mark.parametrize(
    "fmt_bytes_kwargs,x_in,x_out",
    [
        (dict(standard="binary"), [1000, 1024, 2346345274.3], ["1,000 B", "1 KiB", "2.2 GiB"]),
        (dict(standard="binary", decimals=2), [845653745232536], ["769.12 TiB"]),
        (
            dict(standard="binary", use_seps=False, force_sign=True, incl_space=False),
            [902487216348759693489128343269],
            ["+746519.9YiB"],
        ),
    ],
)
def test_fmt_bytes_case(fmt_bytes_kwargs: dict[str, Any], x_in: list[float], x_out: list[str]):
    df = pd.DataFrame({"x": x_in})
    gt = GT(df).fmt_bytes(columns="x", **fmt_bytes_kwargs)
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == x_out


# ------------------------------------------------------------------------------
# Test `fmt_roman()`
# ------------------------------------------------------------------------------


df_fmt_roman = pd.DataFrame({"x": [-1234, 0, 0.4, 0.8, 1, 99, 4500]})


def test_fmt_roman_upper():
    gt = GT(df_fmt_roman).fmt_roman(columns="x")
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == ["MCCXXXIV", "N", "N", "I", "I", "XCIX", "ex terminis"]


def test_fmt_roman_lower():
    gt = GT(df_fmt_roman).fmt_roman(columns="x", case="lower")
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == ["mccxxxiv", "n", "n", "i", "i", "xcix", "ex terminis"]


def test_fmt_roman_bad_case_raises():
    with pytest.raises(ValueError) as exc_info:
        gt = GT(df_fmt_roman).fmt_roman(columns="x", case="case")

    assert "The `case` argument must be either 'upper' or 'lower'" in exc_info.value.args[0]


# ------------------------------------------------------------------------------
# Test `fmt_markdown()`
# ------------------------------------------------------------------------------


def test_fmt_markdown():
    df = pd.DataFrame(
        {
            "x": [
                "**bold** and *italic*",
                "__bold__ and _italic_",
                "<strong>bold</strong> and <em>italic</em>",
                "`code` and [link](www.example.com)",
            ]
        }
    )

    # Expect that the smaller values in `x` are formatted correctly when
    # varying the number of fixed decimal places (`decimals`)
    gt = GT(df).fmt_markdown(columns="x")
    x = _get_column_of_values(gt, column_name="x", context="html")
    assert x == [
        "<strong>bold</strong> and <em>italic</em>",
        "<strong>bold</strong> and <em>italic</em>",
        "<strong>bold</strong> and <em>italic</em>",
        '<code>code</code> and <a href="www.example.com">link</a>',
    ]


# ------------------------------------------------------------------------------
# Test `data_color()` and util functions
# ------------------------------------------------------------------------------


@pytest.fixture
def df_color():
    df = pd.DataFrame(
        {
            "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "B": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
            "C": ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"],
        }
    )
    return df


@pytest.mark.parametrize(
    "color, x_out",
    [
        ("red", "#FF0000"),
        ("#FFF", "#FFFFFF"),
        ("crimson", "#DC143C"),
        ("SteelBlue", "#4682B4"),
        ("RED", "#FF0000"),
        ("#FFFFFF", "#FFFFFF"),
        ("transparent", "#FFFFFF00"),
    ],
)
def test_html_color(color: str, x_out: str):
    x = _html_color(colors=[color])
    assert x == [x_out]


@pytest.mark.parametrize(
    "color, x_out, alpha",
    [
        ("red", "#FF0000D8", 0.85),
        ("#DEF", "#DDEEFFD8", 0.85),
        ("crimson", "#DC143CD8", 0.85),
        ("SteelBlue", "#4682B4D8", 0.85),
        ("RED", "#FF0000D8", 0.85),
        ("#FFFFFF", "#FFFFFFD8", 0.85),
        ("transparent", "#FFFFFF00", 0.85),
        ("#FFFFFF00", "#FFFFFF00", 0.85),
    ],
)
def test_html_color_with_alpha(color: str, x_out: str, alpha: float):
    x = _html_color(colors=[color], alpha=alpha)
    assert x == [x_out]


def test_fmt_image_single():
    formatter = FmtImage(sep=" ", file_pattern="{}.svg", encode=False)
    res = formatter.to_html("/a")
    dst = formatter.SPAN_TEMPLATE.format('<img src="/a.svg" style="vertical-align: middle;">')

    assert strip_windows_drive(res) == dst


def test_fmt_image_missing():
    formatter = FmtImage()
    assert formatter.to_html(None) is None

    formatter_pd = FmtImage(pd.DataFrame())
    assert formatter_pd.to_html(pd.NA) is pd.NA


def test_fmt_image_multiple():
    formatter = FmtImage(sep="---", file_pattern="{}.svg", encode=False)
    res = formatter.to_html("/a,/b")
    dst = formatter.SPAN_TEMPLATE.format(
        '<img src="/a.svg" style="vertical-align: middle;">'
        "---"
        '<img src="/b.svg" style="vertical-align: middle;">'
    )

    assert strip_windows_drive(res) == dst


def test_fmt_image_encode(tmpdir):
    from base64 import b64encode
    from pathlib import Path

    content = "abc"
    p_svg = Path(tmpdir) / "some.svg"
    p_svg.write_text(content)

    formatter = FmtImage(sep=" ", file_pattern="{}.svg", encode=True)
    res = formatter.to_html(f"{tmpdir}/some")

    b64_content = b64encode(content.encode()).decode()
    img_src = f"data:image/svg+xml;base64,{b64_content}"
    dst = formatter.SPAN_TEMPLATE.format(f'<img src="{img_src}" style="vertical-align: middle;">')

    assert strip_windows_drive(res) == dst


def test_fmt_image_width_height_str():
    formatter = FmtImage(encode=False, width="20px", height="30px")
    res = formatter.to_html("/a")
    dst_img = '<img src="/a" style="height: 30px;width: 20px;vertical-align: middle;">'
    dst = formatter.SPAN_TEMPLATE.format(dst_img)

    assert strip_windows_drive(res) == dst


def test_fmt_image_height_int():
    formatter = FmtImage(encode=False, height=30)
    res = formatter.to_html("/a")
    dst_img = '<img src="/a" style="height: 30px;vertical-align: middle;">'
    dst = formatter.SPAN_TEMPLATE.format(dst_img)

    assert strip_windows_drive(res) == dst


def test_fmt_image_width_int():
    formatter = FmtImage(encode=False, width=20)

    with pytest.raises(NotImplementedError):
        formatter.to_html("/a")


@pytest.mark.skipif(sys.platform == "win32", reason="uses linux specific paths")
def test_fmt_image_path():
    formatter = FmtImage(encode=False, path="/a/b")
    res = formatter.to_html("c")
    assert 'src="/a/b/c"' in strip_windows_drive(res)


@pytest.mark.parametrize(
    "url", ["http://posit.co/", "http://posit.co", "https://posit.co/", "https://posit.co"]
)
def test_fmt_image_path_http(url: str):
    formatter = FmtImage(encode=False, height=30, path=url)
    res = formatter.to_html("c")
    dst_img = '<img src="{}/c" style="height: 30px;vertical-align: middle;">'.format(
        url.removesuffix("/")
    )
    dst = formatter.SPAN_TEMPLATE.format(dst_img)

    assert strip_windows_drive(res) == dst


@pytest.mark.parametrize(
    "src,dst",
    [
        # 1. unit with superscript
        ("m^2", 'm<span style="white-space:nowrap;"><sup style="line-height:0;">2</sup></span>'),
        # 2. unit with subscript
        ("h_0", 'h<span style="white-space:nowrap;"><sub style="line-height:0;">0</sub></span>'),
        # 3. unit with superscript and subscript
        (
            "h_0^3",
            'h<span style="white-space:nowrap;"><sub style="line-height:0;">0</sub></span><span style="white-space:nowrap;"><sup style="line-height:0;">3</sup></span>',
        ),
        # 4. unit with superscript and subscript (using overstriking)
        (
            "h[_0^3]",
            'h<span style="display:inline-block;line-height:1em;text-align:left;font-size:60%;vertical-align:-0.25em;margin-left:0.1em;">3<br>0</span>',
        ),
        # 5. slashed-unit shorthand for a '-1' exponent
        (
            "/s",
            's<span style="white-space:nowrap;"><sup style="line-height:0;">&minus;1</sup></span>',
        ),
        # 6. slashes between units normalized
        (
            "t_0 / t_n",
            't<span style="white-space:nowrap;"><sub style="line-height:0;">0</sub></span>/t<span style="white-space:nowrap;"><sub style="line-height:0;">n</sub></span>',
        ),
        # 7. multiple inline units, separating by a space
        (
            "kg^2 m^-1",
            'kg<span style="white-space:nowrap;"><sup style="line-height:0;">2</sup></span> m<span style="white-space:nowrap;"><sup style="line-height:0;">&minus;1</sup></span>',
        ),
        # 8. use of a number allowed with previous rules
        (
            "10^3 kg^2 m^-1",
            '10<span style="white-space:nowrap;"><sup style="line-height:0;">3</sup></span> kg<span style="white-space:nowrap;"><sup style="line-height:0;">2</sup></span> m<span style="white-space:nowrap;"><sup style="line-height:0;">&minus;1</sup></span>',
        ),
        # 9. use of 'x' preceding number to form scalar multiplier
        (
            "x10^3 kg^2 m^-1",
            '&times;10<span style="white-space:nowrap;"><sup style="line-height:0;">3</sup></span> kg<span style="white-space:nowrap;"><sup style="line-height:0;">2</sup></span> m<span style="white-space:nowrap;"><sup style="line-height:0;">&minus;1</sup></span>',
        ),
        # 10. hyphen is transformed to minus sign when preceding a unit
        (
            "-h^2",
            '−h<span style="white-space:nowrap;"><sup style="line-height:0;">2</sup></span>',
        ),
        # 11. italicization of base unit
        (
            "*m*^2",
            '<em>m</em><span style="white-space:nowrap;"><sup style="line-height:0;">2</sup></span>',
        ),
        # 12. emboldening of base unit
        (
            "**m**^2",
            '<strong>m</strong><span style="white-space:nowrap;"><sup style="line-height:0;">2</sup></span>',
        ),
        # 13. italicizing and emboldening of base unit
        (
            "_**m**_^2",
            '<em><strong>m</strong></em><span style="white-space:nowrap;"><sup style="line-height:0;">2</sup></span>',
        ),
        # 14. styling of subscripts and superscripts
        (
            "h_*0*^**3**",
            'h<span style="white-space:nowrap;"><sub style="line-height:0;"><em>0</em></sub></span><span style="white-space:nowrap;"><sup style="line-height:0;"><strong>3</strong></sup></span>',
        ),
        # 15. transformation of common units from ASCII to preferred form
        ("ug", "µg"),
        # 16. insertion of common symbols and Greek letters via `:[symbol name]:`
        (":angstrom:", "Å"),
        # 17. use of chemical formulas via `%[chemical formula]%`
        (
            "%C6H12O6%",
            'C<span style="white-space:nowrap;"><sub style="line-height:0;">6</sub></span>H<span style="white-space:nowrap;"><sub style="line-height:0;">12</sub></span>O<span style="white-space:nowrap;"><sub style="line-height:0;">6</sub></span>',
        ),
        # 18. Any '<' and '>' characters from input are escaped to prevent HTML rendering as tags
        (
            "m^2 <tag> s_0",
            'm<span style="white-space:nowrap;"><sup style="line-height:0;">2</sup></span> &lt;tag&gt; s<span style="white-space:nowrap;"><sub style="line-height:0;">0</sub></span>',
        ),
    ],
)
def test_fmt_units(src: str, dst: str):
    units_tbl = pl.DataFrame({"units": [src]})
    gt_tbl = GT(units_tbl).fmt_units(columns="units")

    assert dst == _get_column_of_values(gt_tbl, column_name="units", context="html")[0]


# ------------------------------------------------------------------------------
# Test `fmt_nanoplot()`
# ------------------------------------------------------------------------------


def _nanoplot_has_tag_attrs(nanoplot_str: str, tag: str, attrs: list[tuple[str, str]]) -> bool:
    import re

    found: list[bool] = []

    for i, _ in enumerate(attrs):
        attrs_i = attrs[i]
        attr_str = f'{attrs_i[0]}="{attrs_i[1]}"'

        found_i = bool(re.search(f"<{tag}.*?{attr_str}.*?</{tag}>", nanoplot_str))

        found.append(found_i)

    return all(found)


df_fmt_nanoplot_single = pl.DataFrame({"vals": [-5.3, 6.3]})

df_fmt_nanoplot_multi = pl.DataFrame(
    {
        "vals": [
            {"x": [-12.0, -5.0, 6.0, 3.0, 0.0, 8.0, -7.0]},
            {"x": [2, 0, 15, 7, 8, 10, 1, 24, 17, 13, 6]},
        ],
    }
)


FMT_NANOPLOT_CASES: list[dict[str, Any]] = [
    # 1. default case
    dict(),
    # 2. reference line with 0 value
    dict(reference_line=0),
    # 3. reference line using a string
    dict(reference_line="mean"),
    # 4. use of a reference area
    dict(reference_area=[0.1, 5.3]),
    # 5. use of a reference line and a reference area
    dict(reference_line=0, reference_area=[2.3, "max"]),
    # 6. expansion in the y direction using a single value
    dict(expand_y=20),
    # 7. expansion in the y direction using a single value (same as #6)
    dict(expand_y=[20]),
    # 8. expansion in the y direction using two values
    dict(expand_y=[-30, 20]),
    # 9. expansions in the x and y directions
    dict(expand_x=[-30, 20], expand_y=[-30, 20]),
]


# Test category 1: Horizontal line-based nanoplot single values
def test_fmt_nanoplot_single_vals_only_line():
    gt = GT(df_fmt_nanoplot_single).fmt_nanoplot(
        columns="vals",
        plot_type="line",
        **FMT_NANOPLOT_CASES[0],
    )
    res = _get_column_of_values(gt, column_name="vals", context="html")[0]

    assert _nanoplot_has_tag_attrs(
        res,
        tag="line",
        attrs=[
            ("x1", "0.0"),
            ("y1", "65.0"),
            ("stroke", "#4682B4"),
            ("stroke-width", "8"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        res,
        tag="g",
        attrs=[
            ("class", "horizontal-line"),
        ],
    )

    # All other test cases for the horizontal line nanoplot will produce the same output
    # as this previous one (none will error as the non-relevant options are no ops)

    for _, params in enumerate(FMT_NANOPLOT_CASES[1:], start=1):
        gt = GT(df_fmt_nanoplot_single).fmt_nanoplot(
            columns="vals",
            plot_type="line",
            **params,
        )
        res_other = _get_column_of_values(gt, column_name="vals", context="html")[0]

        assert res == res_other


# Test category 2: Horizontal bar-based nanoplot single values
def test_fmt_nanoplot_single_vals_only_bar():
    gt = GT(df_fmt_nanoplot_single).fmt_nanoplot(
        columns="vals",
        plot_type="bar",
        **FMT_NANOPLOT_CASES[0],
    )
    res = _get_column_of_values(gt, column_name="vals", context="html")[0]

    assert _nanoplot_has_tag_attrs(
        res,
        tag="rect",
        attrs=[
            ("stroke", "#CC3243"),
            ("stroke-width", "4"),
            ("fill", "#D75A68"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        res,
        tag="rect",
        attrs=[
            ("stroke", "transparent"),
            ("fill", "transparent"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        res,
        tag="text",
        attrs=[
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "30px"),
        ],
    )

    # All other test cases for the horizontal bar nanoplot will produce the same output
    # as this previous one (none will error as the non-relevant options are no ops)
    for _, params in enumerate(FMT_NANOPLOT_CASES[1:], start=1):
        gt = GT(df_fmt_nanoplot_single).fmt_nanoplot(
            columns="vals",
            plot_type="bar",
            **params,
        )
        res_other = _get_column_of_values(gt, column_name="vals", context="html")[0]

        assert res == res_other


# Test category 3: Line-based nanoplot, multiple values per row
def test_fmt_nanoplot_multi_vals_line():
    # Subcase with default options
    gt = GT(df_fmt_nanoplot_multi).fmt_nanoplot(
        columns="vals",
        plot_type="line",
        **FMT_NANOPLOT_CASES[0],
    )
    res = _get_column_of_values(gt, column_name="vals", context="html")[0]

    assert _nanoplot_has_tag_attrs(
        res,
        tag="pattern",
        attrs=[
            ("width", "8"),
            ("height", "8"),
            ("patternUnits", "userSpaceOnUse"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        res,
        tag="path",
        attrs=[
            ("class", "area-closed"),
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill-opacity", "0.7"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        res,
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
        res,
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
        res,
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
        res,
        tag="g",
        attrs=[
            ("class", "vert-line"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        res,
        tag="g",
        attrs=[
            ("class", "y-axis-line"),
        ],
    )


# Test category 3: Line-based nanoplot, multiple values per row, use of reference line
def test_fmt_nanoplot_multi_vals_line_ref_line():
    # Subcase with reference line
    gt = GT(df_fmt_nanoplot_multi).fmt_nanoplot(
        columns="vals",
        plot_type="line",
        **FMT_NANOPLOT_CASES[1],
    )
    res = _get_column_of_values(gt, column_name="vals", context="html")[0]

    assert _nanoplot_has_tag_attrs(
        res,
        tag="line",
        attrs=[
            ("class", "ref-line"),
            ("stroke", "#75A8B0"),
            ("stroke-width", "1"),
            ("stroke-dasharray", "4 3"),
            ("stroke-linecap", "round"),
            ("vector-effect", "non-scaling-stroke"),
        ],
    )


# Test category 4: Line-based nanoplot, multiple values per row, use of reference
# line and reference area
def test_fmt_nanoplot_multi_vals_line_ref_line_ref_area():
    gt = GT(df_fmt_nanoplot_multi).fmt_nanoplot(
        columns="vals",
        plot_type="line",
        **FMT_NANOPLOT_CASES[4],
    )
    res = _get_column_of_values(gt, column_name="vals", context="html")[0]

    assert _nanoplot_has_tag_attrs(
        res,
        tag="line",
        attrs=[
            ("class", "ref-line"),
            ("stroke", "#75A8B0"),
            ("stroke-width", "1"),
            ("stroke-dasharray", "4 3"),
            ("stroke-linecap", "round"),
            ("vector-effect", "non-scaling-stroke"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        res,
        tag="path",
        attrs=[
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill", "#A6E6F2"),
            ("fill-opacity", "0.8"),
        ],
    )


# Test category 5: Bar-based nanoplot, multiple values per row
def test_fmt_nanoplot_multi_vals_bar():
    # Subcase with default options
    gt = GT(df_fmt_nanoplot_multi).fmt_nanoplot(
        columns="vals",
        plot_type="bar",
        **FMT_NANOPLOT_CASES[0],
    )
    res = _get_column_of_values(gt, column_name="vals", context="html")[0]

    assert _nanoplot_has_tag_attrs(
        res,
        tag="rect",
        attrs=[
            ("stroke", "#CC3243"),
            ("stroke-width", "4"),
            ("fill", "#D75A68"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        res,
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
        res,
        tag="text",
        attrs=[
            ("x", "0"),
            ("y", "19.0"),
            ("fill", "transparent"),
            ("stroke", "transparent"),
            ("font-size", "25"),
        ],
    )


# Test category 6: Bar-based nanoplot, multiple values per row, use of reference line
def test_fmt_nanoplot_multi_vals_bar_ref_line():
    gt = GT(df_fmt_nanoplot_multi).fmt_nanoplot(
        columns="vals",
        plot_type="bar",
        **FMT_NANOPLOT_CASES[1],
    )
    res = _get_column_of_values(gt, column_name="vals", context="html")[0]

    assert _nanoplot_has_tag_attrs(
        res,
        tag="line",
        attrs=[
            ("class", "ref-line"),
            ("stroke", "#75A8B0"),
            ("stroke-width", "1"),
            ("stroke-dasharray", "4 3"),
            ("stroke-linecap", "round"),
            ("vector-effect", "non-scaling-stroke"),
        ],
    )


# Test category 7: Bar-based nanoplot, multiple values per row, reference line and reference area
def test_fmt_nanoplot_multi_vals_bar_ref_line_ref_area():
    gt = GT(df_fmt_nanoplot_multi).fmt_nanoplot(
        columns="vals",
        plot_type="bar",
        **FMT_NANOPLOT_CASES[4],
    )
    res = _get_column_of_values(gt, column_name="vals", context="html")[0]

    assert _nanoplot_has_tag_attrs(
        res,
        tag="line",
        attrs=[
            ("class", "ref-line"),
            ("stroke", "#75A8B0"),
            ("stroke-width", "1"),
            ("stroke-dasharray", "4 3"),
            ("stroke-linecap", "round"),
            ("vector-effect", "non-scaling-stroke"),
        ],
    )

    assert _nanoplot_has_tag_attrs(
        res,
        tag="path",
        attrs=[
            ("stroke", "transparent"),
            ("stroke-width", "2"),
            ("fill", "#A6E6F2"),
            ("fill-opacity", "0.8"),
        ],
    )


@pytest.mark.parametrize(
    "plot_type",
    [
        ("bars"),
        ("abc"),
    ],
)
def test_fmt_nanoplot_raise_implemented_error(plot_type: str):
    with pytest.raises(NotImplementedError) as exc_info:
        GT(df_fmt_nanoplot_single).fmt_nanoplot(columns="vals", plot_type=plot_type)
        assert f"Value received: {plot_type}" in exc_info.value.args[0]


def test_fmt_nanoplot_polars_listcol(snapshot):
    gt = GT(pl.DataFrame({"x": [[1, 2], [3, 4]]})).fmt_nanoplot("x")

    assert_rendered_body(snapshot, gt)


def test_normalize_locale():
    assert _normalize_locale("af-ZA") == "af"


def test_normalize_locale_noops_none():
    assert _normalize_locale(None) is None


def test_normalize_locale_raises():
    with pytest.raises(ValueError) as exc_info:
        _normalize_locale("abcde")

    assert "abcde" in exc_info.value.args[0]


def test_normalize_locale_babel_validation():
    defaults = _locale._get_default_locales_data()
    default_names = [entry["default_locale"] for entry in defaults]

    assert "de-CH" not in default_names
    assert _normalize_locale("de-CH") == "de-CH"


def test_get_locale_sep_mark_lookup():
    # , is the group associated with "ak" locale
    assert _get_locale_sep_mark("zzz", use_seps=True, locale="ak") == ","


def test_get_locale_sep_mark_default_for_none():
    assert _get_locale_sep_mark("zzz", use_seps=True, locale=None) == "zzz"


def test_get_locale_sep_mark_not_use_seps():
    # for some reason, when use seps is false, an empty string is returned
    assert _get_locale_sep_mark("zzz", use_seps=False) == ""


def test_get_locale_sep_mark_no_match_raises():
    with pytest.raises(Exception):
        _get_locale_sep_mark("zzz", use_seps=True, locale="NOT_A_LOCALE")


def test_get_local_dec_mark():
    # france uses a , as a decimal mark (e.g. 1.000,99)
    assert _get_locale_dec_mark("zzz", "fr") == ","


def test_get_locale_dec_mark_default():
    assert _get_locale_dec_mark(default="abc") == "abc"


def test_validate_locales():
    _validate_locale("fr")


def test_validate_locales_raises():
    with pytest.raises(ValueError) as exc_info:
        _validate_locale("NOT_A_LOCALE")

    assert "The normalized locale name `NOT-A-LOCALE`" in exc_info.value.args[0]


def test_get_locale_currency_code():
    assert _get_locale_currency_code("fr") == "EUR"


def test_get_locale_currency_code_default():
    assert _get_locale_currency_code() == "USD"


def test_get_locale_currency_code_no_match_raises():
    with pytest.raises(Exception):
        assert _get_locale_currency_code("NOT_A_LOCALE")


def test_get_currency_str():
    assert _get_currency_str("AED") == "DH"


def test_get_currency_str_no_match_raises():
    with pytest.raises(Exception):
        _get_currency_str("NOT_A_CURRENCY")


@pytest.mark.parametrize(
    "src, fn",
    [
        (1, "fmt_number"),
        (2, "fmt_integer"),
        (3, "fmt_scientific"),
        (4, "fmt_percent"),
        (5, "fmt_currency"),
        (6, "fmt_bytes"),
        ("2023-12-31", "fmt_date"),
        ("12:34:56", "fmt_time"),
        ("2023-12-31 12:34:56", "fmt_datetime"),
    ],
)
def test_fmt_with_locale1(src, fn):
    df = pd.DataFrame({"x": [src]})
    global_locale = local_locale = "en"

    # w/o global locale, w/o local locale => use default locale => "en"
    gt1 = getattr(GT(df), fn)()
    x1 = _get_column_of_values(gt1, column_name="x", context="html")

    # w global locale, w/o local locale => use global locale => "en"
    gt2 = getattr(GT(df, locale=global_locale), fn)()
    x2 = _get_column_of_values(gt2, column_name="x", context="html")

    # w/o global locale, w local locale => use local locale => "en"
    gt3 = getattr(GT(df), fn)(locale=local_locale)
    x3 = _get_column_of_values(gt3, column_name="x", context="html")

    assert x1 == x2 == x3


@pytest.mark.parametrize(
    "src, fn",
    [
        (1, "fmt_number"),
        (2, "fmt_integer"),
        (3, "fmt_scientific"),
        (4, "fmt_percent"),
        (5, "fmt_currency"),
        (6, "fmt_bytes"),
        ("2023-12-31", "fmt_date"),
        ("12:34:56", "fmt_time"),
        ("2023-12-31 12:34:56", "fmt_datetime"),
    ],
)
def test_fmt_with_locale2(src, fn):
    df = pd.DataFrame({"x": [src]})
    global_locale = local_locale = "ja"

    # w global locale, w/o local locale => use global locale => "ja"
    gt1 = getattr(GT(df, locale=global_locale), fn)()
    x1 = _get_column_of_values(gt1, column_name="x", context="html")

    # w/o global locale, w local locale => use local locale => "ja"
    gt2 = getattr(GT(df), fn)(locale=local_locale)
    x2 = _get_column_of_values(gt2, column_name="x", context="html")

    assert x1 == x2


@pytest.mark.parametrize(
    "src, fn",
    [
        (1, "fmt_number"),
        (2, "fmt_integer"),
        (3, "fmt_scientific"),
        (4, "fmt_percent"),
        (5, "fmt_currency"),
        (6, "fmt_bytes"),
        ("2023-12-31", "fmt_date"),
        ("12:34:56", "fmt_time"),
        ("2023-12-31 12:34:56", "fmt_datetime"),
    ],
)
def test_fmt_with_locale3(src, fn):
    df = pd.DataFrame({"x": [src]})
    global_locale, local_locale = "ja", "de"

    # w global locale, w local locale => use local locale => "de"
    gt = getattr(GT(df, locale=global_locale), fn)(locale=local_locale)
    x = _get_column_of_values(gt, column_name="x", context="html")

    gt_de = getattr(GT(df, locale="de"), fn)()
    x_de = _get_column_of_values(gt_de, column_name="x", context="html")

    assert x == x_de
