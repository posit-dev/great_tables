from __future__ import annotations

import copy
import itertools
from typing import Literal, TYPE_CHECKING

from typing_extensions import TypeAlias

from ._boxhead import cols_label
from ._gt_data import SpannerInfo, Spanners
from ._helpers import random_id
from ._locations import resolve_cols_c
from ._tbl_data import SelectExpr
from ._text import BaseText, Text
from ._utils import OrderedSet, _assert_list_is_subset

if TYPE_CHECKING:
    from ._gt_data import Boxhead
    from ._types import GTSelf


SpannerMatrix: TypeAlias = list[dict[str, "str | None"]]


def tab_spanner(
    self: GTSelf,
    label: str | BaseText,
    columns: SelectExpr = None,
    spanners: str | list[str] | None = None,
    level: int | None = None,
    id: str | None = None,
    gather: bool = True,
    replace: bool = False,
) -> GTSelf:
    """
    Insert a spanner above a selection of column headings.

    This part of the table contains, at a minimum, column labels and, optionally, an unlimited
    number of levels for spanners. A spanner will occupy space over any number of contiguous column
    labels and it will have an associated label and ID value. This method allows for mapping to be
    defined by column names, existing spanner ID values, or a mixture of both.

    The spanners are placed in the order of calling `tab_spanner()` so if a later call uses the same
    columns in its definition (or even a subset) as the first invocation, the second spanner will be
    overlaid atop the first. Options exist for forcibly inserting a spanner underneath others (with
    `level` as space permits) and with `replace`, which allows for full or partial spanner
    replacement.

    Parameters
    ----------
    label
        The text to use for the spanner label. We can optionally use the [`md()`](`great_tables.md`)
        and [`html()`](`great_tables.html`) helper functions to style the text as Markdown or to
        retain HTML elements in the text. Alternatively, units notation can be used (see
        [`define_units()`](`great_tables.define_units`) for details).
    columns
        The columns to target. Can either be a single column name or a series of column names
        provided in a list.
    spanners
        The spanners that should be spanned over, should they already be defined. One or more
        spanner ID values (in quotes) can be supplied here. This argument works in tandem with the
        `columns` argument.
    level
        An explicit level to which the spanner should be placed. If not provided, **Great Tables**
        will choose the level based on the inputs provided within `columns` and `spanners`, placing
        the spanner label where it will fit. The first spanner level (right above the column labels)
        is `0`.
    id
        The ID for the spanner. When accessing a spanner through the `spanners` argument of
        `tab_spanner()` the `id` value is used as the reference (and not the `label`). If an `id`
        is not explicitly provided here, it will be taken from the `label` value. It is advisable to
        set an explicit `id` value if you plan to access this cell in a later call and the label
        text is complicated (e.g., contains markup, is lengthy, or both). Finally, when providing
        an `id` value you must ensure that it is unique across all ID values set for spanner labels
        (the method will throw an error if `id` isn't unique).
    gather
        An option to move the specified `columns` such that they are unified under the spanner.
        Ordering of the moved-into-place columns will be preserved in all cases. By default, this
        is set to `True`.
    replace
        Should new spanners be allowed to partially or fully replace existing spanners? (This is a
        possibility if setting spanners at an already populated `level`.) By default, this is set to
        `False` and an error will occur if some replacement is attempted.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    Let's create a table using a small portion of the `gtcars` dataset. Over several columns (`hp`,
    `hp_rpm`, `trq`, `trq_rpm`, `mpg_c`, `mpg_h`) we'll use `tab_spanner()` to add a spanner with
    the label `"performance"`. This effectively groups together several columns related to car
    performance under a unifying label.

    ```{python}
    from great_tables import GT
    from great_tables.data import gtcars

    colnames = ["model", "hp", "hp_rpm", "trq", "trq_rpm", "mpg_c", "mpg_h"]
    gtcars_mini = gtcars[colnames].head(10)

    (
        GT(gtcars_mini)
        .tab_spanner(
            label="performance",
            columns=["hp", "hp_rpm", "trq", "trq_rpm", "mpg_c", "mpg_h"]
        )
    )
    ```

    One cool feature of `tab_spanner()` is its support for multiple levels, allowing you to group
    columns in various ways. For example, you can create three bottom spanners and a top spanner:

    ```{python}
    (
        GT(gtcars_mini)
        .tab_spanner(
            label="hp",
            columns=["hp", "hp_rpm"],
        )
        .tab_spanner(
            label="trq",
            columns=["trq", "trq_rpm"],
        )
        .tab_spanner(
            label="mpg",
            columns=["mpg_c", "mpg_h"],
        )
        .tab_spanner(
            label="performance",
            columns=["hp", "hp_rpm", "trq", "trq_rpm", "mpg_c", "mpg_h"],
        )
    )
    ```

    Did you notice that the spanners stacked automatically? What if you want granular control to
    specify a spanner in a specific hierarchy? **Great Tables** has you covered. By using the `level=`
    parameter, you can easily adjust the hierarchy of spanners. For example, by specifying `level=0`
    for the last call of `tab_spanner()`, you can place that spanner at the bottom level (level `0`)
    instead of the top level (level `2`).

    ```{python}
    (
        GT(gtcars_mini)
        .tab_spanner(
            label="hp",
            columns=["hp", "hp_rpm"],
        )
        .tab_spanner(
            label="performance",
            columns=["hp", "hp_rpm", "trq", "trq_rpm"],
        )
        .tab_spanner(
            label="trq",
            columns=["trq", "trq_rpm"],
            level=0,
        )
    )
    ```

    We can also use Markdown formatting for the spanner label. In this example, we'll use
    `gt.md("*Performance*")` to make the label italicized.

    ```{python}
    (
        GT(gtcars_mini)
        .tab_spanner(
            label=md("*Performance*"),
            columns=["hp", "hp_rpm", "trq", "trq_rpm", "mpg_c", "mpg_h"]
        )
    )
    ```
    """
    from great_tables._helpers import UnitStr

    crnt_spanner_ids = set([span.spanner_id for span in self._spanners])

    if id is None:
        # The label may contain HTML or Markdown, so we need to extract
        # it from the Text object
        if isinstance(label, Text):
            id = label.text
        else:
            id = label

    if isinstance(columns, (str, int)):
        columns = [columns]
    elif columns is None:
        columns = []

    if isinstance(spanners, (str, int)):
        spanners = [spanners]
    elif spanners is None:
        spanners = []

    # validations ----
    if level is not None and level < 0:
        raise ValueError(f"Level may not be negative. Received {level}.")
    if id in crnt_spanner_ids:
        raise ValueError(f"Spanner id {id} already exists.")

    # select columns ----

    selected_column_names = resolve_cols_c(data=self, expr=columns, null_means="nothing") or []

    # select spanner ids ----
    # TODO: this supports tidyselect
    # TODO: could we use something like resolve_vector_l
    if spanners is not None:
        assert set(spanners).issubset(set(crnt_spanner_ids))
        spanner_ids = spanners
    else:
        spanner_ids = []

    # Check that we've selected something explicitly
    if not len(selected_column_names) and not len(spanner_ids):
        # TODO: null_means is unimplemented
        raise NotImplementedError("columns/spanners must be specified")

    # get column names associated with selected spanners ----
    _vars = [span.vars for span in self._spanners if span.spanner_id in spanner_ids]
    spanner_column_names = OrderedSet(itertools.chain(*_vars)).as_list()

    column_names = OrderedSet([*selected_column_names, *spanner_column_names]).as_list()
    # combine columns names and those from spanners ----

    # get spanner level ----
    if level is None:
        level = self._spanners.next_level(list(column_names))

    # get spanner units and labels ----
    # TODO: grep units from {{.*}}, may need to switch delimiters
    spanner_units = None
    spanner_pattern = None

    # Handle units syntax in the label (e.g., "Density ({{ppl / mi^2}})")
    if isinstance(label, str):
        unitstr = UnitStr.from_str(label)

        if len(unitstr.units_str) == 1 and isinstance(unitstr.units_str[0], str):
            new_label = unitstr.units_str[0]
        else:
            new_label = unitstr

    elif isinstance(label, BaseText):
        new_label = label

    else:
        raise ValueError(
            "Spanner labels must be strings or Text objects. Use `md()` or `html()` for formatting."
        )

    new_span = SpannerInfo(
        spanner_id=id,
        spanner_level=level,
        vars=column_names,
        spanner_units=spanner_units,
        spanner_pattern=spanner_pattern,
        spanner_label=new_label,
    )

    spanners = self._spanners.append_entry(new_span)
    new_data = self._replace(_spanners=spanners)

    if gather and not len(spanner_ids) and level == 0 and column_names:
        return cols_move(new_data, columns=column_names, after=column_names[0])

    return new_data


