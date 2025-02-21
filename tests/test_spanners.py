import pandas as pd
import polars as pl
import polars.selectors as cs
import pytest
from great_tables import GT, exibble
from great_tables._gt_data import Boxhead, ColInfo, ColInfoTypeEnum, SpannerInfo, Spanners
from great_tables._helpers import UnitStr
from great_tables._spanners import (
    _validate_sel_cols,
    cols_hide,
    cols_move,
    cols_move_to_end,
    cols_move_to_start,
    empty_spanner_matrix,
    spanners_print_matrix,
    tab_spanner,
    SpannerTransformer,
)
from great_tables._utils_render_html import _get_table_defs


@pytest.fixture
def spanners() -> Spanners:
    return Spanners(
        [
            SpannerInfo(spanner_id="a", spanner_level=0, vars=["col1"], built="A"),
            SpannerInfo(spanner_id="b", spanner_level=1, vars=["col2"], built="B"),
        ]
    )


@pytest.fixture
def boxhead() -> Boxhead:
    return Boxhead(
        [
            ColInfo(var="col1"),
            ColInfo(var="col2"),
            ColInfo(var="col3"),
            ColInfo(var="col4", type=ColInfoTypeEnum.hidden),
        ]
    )


def test_spanners_next_level_above_first(spanners: Spanners):
    assert spanners.next_level(["col1"]) == 1


def test_spanners_next_level_above_second(spanners: Spanners):
    assert spanners.next_level(["col2"]) == 2


def test_spanners_next_level_unique(spanners: Spanners):
    assert spanners.next_level(["col3"]) == 0


def test_spanners_print_matrix(spanners: Spanners, boxhead: Boxhead):
    mat, vars = spanners_print_matrix(spanners, boxhead)
    assert vars == ["col1", "col2", "col3"]
    assert mat == [
        {"col1": None, "col2": "B", "col3": None},
        {"col1": "A", "col2": None, "col3": None},
        {"col1": "col1", "col2": "col2", "col3": "col3"},
    ]


def test_spanners_print_matrix_arg_omit_columns_row(spanners: Spanners, boxhead: Boxhead):
    mat, vars = spanners_print_matrix(spanners, boxhead, omit_columns_row=True)
    assert vars == ["col1", "col2", "col3"]
    assert mat == [
        {"col1": None, "col2": "B", "col3": None},
        {"col1": "A", "col2": None, "col3": None},
    ]


def test_spanners_print_matrix_arg_include_hidden(spanners: Spanners, boxhead: Boxhead):
    mat, vars = spanners_print_matrix(spanners, boxhead, include_hidden=True)
    assert vars == ["col1", "col2", "col3", "col4"]
    assert mat == [
        {"col1": None, "col2": "B", "col3": None, "col4": None},
        {"col1": "A", "col2": None, "col3": None, "col4": None},
        {"col1": "col1", "col2": "col2", "col3": "col3", "col4": "col4"},
    ]


def test_spanners_print_matrix_exclude_stub():
    """spanners_print_matrix omits a selected column if it's in the stub."""
    info = SpannerInfo(spanner_id="a", spanner_level=0, vars=["x", "y"], built="A")
    spanners = Spanners([info])
    boxh = Boxhead([ColInfo(var="x"), ColInfo(var="y", type=ColInfoTypeEnum.stub)])

    mat, vars = spanners_print_matrix(spanners, boxh, omit_columns_row=True)
    assert vars == ["x"]
    assert mat == [{"x": "A"}]


def test_empty_spanner_matrix():
    mat, vars = empty_spanner_matrix(["a", "b"], omit_columns_row=False)

    assert vars == ["a", "b"]
    assert mat == [{"a": "a", "b": "b"}]


def test_empty_spanner_matrix_arg_omit_columns_row():
    mat, vars = empty_spanner_matrix(["a", "b"], omit_columns_row=True)

    assert vars == ["a", "b"]
    assert mat == []


def test_tab_spanners_with_columns():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    src_gt = GT(df)

    dst_span = SpannerInfo("a_spanner", 0, "a_spanner", vars=["b", "a"])

    new_gt = tab_spanner(src_gt, "a_spanner", columns=["b", "a"], gather=False)
    assert len(new_gt._spanners)
    assert new_gt._spanners[0] == dst_span


def test_tab_spanners_with_spanner_ids():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    src_gt = GT(df)

    # we'll be testing for this second spanner added
    dst_span = SpannerInfo("b_spanner", 1, "b_spanner", vars=["c", "b", "a"])

    gt_with_span = tab_spanner(src_gt, "a_spanner", columns=["b", "a"], gather=False)

    new_gt = tab_spanner(gt_with_span, "b_spanner", spanners="a_spanner", columns=["c"])

    assert len(new_gt._spanners) == 2
    assert new_gt._spanners[1] == dst_span


