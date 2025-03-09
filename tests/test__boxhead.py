import great_tables as gt
import pandas as pd
import polars as pl
import pytest
from polars import selectors as cs


def test_cols_label_relabel_columns():
    # Create a table with default column labels
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    table = gt.GT(df)

    # Relabel the columns
    modified_table = table.cols_label(A="Column 1", B="Column 2")

    # Check that the column labels have been updated
    assert modified_table._boxhead._get_column_labels() == ["Column 1", "Column 2"]


def test_cols_label_relabel_columns_with_markdown():
    # Create a table with default column labels
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    table = gt.GT(df)

    # Relabel a column with a Markdown formatted label
    modified_table = table.cols_label(A=gt.md("*Column 1*"))

    # Check that the column label has been updated with Markdown formatting
    modified_column_labels = modified_table._boxhead._get_column_labels()

    assert modified_column_labels[0].text == "*Column 1*"
    assert modified_column_labels[1] == "B"


def test_cols_label_return_type():
    # Create a table with default column labels
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    table = gt.GT(df)

    # Call cols_label() with changes
    modified_table = table.cols_label(A="Column 1", B="Column 2")

    # Check that the return type is GT
    assert isinstance(modified_table, gt.GT)


def test_cols_label_return_self_if_no_kwargs():
    # Create a table with default column labels
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    table = gt.GT(df)

    # Call cols_label() without changes
    unmodified_table = table.cols_label()

    # Check that the return type is GT
    assert isinstance(unmodified_table, gt.GT)


def test_cols_label_with_relabel_columns():
    # Create a table with default column labels
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    table = gt.GT(df)

    # Relabel the columns
    modified_table = table.cols_label_with(converter=str.lower)

    # Check that the column labels have been updated
    assert modified_table._boxhead._get_column_labels() == ["a", "b"]


@pytest.mark.parametrize(
    "converter",
    [
        pl.col("my_col", "my_col2").name.to_uppercase(),
        pl.col(["my_col", "my_col2"]).name.to_uppercase(),
        cs.by_name("my_col", "my_col2").name.to_uppercase(),
        cs.by_name(["my_col", "my_col2"]).name.to_uppercase(),
        cs.starts_with("my").name.to_uppercase(),
        [cs.by_name("my_col").name.to_uppercase(), cs.by_name("my_col2").name.to_uppercase()],
        [pl.col("my_col").name.to_uppercase(), cs.by_name("my_col2").name.to_uppercase()],
        [cs.all().name.suffix("_suffix"), cs.all().name.to_uppercase()],  # test for last one wins
        pl.col("my_col2", "my_col").name.to_uppercase(),  # test for column positions
    ],
)
def test_cols_label_with_relabel_columns_polars(converter):
    # Create a table with default column labels
    df = pl.DataFrame({"my_col": [1, 2, 3], "my_col2": [4, 5, 6]})
    table = gt.GT(df)

    # Relabel the columns
    modified_table = table.cols_label_with(converter=converter)

    # Check that the column labels have been updated
    assert modified_table._boxhead._get_column_labels() == ["MY_COL", "MY_COL2"]


def test_cols_label_with_relabel_columns_with_markdown():
    # Create a table with default column labels
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    table = gt.GT(df)

    # Relabel a column with a Markdown formatted label
    modified_table = table.cols_label_with("A", lambda x: gt.md(f"**{x}**"))

    # Check that the column label has been updated with Markdown formatting
    modified_column_labels = modified_table._boxhead._get_column_labels()

    assert modified_column_labels[0].text == "**A**"
    assert modified_column_labels[1] == "B"


def test_cols_label_with_raises():
    # Create a table with default column labels
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    table = gt.GT(df)

    with pytest.raises(ValueError) as exc_info:
        table.cols_label_with()

    assert (
        "Must provide the `converter=` parameter to use `cols_label_with()`."
        in exc_info.value.args[0]
    )


def test_cols_align_default():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    table = gt.GT(df)

    # Make sure default align is "left"
    aligned_table = table.cols_align()
    all_column_align = [x.column_align for x in aligned_table._boxhead._d]

    # Check that all columns align "left"
    assert all_column_align == ["left", "left"]


def test_cols_align_columns_str():
    df = pl.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7.1, 8.2, 9.3]})
    table = gt.GT(df)

    # Select columns by a list of column names
    aligned_table = table.cols_align(align="center", columns="B")
    all_column_align = [x.column_align for x in aligned_table._boxhead._d]

    assert all_column_align == [
        "right",  # `auto_align` for `int` is "right"
        "center",  # manually assign
        "right",  # `auto_align` for `float` is "right"
    ]


def test_cols_align_columns_list_of_str():
    df = pl.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7.1, 8.2, 9.3]})
    table = gt.GT(df)

    # Select columns by a list of column names
    aligned_table = table.cols_align(align="left", columns=["A"])
    all_column_align = [x.column_align for x in aligned_table._boxhead._d]

    assert all_column_align == [
        "left",  # manually assign
        "right",  # `auto_align` for `int` is "right"
        "right",  # `auto_align` for `float` is "right"
    ]


def test_cols_align_pl_expr():
    df = pl.DataFrame({"col1": [1, 2], "col2": [3.3, 4.4], "c": ["x", "y"]}).with_columns(
        pl.col("col1").cast(pl.UInt8).alias("d")
    )
    table = gt.GT(df)

    # Select columns by polars expressions
    aligned_table = table.cols_align(align="center", columns=cs.starts_with("col"))
    all_column_align = [x.column_align for x in aligned_table._boxhead._d]

    assert all_column_align == [
        "center",  # manually assign
        "center",  # manually assign
        "left",  # `auto_align` for `str` is "left"
        "right",  # `auto_align` for `pl.UInt` is "right"
    ]


def test_cols_align_raises():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    table = gt.GT(df)

    # Make sure `align="align"` will raise `ValueError`
    with pytest.raises(ValueError) as exc_info:
        table.cols_align(align="align")

    assert "Align must be one of 'left', 'center', or 'right'." in exc_info.value.args[0]


def test_cols_align_return_type():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    table = gt.GT(df)

    aligned_table = table.cols_label()

    # Check that the return type is GT
    assert isinstance(aligned_table, gt.GT)