class SpannerTransformer:
    """
    https://github.com/posit-dev/great-tables/pull/604
    """

    def __init__(
        self,
        columns: list[str],
        delim: str = ".",
        split: Literal["first", "last"] = "last",
        limit: int = -1,
        reverse: bool = False,
    ):
        self._columns = columns
        self._delim = delim
        self._split = split
        self._limit = limit
        self._reverse = reverse

        self._split_func = self._get_split_func()
        self._d: dict[str, list[str]] = {}
        self._rectangle: list[list[str]] = []

    def _get_split_func(self):
        if self._split == "first":
            split_ = "split"
        elif self._split == "last":
            split_ = "rsplit"
        else:
            raise ValueError("The `split=` parameter accepts only `first` or `last` as input.")
        return getattr(str, split_)

    def split(self):
        if not self._d:
            for col in self._columns:
                col_names = self._split_func(col, self._delim, self._limit)  # split for one column
                if self._reverse:
                    col_names = col_names[::-1]
                self._d[col] = col_names
        return self._d

    def get_rectangle(self):
        if not self._rectangle:
            d = self.split()  # get the intermediate representation
            values = [list(v) for v in itertools.zip_longest(*d.values())]
            if self._reverse:
                self._rectangle = [list(d.keys()), *values]
            else:
                self._rectangle = [list(d.keys()), *values[::-1]]
        return self._rectangle

    def __repr__(self):
        cls_name = type(self).__name__
        return (
            f"{cls_name}(columns={self._columns!r}, delim={self._delim!r}, "
            + f"split={self._split!r}, limit={self._limit}, reverse={self._reverse})"
        )