def test_tab_spanner_units_text():
    df = pd.DataFrame({"x": [1.234, 2.345], "y": [3.456, 4.567], "z": [5.678, 6.789]})

    gt = GT(df).tab_spanner(label="Area ({{m^2}})", columns=["x", "y"])

    spanner = gt._spanners[0]

    assert isinstance(spanner.spanner_label, UnitStr)


def test_tab_spanners_overlap():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    src_gt = GT(df)

    # we'll be testing for this second spanner added
    dst_span = SpannerInfo("b_spanner", 0, "b_spanner", vars=["b"])

    new_gt = src_gt.tab_spanner("a_spanner", columns=["a"], gather=False).tab_spanner(
        "b_spanner", columns=["b"]
    )

    assert len(new_gt._spanners) == 2
    assert new_gt._spanners[1] == dst_span


def test_multiple_spanners_above_one():
    from great_tables import GT, exibble

    gt = (
        GT(exibble, rowname_col="row", groupname_col="group")
        .tab_spanner("A", ["num", "char", "fctr"])
        .tab_spanner("B", ["fctr"])
        .tab_spanner("C", ["num", "char"])
        .tab_spanner("D", ["fctr", "date", "time"])
        .tab_spanner("E", spanners=["B", "C"])
    )

    # Assert that the spanners have been added in the correct
    # format and in the correct levels

    assert len(gt._spanners) == 5
    assert gt._spanners[0] == SpannerInfo("A", 0, "A", vars=["num", "char", "fctr"])
    assert gt._spanners[1] == SpannerInfo("B", 1, "B", vars=["fctr"])
    assert gt._spanners[2] == SpannerInfo("C", 1, "C", vars=["num", "char"])
    assert gt._spanners[3] == SpannerInfo("D", 2, "D", vars=["fctr", "date", "time"])
    assert gt._spanners[4] == SpannerInfo("E", 3, "E", vars=["fctr", "num", "char"])


def test_tab_spanners_with_gather():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    src_gt = GT(df)

    new_gt = tab_spanner(src_gt, "a_spanner", columns=["a", "c"], gather=True)

    assert len(new_gt._spanners) == 1
    assert [col.var for col in new_gt._boxhead] == ["a", "c", "b"]


def test_cols_width_partial_set():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    gt_tbl = GT(df).cols_width({"a": "10px"})

    assert gt_tbl._boxhead[0].column_width == "10px"
    assert gt_tbl._boxhead[1].column_width == None
    assert gt_tbl._boxhead[2].column_width == None


def test_cols_width_fully_set():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    gt_tbl = GT(df).cols_width({"a": "10px", "b": "20px", "c": "30px"})

    assert gt_tbl._boxhead[0].column_width == "10px"
    assert gt_tbl._boxhead[1].column_width == "20px"
    assert gt_tbl._boxhead[2].column_width == "30px"


def test_cols_width_mix_cases_kwargs():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    gt_tbl = GT(df).cols_width({"a": "10px"}, **{"b": "20px"}, c="30px")

    assert gt_tbl._boxhead[0].column_width == "10px"
    assert gt_tbl._boxhead[1].column_width == "20px"
    assert gt_tbl._boxhead[2].column_width == "30px"


def test_cols_width_partial_set_pct():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    gt_tbl = GT(df).cols_width({"a": "20%"})

    assert gt_tbl._boxhead[0].column_width == "20%"
    assert gt_tbl._boxhead[1].column_width == None
    assert gt_tbl._boxhead[2].column_width == None


def test_cols_width_fully_set_pct():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    gt_tbl = GT(df).cols_width({"a": "20%", "b": "20%", "c": "60%"})

    assert gt_tbl._boxhead[0].column_width == "20%"
    assert gt_tbl._boxhead[1].column_width == "20%"
    assert gt_tbl._boxhead[2].column_width == "60%"


def test_cols_width_fully_set_pct_2():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    gt_tbl = GT(df).cols_width({"a": "10%", "b": "10%", "c": "40%"})

    assert gt_tbl._boxhead[0].column_width == "10%"
    assert gt_tbl._boxhead[1].column_width == "10%"
    assert gt_tbl._boxhead[2].column_width == "40%"


def test_cols_width_html_colgroup():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    gt_tbl = GT(df).cols_width({"a": "10px", "b": "20px", "c": "30px"})

    tbl_built = gt_tbl._build_data(context="html")
    table_defs = _get_table_defs(tbl_built)

    assert (
        str(table_defs["table_colgroups"])
        == '<colgroup>\n  <col style="width:10px;"/>\n  <col style="width:20px;"/>\n  <col style="width:30px;"/>\n</colgroup>'
    )


