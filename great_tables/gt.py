from __future__ import annotations

from typing import Any

from typing_extensions import Self

from great_tables._gt_data import GTData

# Main gt imports ----
from great_tables._body import body_reassemble
from great_tables._boxhead import cols_align, cols_label
from great_tables._data_color import data_color, data_color_mpl
from great_tables._export import as_raw_html, save
from great_tables._formats import (
    fmt,
    fmt_bytes,
    fmt_currency,
    fmt_date,
    fmt_datetime,
    fmt_image,
    fmt_integer,
    fmt_markdown,
    fmt_nanoplot,
    fmt_number,
    fmt_percent,
    fmt_roman,
    fmt_scientific,
    fmt_time,
    fmt_units,
)
from great_tables._heading import tab_header
from great_tables._helpers import random_id
from great_tables._modify_rows import (
    row_group_order,
    tab_stub,
    with_id,
    with_locale,
)
from great_tables._options import (
    opt_align_table_header,
    opt_all_caps,
    opt_footnote_marks,
    opt_horizontal_padding,
    opt_row_striping,
    opt_stylize,
    opt_table_outline,
    opt_vertical_padding,
    tab_options,
)
from great_tables._render import infer_render_env_defaults
from great_tables._source_notes import tab_source_note
from great_tables._spanners import (
    cols_hide,
    cols_move,
    cols_move_to_end,
    cols_move_to_start,
    cols_width,
    tab_spanner,
)
from great_tables._stub import reorder_stub_df
from great_tables._stubhead import tab_stubhead
from great_tables._substitution import sub_missing, sub_zero
from great_tables._tab_create_modify import tab_style
from great_tables._tbl_data import _get_cell, n_rows
from great_tables._utils_render_html import (
    _get_table_defs,
    create_body_component_h,
    create_columns_component_h,
    create_footnotes_component_h,
    create_heading_component_h,
    create_source_notes_component_h,
)

__all__ = ["GT"]