def tab_spanner_delim(
    self: GTSelf,
    delim: str = ".",
    columns: SelectExpr = None,
    split: Literal["first", "last"] = "last",
    limit: int = -1,
    reverse: bool = False,
) -> GTSelf:
    """
    `tab_spanner_delim()` can take specially-crafted column names and generate one or more spanners
    (and revise column labels at the same time). This is done by splitting the column name by the
    specified delimiter text (delim) and placing the fragments from top to bottom (i.e.,
    higher-level spanners to the column labels) or vice versa. Furthermore, neighboring text
    fragments on different spanner levels that have the same text will be coalesced together.
    For instance, having the three side-by-side column names rating_1, rating_2, and rating_3 will
    (in the default case at least) result in a spanner with the label "rating" above columns with
    the labels "1", "2", and "3".

    Parameters
    ----------
    delim
        Delimiter for splitting, default to `"."`.

    columns
        The columns to target. Can either be a single column name or a series of column names
        provided in a list.

    split
        Should the delimiter splitting occur from the "last" instance of the delim character or
        from the "first"? The default here uses the "last" keyword, and splitting begins at the
        last instance of the delimiter in the column name. This option only has some consequence
        when there is a limit value applied that is lesser than the number of delimiter characters
        for a given column name (i.e., number of splits is not the maximum possible number).

    limit
        Limit for splitting. An optional limit to place on the splitting procedure. The default -1
        means that a column name will be split as many times are there are delimiter characters.
        In other words, the default means there is no limit. If an integer value is given to limit
        then splitting will cease at the iteration given by limit. This works in tandem with split
        since we can adjust the number of splits from either the right side (split = "last") or
        left side (split = "first") of the column name.

    reverse
        Should the order of split names be reversed? By default, this is `False`.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    Let's create a table table that includes the column names province.NL_ZH.pop, province.NL_ZH.gdp,
    province.NL_NH.pop, and province.NL_NH.gdp, we can see that we have a naming system that has
    a well-defined structure. We start with the more general to the left ("province") and move to
    the more specific on the right ("pop"). If the columns are in the table in this exact order,
    then things are in an ideal state as the eventual spanner labels will form from this neighboring.
    When using tab_spanner_delim() here with delim set as "." we get the following table:

    ```{python}
    import polars as pl
    from great_tables import GT

    data = {
        "province.NL_ZH.pop": [1, 2, 3],
        "province.NL_ZH.gdp": [4, 5, 6],
        "province.NL_NH.pop": [7, 8, 9],
        "province.NL_NH.gdp": [10, 11, 12],
    }

    gt = GT(pl.DataFrame(data))
    gt.tab_spanner_delim()
    ```
    """

    sel_cols = resolve_cols_c(data=self, expr=columns)

    spter = SpannerTransformer(
        delim=delim, columns=sel_cols, split=split, limit=limit, reverse=reverse
    )
    col_names, first_col, *other_cols = spter.get_rectangle()

    new_obj = copy.copy(self)

    # for `first_col`, call `.cols_label()`
    new_obj = cols_label(new_obj, dict(zip(col_names, first_col)))

    # for `other_cols`, call `.tab_spanner()`
    for level, col_labels in enumerate(other_cols, start=1):
        for col_name, col_label in zip(col_names, col_labels):
            new_obj = tab_spanner(
                new_obj,
                label=col_label,
                columns=col_name,
                level=level,
                id=random_id(),  # good?
            )
    return new_obj