def test_cols_width_html_colgroup_hidden():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    gt_tbl = GT(df).cols_width({"a": "10px", "b": "20px", "c": "30px"}).cols_hide(columns="b")

    tbl_built = gt_tbl._build_data(context="html")
    table_defs = _get_table_defs(tbl_built)

    assert (
        str(table_defs["table_colgroups"])
        == '<colgroup>\n  <col style="width:10px;"/>\n  <col style="width:30px;"/>\n</colgroup>'
    )


def test_cols_width_html_colgroup_stub():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    gt_tbl = GT(df, rowname_col="b").cols_width({"a": "10px", "b": "20px", "c": "30px"})

    tbl_built = gt_tbl._build_data(context="html")
    table_defs = _get_table_defs(tbl_built)

    assert (
        str(table_defs["table_colgroups"])
        == '<colgroup>\n  <col style="width:20px;"/>\n  <col style="width:10px;"/>\n  <col style="width:30px;"/>\n</colgroup>'
    )


def test_cols_width_html_colgroup_complex():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6], "d": [7, 8], "e": [9, 10]})
    gt_tbl = (
        GT(df, rowname_col="c")
        .cols_move_to_start(columns="d")
        .cols_hide(columns="a")
        .cols_width({"a": "10px", "b": "20px", "c": "30px", "d": "40px", "e": "50px"})
    )

    tbl_built = gt_tbl._build_data(context="html")
    table_defs = _get_table_defs(tbl_built)

    assert (
        str(table_defs["table_colgroups"])
        == '<colgroup>\n  <col style="width:30px;"/>\n  <col style="width:40px;"/>\n  <col style="width:20px;"/>\n  <col style="width:50px;"/>\n</colgroup>'
    )


@pytest.mark.parametrize("DF, columns", [(pd.DataFrame, "a"), (pl.DataFrame, cs.starts_with("a"))])
def test_cols_move_single_col(DF, columns):
    df = DF({"a": [1, 2], "b": [3, 4], "c": [5, 6], "d": [7, 8]})
    src_gt = GT(df)
    new_gt = cols_move(src_gt, columns=columns, after="b")
    assert [col.var for col in new_gt._boxhead] == ["b", "a", "c", "d"]


@pytest.mark.parametrize(
    "DF, columns",
    [(pd.DataFrame, ["a", "d"]), (pl.DataFrame, cs.starts_with("a") | cs.ends_with("d"))],
)
def test_cols_move_multi_cols(DF, columns):
    df = DF({"a": [1, 2], "b": [3, 4], "c": [5, 6], "d": [7, 8]})
    src_gt = GT(df)
    new_gt = cols_move(src_gt, columns=columns, after="b")
    assert [col.var for col in new_gt._boxhead] == ["b", "a", "d", "c"]


@pytest.mark.parametrize("DF, columns", [(pd.DataFrame, "c"), (pl.DataFrame, cs.starts_with("c"))])
def test_cols_move_to_start_single_col(DF, columns):
    df = DF({"a": [1, 2], "b": [3, 4], "c": [5, 6], "d": [7, 8]})
    src_gt = GT(df)
    new_gt = cols_move_to_start(src_gt, columns=columns)
    assert [col.var for col in new_gt._boxhead] == ["c", "a", "b", "d"]


@pytest.mark.parametrize(
    "DF, columns",
    [(pd.DataFrame, ["c", "d"]), (pl.DataFrame, cs.starts_with("c") | cs.ends_with("d"))],
)
def test_cols_move_to_start_multi_cols(DF, columns):
    df = DF({"a": [1, 2], "b": [3, 4], "c": [5, 6], "d": [7, 8]})
    src_gt = GT(df)
    new_gt = cols_move_to_start(src_gt, columns=columns)
    assert [col.var for col in new_gt._boxhead] == ["c", "d", "a", "b"]


@pytest.mark.parametrize("DF, columns", [(pd.DataFrame, "c"), (pl.DataFrame, cs.starts_with("c"))])
def test_cols_move_to_end_single_col(DF, columns):
    df = DF({"a": [1, 2], "b": [3, 4], "c": [5, 6], "d": [7, 8]})
    src_gt = GT(df)
    new_gt = cols_move_to_end(src_gt, columns=columns)
    assert [col.var for col in new_gt._boxhead] == ["a", "b", "d", "c"]


@pytest.mark.parametrize(
    "DF, columns",
    [(pd.DataFrame, ["a", "c"]), (pl.DataFrame, cs.starts_with("a") | cs.ends_with("c"))],
)
def test_cols_move_to_end_multi_cols(DF, columns):
    df = DF({"a": [1, 2], "b": [3, 4], "c": [5, 6], "d": [7, 8]})
    src_gt = GT(df)
    new_gt = cols_move_to_end(src_gt, columns=columns)
    assert [col.var for col in new_gt._boxhead] == ["b", "d", "a", "c"]