# =============================================================================
# GT class
# =============================================================================
class GT(
    GTData,
):
    """
    Create a **Great Tables** object.

    The `GT()` class creates the `GT` object when provided with tabular data. Using this class is
    the the first step in a typical **Great Tables** workflow. Once we have this object, we can
    take advantage of numerous methods to get the desired display table for publication.

    There are a few table structuring options we can consider at this stage. We can choose to create
    a table stub containing row labels through the use of the `rowname_col=` argument. Further to
    this, row groups can be created with the `groupname_col=` argument. Both arguments take the name
    of a column in the input table data. Typically, the data in the `groupname_col=` column will
    consist of categorical text whereas the data in the `rowname_col=` column will often contain
    unique labels (perhaps being unique across the entire table or unique only within the different
    row groups).

    Parameters
    ----------
    data
        A DataFrame object.
    rowname_col
        The column name in the input `data=` table to use as row labels to be placed in the table
        stub.
    groupname_col
        The column name in the input `data=` table to use as group labels for generation of row
        groups.
    auto_align
        Optionally have column data be aligned depending on the content contained in each column of
        the input `data=`.
    id
        By default (with `None`) the table ID will be a random, ten-letter string as generated
        through internal use of the `random_id()` function. A custom table ID can be used here by
        providing a string.
    locale
        An optional locale identifier that can be set as the default locale for all functions that
        take a `locale` argument. Examples include `"en"` for English (United States) and `"fr"`
        for French (France).

    Returns
    -------
    GT
        A GT object is returned.

    Examples
    --------
    Let's use the `exibble` dataset for the next few examples, we'll learn how to make simple
    output tables with the `GT()` class. The most basic thing to do is to just use `GT()` with the
    dataset as the input.

    ```{python}
    from great_tables import GT, exibble

    GT(exibble)
    ```

    This dataset has the `row` and `group` columns. The former contains unique values that are ideal
    for labeling rows, and this often happens in what is called the 'stub' (a reserved area that
    serves to label rows). With the `GT()` class, we can immediately place the contents of the `row`
    column into the stub column. To do this, we use the `rowname_col=` argument with the appropriate
    column name.

    ```{python}
    from great_tables import GT, exibble

    GT(exibble, rowname_col="row")
    ```

    This sets up a table with a stub, the row labels are placed within the stub column, and a
    vertical dividing line has been placed on the right-hand side.

    The `group` column contains categorical values that are ideal for grouping rows. We can use the
    `groupname_col=` argument to place these values into row groups.

    ```{python}
    from great_tables import GT, exibble

    GT(exibble, rowname_col="row", groupname_col="group")
    ```

    By default, values in the body of a table (and their column labels) are automatically aligned.
    The alignment is governed by the types of values in a column. If you'd like to disable this form
    of auto-alignment, the `auto_align=False` option can be taken.

    ```{python}
    from great_tables import GT, exibble

    GT(exibble, rowname_col="row", auto_align=False)
    ```

    What you'll get from that is center-alignment of all table body values and all column labels.
    Note that row labels in the the stub are still left-aligned; and `auto_align=` has no effect on
    alignment within the table stub.

    However which way you generate the initial table object, you can modify it with a huge variety
    of methods to further customize the presentation. Formatting body cells is commonly done with
    the family of formatting methods (e.g., `fmt_number()`, `fmt_date()`, etc.). The package
    supports formatting with internationalization ('i18n' features) and so locale-aware methods
    all come with a `locale=` argument. To avoid having to use that argument repeatedly, the `GT()`
    class has its own `locale=` argument. Setting a locale in that will make it available globally.
    Here's an example of how that works in practice when setting `locale = "fr"` in `GT()` prior to
    using formatting methods:

    ```{python}
    from great_tables import GT, exibble

    (
        GT(exibble, rowname_col="row", locale="fr")
        .fmt_currency(columns="currency")
        .fmt_scientific(columns="num")
        .fmt_date(columns="date", date_style="day_month_year")
    )
    ```

    In this example, the `fmt_currency()`, `fmt_scientific()`, and `fmt_date()` methods understand
    that the locale for this table is `"fr"` (French), so the appropriate formatting for that locale
    is apparent in the `currency`, `num`, and `date` columns.
    """

    def __init__(
        self,
        data: Any,
        rowname_col: str | None = None,
        groupname_col: str | None = None,
        auto_align: bool = True,
        id: str | None = None,
        locale: str | None = None,
    ):
        gtdata = GTData.from_data(
            data,
            rowname_col=rowname_col,
            groupname_col=groupname_col,
            auto_align=auto_align,
            id=id,
            locale=locale,
        )
        super().__init__(**gtdata.__dict__)

    fmt = fmt
    fmt_number = fmt_number
    fmt_integer = fmt_integer
    fmt_percent = fmt_percent
    fmt_scientific = fmt_scientific
    fmt_currency = fmt_currency
    fmt_bytes = fmt_bytes
    fmt_roman = fmt_roman
    fmt_date = fmt_date
    fmt_time = fmt_time
    fmt_datetime = fmt_datetime
    fmt_markdown = fmt_markdown
    fmt_image = fmt_image
    fmt_units = fmt_units
    fmt_nanoplot = fmt_nanoplot
    data_color = data_color
    data_color_mpl = data_color_mpl

    sub_missing = sub_missing
    sub_zero = sub_zero

    opt_stylize = opt_stylize
    opt_align_table_header = opt_align_table_header
    opt_all_caps = opt_all_caps
    opt_footnote_marks = opt_footnote_marks
    opt_row_striping = opt_row_striping
    opt_vertical_padding = opt_vertical_padding
    opt_horizontal_padding = opt_horizontal_padding
    opt_table_outline = opt_table_outline

    cols_align = cols_align
    cols_width = cols_width
    cols_label = cols_label
    cols_move = cols_move
    cols_move_to_start = cols_move_to_start
    cols_move_to_end = cols_move_to_end
    cols_hide = cols_hide

    tab_header = tab_header
    tab_source_note = tab_source_note
    tab_spanner = tab_spanner
    tab_stubhead = tab_stubhead
    tab_style = tab_style
    tab_options = tab_options

    row_group_order = row_group_order
    tab_stub = tab_stub
    with_id = with_id
    with_locale = with_locale

    save = save
    as_raw_html = as_raw_html

    # -----

    def _repr_html_(self):
        # Some rendering environments expect that the HTML provided is a full page; however, quite
        # a few others accept a fragment of HTML. Within `as_raw_html()` can use the `make_page=`
        # argument to control this behavior. When `True` the table's HTML fragment (`<div><table>`)
        # is wrapped in a full page

        defaults = infer_render_env_defaults()
        make_page = defaults["make_page"]
        all_important = defaults["all_important"]

        rendered = self.as_raw_html(
            make_page=make_page,
            all_important=all_important,
        )

        return rendered

    def _render_formats(self, context: str) -> Self:
        new_body = self._body.copy()

        # TODO: this body method performs a mutation. Should we make a copy of body?
        new_body.render_formats(self._tbl_data, self._formats, context)
        new_body.render_formats(self._tbl_data, self._substitutions, context)
        return self._replace(_body=new_body)

    def _build_data(self, context: str) -> Self:
        # Build the body of the table by generating a dictionary
        # of lists with cells initially set to nan values
        built = self._render_formats(context)
        # built._body = _migrate_unformatted_to_output(body)

        # built._perform_col_merge()
        final_body = body_reassemble(built._body, built._stub, built._boxhead)

        # Reordering of the metadata elements of the table

        final_stub = reorder_stub_df(built._stub)
        # self = self.reorder_footnotes()
        # self = self.reorder_styles()

        # Transformations of individual cells at supported locations

        # self = self.perform_text_transforms()

        # ...

        return built._replace(_body=final_body, _stub=final_stub)

    def render(
        self,
        context: str,
    ) -> str:
        # Note ideally, this function will forward to things like .as_raw_html(), using a
        # context dataclass to set the options on those functions. E.g. a LatexContext
        # would have the options for a .as_latex() method, etc..
        html_table = self._build_data(context=context)._render_as_html()
        return html_table

    # =============================================================================
    # HTML Rendering
    # =============================================================================
    def _render_as_html(
        self,
        make_page: bool = False,
        all_important: bool = False,
    ) -> str:

        heading_component = create_heading_component_h(data=self)
        column_labels_component = create_columns_component_h(data=self)
        body_component = create_body_component_h(data=self)
        source_notes_component = create_source_notes_component_h(data=self)
        footnotes_component = create_footnotes_component_h(data=self)

        # Get attributes for the table
        table_defs = _get_table_defs(data=self)

        # Determine whether Quarto processing of the table is enabled
        quarto_disable_processing = str(self._options.quarto_disable_processing.value).lower()
        quarto_use_bootstrap = str(self._options.quarto_use_bootstrap.value).lower()

        # If table_defs["table_colgroups"] is None, then we set table_colgroups to an empty string;
        # if present, wrap the value with newlines
        if table_defs["table_colgroups"] is None:
            table_colgroups = ""
        else:
            table_colgroups = f"\n{table_defs['table_colgroups']}\n"

        if table_defs["table_style"] is None:
            table_tag_open = f'<table class="gt_table" data-quarto-disable-processing="{quarto_disable_processing}" data-quarto-bootstrap="{quarto_use_bootstrap}">'
        else:
            table_tag_open = f'<table style="{table_defs["table_style"]}" class="gt_table" data-quarto-disable-processing="{quarto_disable_processing}" data-quarto-bootstrap="{quarto_use_bootstrap}">'

        html_table = f"""{table_tag_open}{table_colgroups}
{heading_component.make_string()}
{column_labels_component}
{body_component}
{source_notes_component}
{footnotes_component}
</table>
"""

        # Obtain the `table_id` value from the Options (might be set, might be None)
        table_id = self._options.table_id.value

        if table_id is None:
            id = random_id()
        else:
            id = table_id

        # Compile the SCSS as CSS
        from ._scss import compile_scss

        css = compile_scss(data=self, id=id, all_important=all_important)

        # Obtain options set for overflow and container dimensions

        container_padding_x = self._options.container_padding_x.value
        container_padding_y = self._options.container_padding_y.value
        container_overflow_x = self._options.container_overflow_x.value
        container_overflow_y = self._options.container_overflow_y.value
        container_width = self._options.container_width.value
        container_height = self._options.container_height.value

        finalized_table = f"""<div id="{id}" style="padding-left:{container_padding_x};padding-right:{container_padding_x};padding-top:{container_padding_y};padding-bottom:{container_padding_y};overflow-x:{container_overflow_x};overflow-y:{container_overflow_y};width:{container_width};height:{container_height};">
<style>
{css}
</style>
{html_table}
</div>
        """

        if make_page:

            # Create an HTML page and place the table within it
            finalized_table = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
</head>
<body>
{finalized_table}
</body>
</html>
            """
        return finalized_table


# =============================================================================
# End of GT class
# =============================================================================


# =============================================================================
# Functions that operate on GT objects
# =============================================================================


def _get_column_labels(gt: GT, context: str) -> list[str]:
    gt_built = gt._build_data(context=context)
    column_labels = [x.column_label for x in gt_built._boxhead]
    return column_labels


def _get_column_of_values(gt: GT, column_name: str, context: str) -> list[str]:
    gt_built = gt._build_data(context=context)
    tbl_data = gt_built._body.body
    cell_values: list[str] = []

    for i in range(n_rows(tbl_data)):
        cell_content: Any = _get_cell(tbl_data, i, column_name)
        cell_str: str = str(cell_content)
        cell_values.append(cell_str)

    return cell_values