def _validate_sel_cols(sel_cols: list[str], col_vars: list[str]) -> None:
    if not len(sel_cols):
        raise Exception("No columns selected.")
    elif not all(col in col_vars for col in sel_cols):
        raise ValueError("All `columns` must exist and be visible in the input `data` table.")


def cols_move(self: GTSelf, columns: SelectExpr, after: str) -> GTSelf:
    """Move one or more columns.

    On those occasions where you need to move columns this way or that way, we can make use of the
    `cols_move()` method. While it's true that the movement of columns can be done upstream of
    **Great Tables**, it is much easier and less error prone to use the method provided here. The
    movement procedure here takes one or more specified columns (in the `columns` argument) and
    places them to the right of a different column (the `after` argument). The ordering of the
    `columns` to be moved is preserved, as is the ordering of all other columns in the table.

    The columns supplied in `columns` must all exist in the table and none of them can be in the
    `after` argument. The `after` column must also exist and only one column should be provided
    here. If you need to place one more or columns at the beginning of the column series, the
    `cols_move_to_start()` method should be used. Similarly, if those columns to move should be
    placed at the end of the column series then use `cols_move_to_end()`.

    Parameters
    ----------
    columns
        The columns to target. Can either be a single column name or a series of column names
        provided in a list.
    after
        The column after which the `columns` should be placed. This can be any column name that
        exists in the table.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    Let's use the `countrypops` dataset to create a table. We'll choose to position the `population`
    column after the `country_name` column by using the `cols_move()` method.

    ```{python}
    from great_tables import GT
    from great_tables.data import countrypops

    countrypops_mini = countrypops.loc[countrypops["country_name"] == "Japan"][
        ["country_name", "year", "population"]
    ].tail(5)

    (
        GT(countrypops_mini)
        .cols_move(
            columns="population",
            after="country_name"
        )
    )
    ```
    """

    # If `columns` is a string, convert it to a list
    if isinstance(columns, str):
        columns = [columns]

    sel_cols = resolve_cols_c(data=self, expr=columns)

    sel_after = resolve_cols_c(data=self, expr=[after])

    col_vars = [col.var for col in self._boxhead]

    if not len(sel_after):
        raise ValueError(f"Column {after} not found in table.")
    elif len(sel_after) > 1:
        raise ValueError(
            f"Only 1 value should be supplied to `after`, recieved argument: {sel_after}"
        )

    _validate_sel_cols(sel_cols, col_vars)

    moving_columns = [col for col in sel_cols if col not in sel_after]
    other_columns = [col for col in col_vars if col not in moving_columns]

    indx = other_columns.index(after)
    final_vars = [
        *other_columns[: indx + 1],
        *moving_columns,
        *other_columns[indx + 1 :],
    ]

    new_boxhead = self._boxhead.reorder(final_vars)
    return self._replace(_boxhead=new_boxhead)