@pytest.mark.parametrize("DF, columns", [(pd.DataFrame, "c"), (pl.DataFrame, cs.starts_with("c"))])
def test_cols_hide_single_col(DF, columns):
    df = DF({"a": [1, 2], "b": [3, 4], "c": [5, 6], "d": [7, 8]})
    src_gt = GT(df)
    new_gt = cols_hide(src_gt, columns=columns)
    assert [col.var for col in new_gt._boxhead if col.visible] == ["a", "b", "d"]


@pytest.mark.parametrize(
    "DF, columns",
    [(pd.DataFrame, ["a", "d"]), (pl.DataFrame, cs.starts_with("a") | cs.ends_with("d"))],
)
def test_cols_hide_multi_cols(DF, columns):
    df = DF({"a": [1, 2], "b": [3, 4], "c": [5, 6], "d": [7, 8]})
    src_gt = GT(df)
    new_gt = cols_hide(src_gt, columns=columns)
    assert [col.var for col in new_gt._boxhead if col.visible] == ["b", "c"]


def test_validate_sel_cols():
    sel_cols = ["a", "b", "c"]
    col_vars = ["a", "b", "c", "d"]
    _validate_sel_cols(sel_cols, col_vars)


def test_validate_sel_cols_raises():
    sel_cols = []
    col_vars = ["a", "b", "c", "d"]
    with pytest.raises(Exception) as exc_info:
        _validate_sel_cols(sel_cols, col_vars)

    assert "No columns selected." in exc_info.value.args[0]

    sel_cols = ["a", "b", "c", "x"]
    with pytest.raises(ValueError) as exc_info:
        _validate_sel_cols(sel_cols, col_vars)

    assert (
        "All `columns` must exist and be visible in the input `data` table."
        in exc_info.value.args[0]
    )


def test_spanner_transforme_split():
    columns = ["span_1.A", "span_1.B.x"]

    # one column
    assert SpannerTransformer(columns=[columns[0]]).split() == {
        "span_1.A": ["span_1", "A"],
    }

    # multiple columns
    assert SpannerTransformer(columns=columns).split() == {
        "span_1.A": ["span_1", "A"],
        "span_1.B.x": ["span_1", "B", "x"],
    }

    # reverse
    assert SpannerTransformer(columns=columns, reverse=True).split() == {
        "span_1.A": ["A", "span_1"],
        "span_1.B.x": ["x", "B", "span_1"],
    }

    # limit
    assert SpannerTransformer(columns=columns, limit=1).split() == {
        "span_1.A": ["span_1", "A"],
        "span_1.B.x": ["span_1.B", "x"],
    }

    # limit + split
    assert SpannerTransformer(columns=columns, limit=1, split="first").split() == {
        "span_1.A": ["span_1", "A"],
        "span_1.B.x": ["span_1", "B.x"],
    }

    # limit + split + reverse
    assert SpannerTransformer(columns=columns, limit=1, split="first", reverse=True).split() == {
        "span_1.A": ["A", "span_1"],
        "span_1.B.x": ["B.x", "span_1"],
    }

    # delim
    assert SpannerTransformer(columns=columns, delim="_").split() == {
        "span_1.A": ["span", "1.A"],
        "span_1.B.x": ["span", "1.B.x"],
    }


def test_spanner_transforme_split_realistic():
    columns = [
        "pop.NL_ZH.province",
        "gdp.NL_ZH.province",
        "pop.NL_NH.province",
        "gdp.NL_NH.province",
    ]

    assert SpannerTransformer(columns=columns, reverse=True).split() == {
        "pop.NL_ZH.province": ["province", "NL_ZH", "pop"],
        "gdp.NL_ZH.province": ["province", "NL_ZH", "gdp"],
        "pop.NL_NH.province": ["province", "NL_NH", "pop"],
        "gdp.NL_NH.province": ["province", "NL_NH", "gdp"],
    }

    columns = ["pop.NL_ZH", "gdp.NL_ZH", "pop.NL_NH", "gdp.NL_NH"]
    assert SpannerTransformer(columns=columns, reverse=True).split() == {
        "pop.NL_ZH": ["NL_ZH", "pop"],
        "gdp.NL_ZH": ["NL_ZH", "gdp"],
        "pop.NL_NH": ["NL_NH", "pop"],
        "gdp.NL_NH": ["NL_NH", "gdp"],
    }


def test_spanner_transforme_get_rectangle():
    columns = ["span_1.A", "span_1.B.x"]
    assert SpannerTransformer(columns=columns).get_rectangle() == [
        columns,
        [None, "x"],
        ["A", "B"],
        ["span_1", "span_1"],
    ]

    assert SpannerTransformer(columns=columns, reverse=True).get_rectangle() == [
        columns,
        ["A", "x"],
        ["span_1", "B"],
        [None, "span_1"],
    ]
