from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from ._locations import resolve_cols_c
from ._utils import _assert_list_is_subset, _handle_units_syntax
from ._tbl_data import SelectExpr
from ._text import BaseText

if TYPE_CHECKING:
    from ._types import GTSelf


def cols_label(
    self: GTSelf, cases: dict[str, str | BaseText] | None = None, **kwargs: str | BaseText
) -> GTSelf:
    """
    Relabel one or more columns.

    There are three important pieces to labelling:

    * Each argument has the form: {name in data} = {new label}.
    * Multiple columns may be given the same label.
    * Labels may use curly braces to apply special formatting, called unit notation.
      For example, "area ({{ft^2}})" would appear as "area (ft²)".

    See [`define_units()`](`great_tables.define_units`) for details on unit notation.

    Parameters
    ----------
    cases
        A dictionary where the keys are column names and the values are the labels. Labels may use
        [`md()`](`great_tables.md`) or [`html()`](`great_tables.html`) helpers for formatting.

    **kwargs
        Keyword arguments to specify column labels. Each keyword corresponds to a column name, with
        its value indicating the new label.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Notes
    -----
    GT always selects columns using their name in the underlying data. This means that a column's
    label is purely for final presentation.

    Examples
    --------

    The example below relabels columns from the `countrypops` data to start with uppercase.

    ```{python}
    from great_tables import GT
    from great_tables.data import countrypops

    countrypops_mini = countrypops.loc[countrypops["country_name"] == "Uganda"][
        ["country_name", "year", "population"]
    ].tail(5)

    (
        GT(countrypops_mini)
        .cols_label(
            country_name="Country Name",
            year="Year",
            population="Population"
        )
    )
    ```

    Note that we supplied the name of the column as the key, and the new label as the value.

    We can also use Markdown formatting for the column labels. In this example, we'll use
    `md("*Population*")` to make the label italicized.

    ```{python}
    from great_tables import GT, md
    from great_tables.data import countrypops

    (
        GT(countrypops_mini)
        .cols_label(
            country_name="Name",
            year="Year",
            population=md("*Population*")
        )
    )
    ```

    We can also use unit notation to format the column labels. In this example, we'll use
    `{{cm^3 molecules^-1 s^-1}}` for part of the label for the `OH_k298` column.

    ```{python}
    from great_tables import GT
    from great_tables.data import reactions
    import polars as pl

    reactions_mini = (
        pl.from_pandas(reactions)
        .filter(pl.col("cmpd_type") == "mercaptan")
        .select(["cmpd_name", "OH_k298"])
    )

    (
        GT(reactions_mini)
        .fmt_scientific("OH_k298")
        .sub_missing()
        .cols_label(
            cmpd_name="Compound Name",
            OH_k298="OH, {{cm^3 molecules^-1 s^-1}}",
        )
    )
    ```
    """
    cases = cases if cases is not None else {}
    new_cases = cases | kwargs

    # If nothing is provided, return `data` unchanged
    if len(new_cases) == 0:
        return self

    # Get the full list of column names for the data
    column_names = self._boxhead._get_columns()
    mod_columns = list(new_cases.keys())

    # Stop function if any of the column names specified are not in `cols_labels`
    # msg: "All column names provided must exist in the input `.data` table."
    _assert_list_is_subset(mod_columns, set_list=column_names)

    # Handle units syntax in labels (e.g., "Density ({{ppl / mi^2}})")
    new_kwargs = _handle_units_syntax(new_cases)

    boxhead = self._boxhead._set_column_labels(new_kwargs)

    return self._replace(_boxhead=boxhead)


def cols_label_with(
    self: GTSelf, columns: SelectExpr = None, fn: Callable[[str], str] | None = None
) -> GTSelf:
    """
    Relabel one or more columns using a function.

    The `cols_label_with()` function allows for modification of column labels through a supplied
    function. By default, the function will be invoked on all column labels but this can be limited
    to a subset via the `columns` parameter.

    Parameters
    ----------
    columns
        The columns to target. Can either be a single column name or a series of column names
        provided in a list.
    fn
        A function that accepts a column label as input and returns a transformed label as output.


    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Notes
    -----
    GT always selects columns using their name in the underlying data. This means that a column's
    label is purely for final presentation.

    Examples
    --------
    Let's use a subset of the `sp500` dataset to create a gt table.
    ```{python}
    from great_tables import GT, md
    from great_tables.data import sp500

    gt = GT(sp500.head())
    gt
    ```

    We can pass `str.upper()` to the `columns` parameter to convert all column labels to uppercase.
    ```{python}
    gt.cols_label_with(fn=str.upper)
    ```

    One useful use case is using `md()`, provided by **Great Tables**, to format column labels.
    For example, the following code demonstrates how to make the `date` and `adj_close` column labels
    bold using markdown syntax.
    ```{python}
    gt.cols_label_with(["date", "adj_close"], lambda x: md(f"**{x}**"))
    ```

    """
    if fn is None:
        raise ValueError("Must provide the `fn=` parameter to use `cols_label_with()`.")

    # Get the full list of column names for the data
    column_names = self._boxhead._get_columns()

    if isinstance(columns, str):
        columns = [columns]
        _assert_list_is_subset(columns, set_list=column_names)
    elif columns is None:
        columns = column_names

    sel_cols = resolve_cols_c(data=self, expr=columns)

    new_cases = {col: fn(col) for col in sel_cols}

    boxhead = self._boxhead._set_column_labels(new_cases)

    return self._replace(_boxhead=boxhead)


def cols_align(self: GTSelf, align: str = "left", columns: SelectExpr = None) -> GTSelf:
    """
    Set the alignment of one or more columns.

    The `cols_align()` method sets the alignment of one or more columns. The `align` argument
    can be set to one of `"left"`, `"center"`, or `"right"` and the `columns` argument can be
    used to specify which columns to apply the alignment to. If `columns` is not specified, the
    alignment is applied to all columns.

    Parameters
    ----------
    align
        The alignment to apply. Must be one of `"left"`, `"center"`, or `"right"`.
    columns
        The columns to target. Can either be a single column name or a series of column names
        provided in a list. If `None`, the alignment is applied to all columns.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    Let's use the `countrypops` to create a small table. We can change the alignment of the
    `population` column with `cols_align()`. In this example, the column label and body cells of
    `population` will be aligned to the left.

    ```{python}
    from great_tables import GT
    from great_tables.data import countrypops

    countrypops_mini = countrypops.loc[countrypops["country_name"] == "San Marino"][
        ["country_name", "year", "population"]
    ].tail(5)

    (
        GT(countrypops_mini, rowname_col="year", groupname_col="country_name")
        .cols_align(align="left", columns="population")
    )
    ```

    """

    # Throw if `align` is not one of the three allowed values
    if align not in ["left", "center", "right"]:
        raise ValueError("Align must be one of 'left', 'center', or 'right'.")

    # Get the full list of column names for the data
    column_names = self._boxhead._get_columns()

    # Upgrade `columns` to a list if `columns` is a string and not None
    if isinstance(columns, str):
        columns = [columns]
        _assert_list_is_subset(columns, set_list=column_names)
    elif columns is None:
        columns = column_names

    sel_cols = resolve_cols_c(data=self, expr=columns)

    # Set the alignment for each column
    return self._replace(_boxhead=self._boxhead._set_column_aligns(sel_cols, align=align))