def cols_move_to_start(self: GTSelf, columns: SelectExpr) -> GTSelf:
    """Move one or more columns to the start.

    We can easily move set of columns to the beginning of the column series and we only need to
    specify which `columns`. It's possible to do this upstream of **Great Tables**, however, it is
    easier with this method and it presents less possibility for error. The ordering of the
    `columns` that are moved to the start is preserved (same with the ordering of all other columns
    in the table).

    The columns supplied in `columns` must all exist in the table. If you need to place one or
    columns at the end of the column series, the `cols_move_to_end()` method should be used. More
    control is offered with the `cols_move()` method, where columns could be placed after a specific
    column.

    Parameters
    ----------
    columns
        The columns to target. Can either be a single column name or a series of column names
        provided in a list.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    For this example, we'll use a portion of the `countrypops` dataset to create a simple table.
    Let's move the `year` column, which is the middle column, to the start of the column series with
    the `cols_move_to_start()` method.

    ```{python}
    from great_tables import GT
    from great_tables.data import countrypops

    countrypops_mini = countrypops.loc[countrypops["country_name"] == "Fiji"][
        ["country_name", "year", "population"]
    ].tail(5)

    GT(countrypops_mini).cols_move_to_start(columns="year")
    ```

    We can also move multiple columns at a time. With the same `countrypops`-based table
    (`countrypops_mini`), let's move both the `year` and `population` columns to the start of the
    column series.

    ```{python}
    GT(countrypops_mini).cols_move_to_start(columns=["year", "population"])
    ```
    """

    # If `columns` is a string, convert it to a list
    if isinstance(columns, str):
        columns = [columns]

    sel_cols = resolve_cols_c(data=self, expr=columns)

    col_vars = [col.var for col in self._boxhead]

    _validate_sel_cols(sel_cols, col_vars)

    moving_columns = [col for col in sel_cols]
    other_columns = [col for col in col_vars if col not in moving_columns]

    final_vars = [*moving_columns, *other_columns]

    new_boxhead = self._boxhead.reorder(final_vars)
    return self._replace(_boxhead=new_boxhead)


def cols_move_to_end(self: GTSelf, columns: SelectExpr) -> GTSelf:
    """Move one or more columns to the end.

    We can easily move set of columns to the beginning of the column series and we only need to
    specify which `columns`. It's possible to do this upstream of **Great Tables**, however, it is
    easier with this method and it presents less possibility for error. The ordering of the
    `columns` that are moved to the end is preserved (same with the ordering of all other columns in
    the table).

    Parameters
    ----------
    columns
        The columns to target. Can either be a single column name or a series of column names
        provided in a list.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    For this example, we'll use a portion of the `countrypops` dataset to create a simple table.
    Let's move the `year` column, which is the middle column, to the end of the column series with
    the `cols_move_to_end()` method.

    ```{python}
    from great_tables import GT
    from great_tables.data import countrypops

    countrypops_mini = countrypops.loc[countrypops["country_name"] == "Benin"][
        ["country_name", "year", "population"]
    ].tail(5)

    GT(countrypops_mini).cols_move_to_end(columns="year")
    ```

    We can also move multiple columns at a time. With the same `countrypops`-based table
    (`countrypops_mini`), let's move both the `year` and `country_name` columns to the end of the
    column series.

    ```{python}
    GT(countrypops_mini).cols_move_to_end(columns=["year", "country_name"])
    ```
    """

    # If `columns` is a string, convert it to a list
    if isinstance(columns, str):
        columns = [columns]

    sel_cols = resolve_cols_c(data=self, expr=columns)

    col_vars = [col.var for col in self._boxhead]

    _validate_sel_cols(sel_cols, col_vars)

    moving_columns = [col for col in sel_cols]
    other_columns = [col for col in col_vars if col not in moving_columns]

    final_vars = [*other_columns, *moving_columns]

    new_boxhead = self._boxhead.reorder(final_vars)
    return self._replace(_boxhead=new_boxhead)


def cols_hide(self: GTSelf, columns: SelectExpr) -> GTSelf:
    """Hide one or more columns.

    The `cols_hide()` method allows us to hide one or more columns from appearing in the final
    output table. While it's possible and often desirable to omit columns from the input table data
    before introduction to the `GT()` class, there can be cases where the data in certain columns is
    useful (as a column reference during formatting of other columns) but the final display of those
    columns is not necessary.

    Parameters
    ----------
    columns
        The columns to hide in the output display table. Can either be a single column name or a
        series of column names provided in a list.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.


    Examples
    --------
    For this example, we'll use a portion of the `countrypops` dataset to create a simple table.
    Let's hide the `year` column with the `cols_hide()` method.

    ```{python}
    from great_tables import GT
    from great_tables.data import countrypops

    countrypops_mini = countrypops.loc[countrypops["country_name"] == "Benin"][
        ["country_name", "year", "population"]
    ].tail(5)

    GT(countrypops_mini).cols_hide(columns="year")
    ```

    Details
    -------
    The hiding of columns is internally a rendering directive, so, all columns that are 'hidden' are
    still accessible and useful in any expression provided to a `rows` argument. Furthermore, the
    `cols_hide()` method (as with many of the methods available in **Great Tables**) can be placed
    anywhere in a chain of calls (acting as a promise to hide columns when the timing is right).
    However there's perhaps greater readability when placing this call closer to the end of such a
    chain. The `cols_hide()` method quietly changes the visible state of a column and doesn't yield
    warnings when changing the state of already-invisible columns.
    """

    # If `columns` is a string, convert it to a list
    if isinstance(columns, str):
        columns = [columns]

    sel_cols = resolve_cols_c(data=self, expr=columns)

    col_vars = [col.var for col in self._boxhead]

    _validate_sel_cols(sel_cols, col_vars)

    # New boxhead with hidden columns
    new_boxhead = self._boxhead.set_cols_hidden(sel_cols)

    return self._replace(_boxhead=new_boxhead)


def spanners_print_matrix(
    spanners: Spanners,
    boxhead: Boxhead,
    include_hidden: bool = False,
    ids: bool = False,
    omit_columns_row: bool = False,
) -> tuple[SpannerMatrix, list[str]]:
    if include_hidden:
        vars = [row.var for row in boxhead if not row.is_stub]
    else:
        vars = [row.var for row in boxhead if not row.is_stub and row.visible]

    if not spanners:
        return empty_spanner_matrix(vars=vars, omit_columns_row=omit_columns_row)

    # Modify `spanners_tbl` such that:
    # (1) only visible vars are included in the `vars` column
    # (2) entries with no vars (after step 1) are removed, and
    # (3) `spanner_level` values have all gaps removed, being compressed
    #     down to start at 1 (e.g., 7, 5, 3, 1 -> 4, 3, 2, 1)
    _vars = [set(span.vars) & set(vars) for span in spanners]
    _lvls = sorted({span.spanner_level for span in spanners})

    non_empty_spans = [span for crnt_vars, span in zip(_vars, spanners) if len(crnt_vars)]
    new_levels = [_lvls.index(span.spanner_level) for span in non_empty_spans]
    crnt_spans = Spanners(non_empty_spans).relevel(new_levels)

    if not crnt_spans:
        return empty_spanner_matrix(vars=vars, omit_columns_row=omit_columns_row)

    spanner_height = len(_lvls)
    # TODO: span.built can be None. When does it get set?
    spanner_reprs = [span.spanner_id if ids else span.built_label() for span in crnt_spans]

    # Create a matrix with dimension spanner_height x vars (e.g. presented columns)
    label_matrix: SpannerMatrix = [
        {var_name: None for var_name in vars} for _ in range(spanner_height)
    ]

    for span_ii, span in enumerate(crnt_spans):
        for var in span.vars:
            # This if clause skips spanned columns that are not in the
            # boxhead vars we are planning to use (e.g. not in the visible ones
            # or in the stub).
            if var in label_matrix[span.spanner_level]:
                label_matrix[span.spanner_level][var] = spanner_reprs[span_ii]

    # reverse order , so if you were to print it out, level 0 would appear on the bottom
    label_matrix.reverse()

    # add column names to matrix
    if not omit_columns_row:
        label_matrix.append({var: var for var in vars})

    return label_matrix, vars


def empty_spanner_matrix(
    vars: list[str], omit_columns_row: bool
) -> tuple[SpannerMatrix, list[str]]:
    if omit_columns_row:
        return [], vars

    return [{var: var for var in vars}], vars


def cols_width(self: GTSelf, cases: dict[str, str] | None = None, **kwargs: str) -> GTSelf:
    """Set the widths of columns.

    Manual specifications of column widths can be performed using the `cols_width()` method. We
    choose which columns get specific widths. This can be in units of pixels or as percentages.
    Width assignments are supplied inside of a dictionary where columns are the keys and the
    corresponding width is the value.

    Parameters
    ----------
    cases
        A dictionary where the keys are column names and the values are the widths. Widths can be
        specified in pixels (e.g., `"50px"`) or as percentages (e.g., `"20%"`).

    **kwargs
        Keyword arguments to specify column widths. Each keyword corresponds to a column name, with
        its value indicating the width in pixels or percentages.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    Let's use select columns from the `exibble` dataset to create a new table. We can specify the
    widths of columns with `cols_width()`. This is done by specifying the exact widths for table
    columns in a dictionary. In this example, we'll set the width of the `num` column to `"150px"`,
    the `char` column to `"100px"`, the `date` column to `"300px"`. All other columns won't be
    affected (their widths will be automatically set by their content).

    ```{python}
    from great_tables import GT, exibble

    exibble_mini = exibble[["num", "char", "date", "datetime", "row"]].head(5)

    (
        GT(exibble_mini)
        .cols_width(
            cases={
                "num": "150px",
                "char": "100px",
                "date": "300px"
            }
        )
    )
    ```

    We can also specify the widths of columns as percentages. In this example, we'll set the width
    of the `num` column to `"20%"`, the `char` column to `"10%"`, and the `date` column to `"30%"`.
    Note that the percentages are relative and don't need to sum to 100%.

    ```{python}
    (
        GT(exibble_mini)
        .cols_width(
            cases={
                "num": "20%",
                "char": "10%",
                "date": "30%"
            }
        )
    )
    ```

    We can also mix and match pixel and percentage widths. In this example, we'll set the width of
    the `num` column to `"150px"`, the `char` column to `"10%"`, and the `date` column to `"30%"`.

    ```{python}
    (
        GT(exibble_mini)
        .cols_width(
            cases={
                "num": "150px",
                "char": "10%",
                "date": "30%"
            }
        )
    )
    ```

    If we set the width of all columns, the table will be forced to use the specified widths (i.e.,
    a column width less than the content width will be honored). In this next example, we'll set
    widths for all columns. This is a good way to ensure that the widths you specify are fully
    respected (and not overridden by automatic width calculations).

    ```{python}
    (
        GT(exibble_mini)
        .cols_width(
            cases={
                "num": "30px",
                "char": "100px",
                "date": "100px",
                "datetime": "200px",
                "row": "50px"
            }
        )
    )
    ```

    Notice that in the above example, the `num` column is very small (only `30px`) and the content
    overflows. When not specifying the width of all columns, the table will automatically adjust the
    column widths based on the content (and you wouldn't get the overflowing behavior seen in the
    previous example).
    """
    cases = cases if cases is not None else {}
    new_cases = cases | kwargs

    # If nothing is provided, return `data` unchanged
    if len(new_cases) == 0:
        return self

    curr_boxhead = self._boxhead

    # Get the full list of column names for the data
    column_names = curr_boxhead._get_columns()
    mod_columns = list(new_cases.keys())

    # Stop function if any of the column names specified are not in `cols_width`
    # msg: "All column names provided must exist in the input `.data` table."
    _assert_list_is_subset(mod_columns, set_list=column_names)

    for col, width in new_cases.items():
        curr_boxhead = curr_boxhead._set_column_width(col, width)

    return self._replace(_boxhead=curr_boxhead)
