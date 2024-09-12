from __future__ import annotations

from dataclasses import dataclass, fields, replace
from typing import TYPE_CHECKING, ClassVar, cast

from great_tables import _utils
from great_tables._helpers import FontStackName


if TYPE_CHECKING:
    from ._types import GTSelf


def tab_options(
    self: GTSelf,
    container_width: str | None = None,
    container_height: str | None = None,
    container_overflow_x: str | None = None,
    container_overflow_y: str | None = None,
    table_width: str | None = None,
    table_layout: str | None = None,
    # table_align: str | None = None,
    table_margin_left: str | None = None,
    table_margin_right: str | None = None,
    table_background_color: str | None = None,
    # table_additional_css: str | None = None,
    table_font_names: str | list[str] | None = None,
    table_font_size: str | None = None,
    table_font_weight: str | int | float | None = None,
    table_font_style: str | None = None,
    table_font_color: str | None = None,
    table_font_color_light: str | None = None,
    table_border_top_style: str | None = None,
    table_border_top_width: str | None = None,
    table_border_top_color: str | None = None,
    table_border_bottom_style: str | None = None,
    table_border_bottom_width: str | None = None,
    table_border_bottom_color: str | None = None,
    table_border_left_style: str | None = None,
    table_border_left_width: str | None = None,
    table_border_left_color: str | None = None,
    table_border_right_style: str | None = None,
    table_border_right_width: str | None = None,
    table_border_right_color: str | None = None,
    heading_background_color: str | None = None,
    heading_align: str | None = None,
    heading_title_font_size: str | None = None,
    heading_title_font_weight: str | int | float | None = None,
    heading_subtitle_font_size: str | None = None,
    heading_subtitle_font_weight: str | int | float | None = None,
    heading_padding: str | None = None,
    heading_padding_horizontal: str | None = None,
    heading_border_bottom_style: str | None = None,
    heading_border_bottom_width: str | None = None,
    heading_border_bottom_color: str | None = None,
    heading_border_lr_style: str | None = None,
    heading_border_lr_width: str | None = None,
    heading_border_lr_color: str | None = None,
    column_labels_background_color: str | None = None,
    column_labels_font_size: str | None = None,
    column_labels_font_weight: str | int | float | None = None,
    column_labels_text_transform: str | None = None,
    column_labels_padding: str | None = None,
    column_labels_padding_horizontal: str | None = None,
    column_labels_vlines_style: str | None = None,
    column_labels_vlines_width: str | None = None,
    column_labels_vlines_color: str | None = None,
    column_labels_border_top_style: str | None = None,
    column_labels_border_top_width: str | None = None,
    column_labels_border_top_color: str | None = None,
    column_labels_border_bottom_style: str | None = None,
    column_labels_border_bottom_width: str | None = None,
    column_labels_border_bottom_color: str | None = None,
    column_labels_border_lr_style: str | None = None,
    column_labels_border_lr_width: str | None = None,
    column_labels_border_lr_color: str | None = None,
    column_labels_hidden: bool | None = None,
    row_group_background_color: str | None = None,
    row_group_font_size: str | None = None,
    row_group_font_weight: str | int | float | None = None,
    row_group_text_transform: str | None = None,
    row_group_padding: str | None = None,
    row_group_padding_horizontal: str | None = None,
    row_group_border_top_style: str | None = None,
    row_group_border_top_width: str | None = None,
    row_group_border_top_color: str | None = None,
    row_group_border_bottom_style: str | None = None,
    row_group_border_bottom_width: str | None = None,
    row_group_border_bottom_color: str | None = None,
    row_group_border_left_style: str | None = None,
    row_group_border_left_width: str | None = None,
    row_group_border_left_color: str | None = None,
    row_group_border_right_style: str | None = None,
    row_group_border_right_width: str | None = None,
    row_group_border_right_color: str | None = None,
    # row_group_default_label: str | None = None,
    row_group_as_column: bool | None = None,
    table_body_hlines_style: str | None = None,
    table_body_hlines_width: str | None = None,
    table_body_hlines_color: str | None = None,
    table_body_vlines_style: str | None = None,
    table_body_vlines_width: str | None = None,
    table_body_vlines_color: str | None = None,
    table_body_border_top_style: str | None = None,
    table_body_border_top_width: str | None = None,
    table_body_border_top_color: str | None = None,
    table_body_border_bottom_style: str | None = None,
    table_body_border_bottom_width: str | None = None,
    table_body_border_bottom_color: str | None = None,
    stub_background_color: str | None = None,
    stub_font_size: str | None = None,
    stub_font_weight: str | int | float | None = None,
    stub_text_transform: str | None = None,
    stub_border_style: str | None = None,
    stub_border_width: str | None = None,
    stub_border_color: str | None = None,
    stub_row_group_font_size: str | None = None,
    stub_row_group_font_weight: str | int | float | None = None,
    stub_row_group_text_transform: str | None = None,
    stub_row_group_border_style: str | None = None,
    stub_row_group_border_width: str | None = None,
    stub_row_group_border_color: str | None = None,
    data_row_padding: str | None = None,
    data_row_padding_horizontal: str | None = None,
    # summary_row_background_color: str | None = None,
    # summary_row_text_transform: str | None = None,
    # summary_row_padding: str | None = None,
    # summary_row_padding_horizontal: str | None = None,
    # summary_row_border_style: str | None = None,
    # summary_row_border_width: str | None = None,
    # summary_row_border_color: str | None = None,
    # grand_summary_row_background_color: str | None = None,
    # grand_summary_row_text_transform: str | None = None,
    # grand_summary_row_padding: str | None = None,
    # grand_summary_row_padding_horizontal: str | None = None,
    # grand_summary_row_border_style: str | None = None,
    # grand_summary_row_border_width: str | None = None,
    # grand_summary_row_border_color: str | None = None,
    # footnotes_background_color: str | None = None,
    # footnotes_font_size: str | None = None,
    # footnotes_padding: str | None = None,
    # footnotes_padding_horizontal: str | None = None,
    # footnotes_border_bottom_style: str | None = None,
    # footnotes_border_bottom_width: str | None = None,
    # footnotes_border_bottom_color: str | None = None,
    # footnotes_border_lr_style: str | None = None,
    # footnotes_border_lr_width: str | None = None,
    # footnotes_border_lr_color: str | None = None,
    # footnotes_marks: str | list[str] | None = None,
    # footnotes_multiline: bool | None = None,
    # footnotes_sep: str | None = None,
    source_notes_background_color: str | None = None,
    source_notes_font_size: str | None = None,
    source_notes_padding: str | None = None,
    source_notes_padding_horizontal: str | None = None,
    source_notes_border_bottom_style: str | None = None,
    source_notes_border_bottom_width: str | None = None,
    source_notes_border_bottom_color: str | None = None,
    source_notes_border_lr_style: str | None = None,
    source_notes_border_lr_width: str | None = None,
    source_notes_border_lr_color: str | None = None,
    source_notes_multiline: bool | None = None,
    source_notes_sep: str | None = None,
    # row_striping_background_color: str | None = None,
    # row_striping_include_stub: bool | None = None,
    # row_striping_include_table_body: bool | None = None,
) -> GTSelf:
    """
    Modify the table output options.

    Modify the options available in a table. These options are named by the components, the
    subcomponents, and the element that can adjusted.

    Parameters
    ----------
    container_width
        The width of the table's container. Can be specified as a single-length
        character with units of pixels or as a percentage. If provided as a scalar numeric
        value, it is assumed that the value is given in units of pixels.
    container_height
        The height of the table's container.
    container_overflow_x
        An option to enable scrolling in the horizontal direction when the table content overflows
        the container dimensions. Using `True` (the default) means that horizontal scrolling is
        enabled to view the entire table in those directions. With `False`, the table may be clipped
        if the table width or height exceeds the `container_width`.
    container_overflow_y
        An option to enable scrolling in the vertical direction when the table content overflows.
        Same rules apply as for `container_overflow_x`; the dependency here is that of the table
        height (`container_height`).
    table_width
        The width of the table. Can be specified as a string with units of pixels or as a
        percentage. If provided as a numeric value, it is assumed that the value is given in
        units of pixels.
    table_layout
        The value for the `table-layout` CSS style in the HTML output context. By default, this
        is `"fixed"` but another valid option is `"auto"`.
    table_margin_left
        The size of the margins on the left of the table within the container. Can be
        specified as a single-length value with units of pixels or as a percentage. If
        provided as a numeric value, it is assumed that the value is given in units of pixels.
        Using `table_margin_left` will overwrite any values set by `table_align`.
    table_margin_right
        The size of the margins on the right of the table within the container. Same rules apply
        as for `table_margin_left`. Using `table_margin_right` will overwrite any values set by
        `table_align`.
    table_background_color
        The background color for the table. A color name or a hexadecimal color code should be
        provided.
    table_font_names
        The names of the fonts used for the table. This should be provided as a list of font
        names. If the first font isn't available, then the next font is tried (and so on).
    table_font_size
        The font size for the table. Can be specified as a string with units of pixels or as a
        percentage. If provided as a numeric value, it is assumed that the value is given in
        units of pixels.
    table_font_weight
        The font weight of the table. Can be a text-based keyword such as `"normal"`, `"bold"`,
        `"lighter"`, `"bolder"`, or, a numeric value between `1` and `1000`, inclusive. Note that
        only variable fonts may support the numeric mapping of weight.
    table_font_style
        The font style for the table. Can be one of either `"normal"`, `"italic"`, or `"oblique"`.
    table_font_color
        The text color used throughout the table. A color name or a hexadecimal color code should be
        provided.
    table_font_color_light
        The text color used throughout the table when the background color is dark. A color name or
        a hexadecimal color code should be provided.
    table_border_top_style
        The style of the table's absolute top border. Can be one of either `"solid"`, `"dotted"`,
        `"dashed"`, `"double"`, `"groove"`, `"ridge"`, `"inset"`, or `"outset"`.
    table_border_top_width
        The width of the table's absolute top border. Can be specified as a string with units of
        pixels or as a percentage. If provided as a numeric value, it is assumed that the value is
        given in units of pixels.
    table_border_top_color
        The color of the table's absolute top border. A color name or a hexadecimal color code
        should be provided.
    table_border_bottom_style
        The style of the table's absolute bottom border.
    table_border_bottom_width
        The width of the table's absolute bottom border.
    table_border_bottom_color
        The color of the table's absolute bottom border.
    table_border_left_style
        The style of the table's absolute left border.
    table_border_left_width
        The width of the table's absolute left border.
    table_border_left_color
        The color of the table's absolute left border.
    table_border_right_style
        The style of the table's absolute right border.
    table_border_right_width
        The width of the table's absolute right border.
    table_border_right_color
        The color of the table's absolute right border.
    heading_background_color
        The background color for the heading. A color name or a hexadecimal color code should be
        provided.
    heading_align
        Controls the horizontal alignment of the heading title and subtitle. We can either use
        `"center"`, `"left"`, or `"right"`.
    heading_title_font_size
        The font size for the heading title element.
    heading_title_font_weight
        The font weight of the heading title.
    heading_subtitle_font_size
        The font size for the heading subtitle element.
    heading_subtitle_font_weight
        The font weight of the heading subtitle.
    heading_padding
        The amount of vertical padding to incorporate in the `heading` (title and subtitle). Can be
        specified as a string with units of pixels or as a percentage. If provided as a numeric
        value, it is assumed that the value is given in units of pixels.
    heading_padding_horizontal
        The amount of horizontal padding to incorporate in the `heading` (title and subtitle). Can
        be specified as a string with units of pixels or as a percentage. If provided as a numeric
        value, it is assumed that the value is given in units of pixels.
    heading_border_bottom_style
        The style of the header's bottom border.
    heading_border_bottom_width
        The width of the header's bottom border. If the `width` of this border is larger, then it
        will be the visible border.
    heading_border_bottom_color
        The color of the header's bottom border.
    heading_border_lr_style
        The style of the left and right borders of the `heading` location.
    heading_border_lr_width
        The width of the left and right borders of the `heading` location. If the `width` of this
        border is larger, then it will be the visible border.
    heading_border_lr_color
        The color of the left and right borders of the `heading` location.
    column_labels_background_color
        The background color for the column labels. A color name or a hexadecimal color code should
        be provided.
    column_labels_font_size
        The font size to use for all column labels.
    column_labels_font_weight
        The font weight of the table's column labels.
    column_labels_text_transform
        The text transformation for the column labels. Either of the `"uppercase"`, `"lowercase"`,
        or `"capitalize"` keywords can be used.
    column_labels_padding
        The amount of vertical padding to incorporate in the `column_labels` (this includes the
        column spanners).
    column_labels_padding_horizontal
        The amount of horizontal padding to incorporate in the `column_labels` (this includes the
        column spanners).
    column_labels_vlines_style
        The style of all vertical lines ('vlines') of the `column_labels`.
    column_labels_vlines_width
        The width of all vertical lines ('vlines') of the `column_labels`.
    column_labels_vlines_color
        The color of all vertical lines ('vlines') of the `column_labels`.
    column_labels_border_top_style
        The style of the top border of the `column_labels` location.
    column_labels_border_top_width
        The width of the top border of the `column_labels` location. If the `width` of this border
        is larger, then it will be the visible border.
    column_labels_border_top_color
        The color of the top border of the `column_labels` location.
    column_labels_border_bottom_style
        The style of the bottom border of the `column_labels` location.
    column_labels_border_bottom_width
        The width of the bottom border of the `column_labels` location. If the `width` of this
        border is larger, then it will be the visible border.
    column_labels_border_bottom_color
        The color of the bottom border of the `column_labels` location.
    column_labels_border_lr_style
        The style of the left and right borders of the `column_labels` location.
    column_labels_border_lr_width
        The width of the left and right borders of the `column_labels` location. If the `width` of
        this border is larger, then it will be the visible border.
    column_labels_border_lr_color
        The color of the left and right borders of the `column_labels` location.
    column_labels_hidden
        An option to hide the column labels. If providing `True` then the entire `column_labels`
        location won't be seen and the table header (if present) will collapse downward.
    row_group_background_color
        The background color for the row group labels. A color name or a hexadecimal color code
        should be provided.
    row_group_font_weight
        The font weight for all row group labels present in the table.
    row_group_font_size
        The font size to use for all row group labels.
    row_group_padding
        The amount of vertical padding to incorporate in the row group labels.
    row_group_border_top_style
        The style of the top border of the `row_group` location.
    row_group_border_top_width
        The width of the top border of the `row_group` location. If the `width` of this border is
        larger, then it will be the visible border.
    row_group_border_top_color
        The color of the top border of the `row_group` location.
    row_group_border_bottom_style
        The style of the bottom border of the `row_group` location.
    row_group_border_bottom_width
        The width of the bottom border of the `row_group` location. If the `width` of this border
        is larger, then it will be the visible border.
    row_group_border_bottom_color
        The color of the bottom border of the `row_group` location.
    row_group_border_left_style
        The style of the left border of the `row_group` location.
    row_group_border_left_width
        The width of the left border of the `row_group` location. If the `width` of this border is
        larger, then it will be the visible border.
    row_group_border_left_color
        The color of the left border of the `row_group` location.
    row_group_border_right_style
        The style of the right border of the `row_group` location.
    row_group_border_right_width
        The width of the right border of the `row_group` location. If the `width` of this border is
    row_group_border_right_color
        The color of the right border of the `row_group` location.
    row_group_as_column
        An option to render the row group labels as a column. If `True`, then the row group labels
        will be rendered as a column to the left of the table body. If `False`, then the row group
        labels will be rendered as a separate row above the grouping of rows.
    table_body_hlines_style
        The style of all horizontal lines ('hlines') in the `table_body`.
    table_body_hlines_width
        The width of all horizontal lines ('hlines') in the `table_body`.
    table_body_hlines_color
        The color of all horizontal lines ('hlines') in the `table_body`.
    table_body_vlines_style
        The style of all vertical lines ('vlines') in the `table_body`.
    table_body_vlines_width
        The width of all vertical lines ('vlines') in the `table_body`.
    table_body_vlines_color
        The color of all vertical lines ('vlines') in the `table_body`.
    table_body_border_top_style
        The style of the top border of the `table_body` location.
    table_body_border_top_width
        The width of the top border of the `table_body` location. If the `width` of this border is
        larger, then it will be the visible border.
    table_body_border_top_color
        The color of the top border of the `table_body` location.
    table_body_border_bottom_style
        The style of the bottom border of the `table_body` location.
    table_body_border_bottom_width
        The width of the bottom border of the `table_body` location. If the `width` of this border
    table_body_border_bottom_color
        The color of the bottom border of the `table_body` location.
    stub_background_color
        The background color for the stub. A color name or a hexadecimal color code should be
        provided.
    stub_font_size
        The font size to use for all row labels present in the table stub.
    stub_font_weight
        The font weight for all row labels present in the table stub.
    stub_text_transform
        The text transformation for the row labels present in the table stub.
    stub_border_style
        The style of the vertical border of the table stub.
    stub_border_width
        The width of the vertical border of the table stub.
    stub_border_color
        The color of the vertical border of the table stub.
    stub_row_group_font_size
        The font size for the row group column in the stub.
    stub_row_group_font_weight
        The font weight for the row group column in the stub.
    stub_row_group_text_transform
        The text transformation for the row group column in the stub.
    stub_row_group_border_style
        The style of the vertical border of the row group column in the stub.
    stub_row_group_border_width
        The width of the vertical border of the row group column in the stub.
    stub_row_group_border_color
        The color of the vertical border of the row group column in the stub.
    data_row_padding
        The amount of vertical padding to incorporate in the body/stub rows.
    data_row_padding_horizontal
        The amount of horizontal padding to incorporate in the body/stub rows.
    source_notes_background_color
        The background color for the source notes. A color name or a hexadecimal color code should
        be provided.
    source_notes_font_size
        The font size to use for all source note text.
    source_notes_padding
        The amount of vertical padding to incorporate in the source notes.
    source_notes_padding_horizontal
        The amount of horizontal padding to incorporate in the source notes.
    source_notes_multiline
        An option to either put source notes in separate lines (the default, or `True`) or render
        them as a continuous line of text with `source_notes_sep` providing the separator (by
        default `" "`) between notes.
    source_notes_sep
        The separating characters between adjacent source notes when rendered as a continuous line
        of text (when `source_notes_multiline` is `False`). The default value is a single space
        character (`" "`).
    source_notes_border_bottom_style
        The style of the bottom border of the `source_notes` location.
    source_notes_border_bottom_width
        The width of the bottom border of the `source_notes` location. If the `width` of this border
        is larger, then it will be the visible border.
    source_notes_border_bottom_color
        The color of the bottom border of the `source_notes` location.
    source_notes_border_lr_style
        The style of the left and right borders of the `source_notes` location.
    source_notes_border_lr_width
        The width of the left and right borders of the `source_notes` location. If the `width` of
        this border is larger, then it will be the visible border.
    source_notes_border_lr_color
        The color of the left and right borders of the `source_notes` location.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    Using select columns from the `exibble` dataset, let's create a new table with a number of table
    components added. We can use this object going forward to demonstrate some of the features
    available in the `tab_options()` method.

    ```{python}
    from great_tables import GT, exibble, md

    gt_tbl = (
      GT(
        exibble[["num", "char", "currency", "row", "group"]],
        rowname_col="row",
        groupname_col="group"
      )
      .tab_header(
        title=md("Data listing from **exibble**"),
        subtitle=md("`exibble` is a **Great Tables** dataset.")
      )
      .fmt_number(columns="num")
      .fmt_currency(columns="currency")
      .tab_source_note(source_note="This is only a subset of the dataset.")
    )

    gt_tbl
    ```

    We can modify the table width to be set as `"100%`". In effect, this spans the table to entirely
    fill the content width area. This is done with the `table_width` option.

    ```{python}
    gt_tbl.tab_options(table_width="100%")
    ```

    With the `table_background_color` option, we can modify the table's background color. Here, we
    want that to be `"lightcyan"`.

    ```{python}
    gt_tbl.tab_options(table_background_color="lightcyan")
    ```

    The data rows of a table typically take up the most physical space but we have some control over
    the extent of that. With the `data_row_padding` option, it's possible to modify the top and
    bottom padding of data rows. We'll do just that in the following example, reducing the padding
    to a value of `"3px"`.

    ```{python}
    gt_tbl.tab_options(data_row_padding="3px")
    ```

    The size of the title and the subtitle text in the header of the table can be altered with the
    `heading_title_font_size` and `heading_subtitle_font_size` options. Here, we'll use the
    `"small"` and `"x-small"` keyword values.

    ```{python}
    gt_tbl.tab_options(heading_title_font_size="small", heading_subtitle_font_size="x-small")
    ```
    """
    saved_args = locals()

    del saved_args["self"]

    modified_args = {k: v for k, v in saved_args.items() if v is not None}

    # Intercept modified args and modify before replacing options:
    # - `table_font_names` should be a list but if given as a string, ensure it is list
    if "table_font_names" in modified_args:
        if isinstance(modified_args["table_font_names"], str):
            modified_args["table_font_names"] = [modified_args["table_font_names"]]

    new_options_info = {
        k: replace(getattr(self._options, k), value=v) for k, v in modified_args.items()
    }
    new_options = replace(self._options, **new_options_info)

    return self._replace(_options=new_options)


def opt_footnote_marks(self: GTSelf, marks: str | list[str] = "numbers") -> GTSelf:
    """
    Option to modify the set of footnote marks
    Alter the footnote marks for any footnotes that may be present in the table. Either a list
    of marks can be provided (including Unicode characters), or, a specific keyword could be
    used to signify a preset sequence. This method serves as a shortcut for using
    `tab_options(footnotes_marks=<marks>)`

    We can supply a list of strings will represent the series of marks. The series of footnote
    marks is recycled when its usage goes beyond the length of the set. At each cycle, the marks
    are simply doubled, tripled, and so on (e.g., `*` -> `**` -> `***`). The option exists for
    providing keywords for certain types of footnote marks. The keywords are

    - `"numbers"`: numeric marks, they begin from 1 and these marks are not subject to recycling
    behavior
    - `"letters"`: lowercase alphabetic marks. Same as using the `gt.letters()` function which
    produces a list of 26 lowercase letters from the Roman alphabet
    - `"LETTERS"`: uppercase alphabetic marks. Same as using the `gt.LETTERS()` function which
    produces a list of 26 uppercase letters from the Roman alphabet
    - `"standard"`: symbolic marks, four symbols in total
    - `"extended"`: symbolic marks, extends the standard set by adding two more symbols, making
    six

    Parameters
    ----------
    marks
        Either a list of strings that will represent the series of marks or a keyword string
        that represents a preset sequence of marks. The valid keywords are: `"numbers"` (for
        numeric marks), `"letters"` and `"LETTERS"` (for lowercase and uppercase alphabetic
        marks), `"standard"` (for a traditional set of four symbol marks), and `"extended"`
        (which adds two more symbols to the standard set).

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.
    """
    # Validate the marks keyword passed in as a string
    if marks is str:
        marks = _utils._match_arg(
            x=cast(str, marks),
            lst=["numbers", "letters", "LETTERS", "standard", "extended"],
        )

    return tab_options(self, footnotes_marks=marks)


def opt_row_striping(self: GTSelf, row_striping: bool = True) -> GTSelf:
    """
    Option to add or remove row striping.

    By default, a gt*table does not have row striping enabled. However, this method allows us to
    easily enable or disable striped rows in the table body. It's a convenient shortcut for
    `gt.tab_options(row_striping_include_table_body=<True|False>)`.

    Parameters
    ----------
    row_striping
        A boolean that indicates whether row striping should be added or removed. Defaults to
        `True`.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.
    """
    return tab_options(self, row_striping_include_table_body=row_striping)


def opt_align_table_header(self: GTSelf, align: str = "center") -> GTSelf:
    """
    Option to align the table header.

    By default, an added table header will have center alignment for both the title and the subtitle
    elements. This method allows us to easily set the horizontal alignment of the title and subtitle
    to the left, right, or center by using the `"align"` argument. This method serves as a
    convenient shortcut for `gt.tab_options(heading_align=<align>)`.

    Parameters
    ----------
    align
        The alignment of the title and subtitle elements in the table header. Options are `"center"`
        (the default), `"left"`, or `"right"`.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    Using select columns from the `exibble` dataset, let's create a table with a number of
    components added. Following that, we'll align the header contents (consisting of the title and
    the subtitle) to the left with the `opt_align_table_header()` method.

    ```{python}
    from great_tables import GT, exibble, md

    (
      GT(
        exibble[["num", "char", "currency", "row", "group"]],
        rowname_col="row",
        groupname_col="group"
      )
      .tab_header(
        title=md("Data listing from **exibble**"),
        subtitle=md("`exibble` is a **Great Tables** dataset.")
      )
      .fmt_number(columns="num")
      .fmt_currency(columns="currency")
      .tab_source_note(source_note="This is only a subset of the dataset.")
      .opt_align_table_header(align="left")
    )
    ```
    """

    align = _utils._match_arg(x=align, lst=["left", "center", "right"])

    return tab_options(self, heading_align=align)


def opt_vertical_padding(self: GTSelf, scale: float = 1.0) -> GTSelf:
    """
    Option to scale the vertical padding of the table.

    This method allows us to scale the vertical padding of the table by a factor of `scale`. The
    default value is `1.0` and this method serves as a convenient shortcut for
    `gt.tab_options(heading_padding=<new_val>, column_labels_padding=<new_val>,
    data_row_padding=<new_val>, row_group_padding=<new_val>, source_notes_padding=<new_val>)`.

    Parameters
    ----------
    scale
        The factor by which to scale the vertical padding. The default value is `1.0`. A value
        less than `1.0` will reduce the padding, and a value greater than `1.0` will increase the
        padding. The value must be between `0` and `3`.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    Using select columns from the `exibble` dataset, let's create a table with a number of
    components added. Following that, we'll scale the vertical padding of the table by a factor of
    `3` using the `opt_vertical_padding()` method.

    ```{python}
    from great_tables import GT, exibble, md

    gt_tbl = (
        GT(
            exibble[["num", "char", "currency", "row", "group"]],
            rowname_col="row",
            groupname_col="group"
        )
        .tab_header(
            title=md("Data listing from **exibble**"),
            subtitle=md("`exibble` is a **Great Tables** dataset.")
        )
        .fmt_number(columns="num")
        .fmt_currency(columns="currency")
        .tab_source_note(source_note="This is only a subset of the dataset.")
    )

    gt_tbl.opt_vertical_padding(scale=3)
    ```

    Now that's a tall table! The overall effect of scaling the vertical padding is that the table
    will appear taller and there will be more buffer space between the table elements. A value of
    `3` is pretty extreme and is likely to be too much in most cases, so, feel free to experiment
    with different values when looking to increase the vertical padding.

    Let's go the other way (using a value less than `1`) and try to condense the content vertically
    with a `scale` factor of `0.5`. This will reduce the top and bottom padding globally and make
    the table appear more compact.

    ```{python}
    gt_tbl.opt_vertical_padding(scale=0.5)
    ```

    A value of `0.5` provides a reasonable amount of vertical padding and the table will appear more
    compact. This is useful when space is limited and, in such a situation, this is a practical
    solution to that problem.
    """

    # Stop if `scale` is beyond an acceptable range
    if scale < 0 or scale > 3:
        raise ValueError("`scale` must be a value between `0` and `3`.")

    # Get the parameters from the options that relate to vertical padding
    vertical_padding_params = [
        "heading_padding",
        "column_labels_padding",
        "data_row_padding",
        "row_group_padding",
        "source_notes_padding",
    ]

    # Get the current values for the vertical padding parameters
    vertical_padding_vals = [
        self._options.heading_padding.value,
        self._options.column_labels_padding.value,
        self._options.data_row_padding.value,
        self._options.row_group_padding.value,
        self._options.source_notes_padding.value,
    ]

    # Multiply each of the padding values by the `scale` factor but strip off the units first
    # then reattach the units after the multiplication
    # TODO: a current limitation is that the padding values must be in pixels and not percentages
    # TODO: another limitation is that the returned values must be in integer pixel values
    new_vertical_padding_vals = [
        str(int(float(v.split("px")[0]) * scale)) + "px" for v in vertical_padding_vals
    ]

    return tab_options(self, **dict(zip(vertical_padding_params, new_vertical_padding_vals)))


def opt_horizontal_padding(self: GTSelf, scale: float = 1.0) -> GTSelf:
    """
    Option to scale the horizontal padding of the table.

    This method allows us to scale the horizontal padding of the table by a factor of `scale`. The
    default value is `1.0` and this method serves as a convenient shortcut for `gt.tab_options(
    heading_padding_horizontal=<new_val>, column_labels_padding_horizontal=<new_val>,
    data_row_padding_horizontal=<new_val>, row_group_padding_horizontal=<new_val>,
    source_notes_padding_horizontal=<new_val>)`.

    Parameters
    ----------
    scale
        The factor by which to scale the horizontal padding. The default value is `1.0`. A value
        less than `1.0` will reduce the padding, and a value greater than `1.0` will increase the
        padding. The value must be between `0` and `3`.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    Using select columns from the `exibble` dataset, let's create a table with a number of
    components added. Following that, we'll scale the horizontal padding of the table by a factor of
    `3` using the `opt_horizontal_padding()` method.

    ```{python}
    from great_tables import GT, exibble, md

    gt_tbl = (
        GT(
            exibble[["num", "char", "currency", "row", "group"]],
            rowname_col="row",
            groupname_col="group"
        )
        .tab_header(
            title=md("Data listing from **exibble**"),
            subtitle=md("`exibble` is a **Great Tables** dataset.")
        )
        .fmt_number(columns="num")
        .fmt_currency(columns="currency")
        .tab_source_note(source_note="This is only a subset of the dataset.")
    )

    gt_tbl.opt_horizontal_padding(scale=3)
    ```

    The overall effect of scaling the horizontal padding is that the table will appear wider or
    and there will added buffer space between the table elements. The overall look of the table will
    be more spacious and neigboring pieces of text will be less cramped.

    Let's go the other way and scale the horizontal padding of the table by a factor of `0.5` using
    the `opt_horizontal_padding()` method.

    ```{python}
    gt_tbl.opt_horizontal_padding(scale=0.5)
    ```

    What you get in this case is more condensed text across the horizontal axis. This may not always
    be desired when cells consist mainly of text, but it could be useful when the table is more
    visual and the cells are filled with graphics or other non-textual elements.
    """

    # Stop if `scale` is beyond an acceptable range
    if scale < 0 or scale > 3:
        raise ValueError("`scale` must be a value between `0` and `3`.")

    # Get the parameters from the options that relate to horizontal padding
    horizontal_padding_params = [
        "heading_padding_horizontal",
        "column_labels_padding_horizontal",
        "data_row_padding_horizontal",
        "row_group_padding_horizontal",
        "source_notes_padding_horizontal",
    ]

    # Get the current values for the horizontal padding parameters
    horizontal_padding_vals = [
        self._options.heading_padding_horizontal.value,
        self._options.column_labels_padding_horizontal.value,
        self._options.data_row_padding_horizontal.value,
        self._options.row_group_padding_horizontal.value,
        self._options.source_notes_padding_horizontal.value,
    ]

    # Multiply each of the padding values by the `scale` factor but strip off the units first
    # then reattach the units after the multiplication
    # TODO: a current limitation is that the padding values must be in pixels and not percentages
    # TODO: another limitation is that the returned values must be in integer pixel values
    new_horizontal_padding_vals = [
        str(int(float(v.split("px")[0]) * scale)) + "px" for v in horizontal_padding_vals
    ]

    return tab_options(self, **dict(zip(horizontal_padding_params, new_horizontal_padding_vals)))


def opt_all_caps(
    self: GTSelf,
    all_caps: bool = True,
    locations: str | list[str] = ["column_labels", "stub", "row_group"],
) -> GTSelf:
    """
    Option to use all caps in select table locations.

    Sometimes an all-capitalized look is suitable for a table. By using `opt_all_caps()`, we can
    transform characters in the column labels, the stub, and in all row groups in this way (and
    there's control over which of these locations are transformed). This method serves as a
    convenient shortcut for `tab_options(<location>_text_transform="uppercase",
    <location>_font_size="80%", <location>_font_weight="bolder")` (for all `locations` selected).

    Parameters
    ----------
    all_caps
        Indicates whether the text transformation to all caps should be performed (`True`, the
        default) or reset to default values (`False`) for the `locations` targeted.

    locations
        Which locations should undergo this text transformation? By default it includes all of
        the `loc.column_labels`, the `loc.stub"`, and the `loc.row_group` locations. However, we
        could just choose one or two of those.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    Using select columns from the `exibble` dataset, let's create a table with a number of
    components added. Following that, we'll ensure that all text in the column labels, the stub, and
    in all row groups is transformed to all caps using the `opt_all_caps()` method.

    ```{python}
    from great_tables import GT, exibble, loc, md

    (
      GT(
        exibble[["num", "char", "currency", "row", "group"]],
        rowname_col="row",
        groupname_col="group"
      )
      .tab_header(
        title=md("Data listing from **exibble**"),
        subtitle=md("`exibble` is a **Great Tables** dataset.")
      )
      .fmt_number(columns="num")
      .fmt_currency(columns="currency")
      .tab_source_note(source_note="This is only a subset of the dataset.")
      .opt_all_caps()
    )
    ```
    `opt_all_caps()` accepts a `locations` parameter that allows us to specify which components
    should be transformed. For example, if we only want to ensure that all text in the stub and all
    row groups is converted to all caps:
    ```{python}
    (
      GT(
        exibble[["num", "char", "currency", "row", "group"]],
        rowname_col="row",
        groupname_col="group"
      )
      .tab_header(
        title=md("Data listing from **exibble**"),
        subtitle=md("`exibble` is a **Great Tables** dataset.")
      )
      .fmt_number(columns="num")
      .fmt_currency(columns="currency")
      .tab_source_note(source_note="This is only a subset of the dataset.")
      .opt_all_caps(locations=[loc.stub, loc.row_group])
    )
    ```
    """
    # Importing `great_tables._locations` at the top will cause a circular import error.
    # The type annotation for `locations` should be:
    # `Loc | list[Loc] = [LocColumnLabels, LocStub, LocRowGroups]`
    from great_tables._locations import Loc, LocColumnLabels, LocStub, LocRowGroups

    if not locations:
        locations = [LocColumnLabels, LocStub, LocRowGroups]

    # If providing a Loc object, normalize it to be in a list
    if not isinstance(locations, list):
        locations = [locations]

    # Ensure that all values within `locations` are valid
    # A `try-except` block is needed here because the first argument of `issubclass()` must be a
    # class.
    for location in locations:
        try:
            issubclass(location, Loc)
        except TypeError as exc:
            raise AssertionError(
                "Only `loc.column_labels`, `loc.stub` and `loc.row_group` are allowed in the locations."
            ) from exc

    # if `all_caps` is False, reset options to default, or, set new options
    # for `locations` selected
    if not all_caps:
        return tab_options(
            self,
            column_labels_font_size="100%",
            column_labels_font_weight="normal",
            column_labels_text_transform="inherit",
            stub_font_size="100%",
            stub_font_weight="initial",
            stub_text_transform="inherit",
            row_group_font_size="100%",
            row_group_font_weight="initial",
            row_group_text_transform="inherit",
        )

    info = [
        (
            LocColumnLabels,
            {
                "column_labels_font_size": "80%",
                "column_labels_font_weight": "bolder",
                "column_labels_text_transform": "uppercase",
            },
        ),
        (
            LocStub,
            {
                "stub_font_size": "80%",
                "stub_font_weight": "bolder",
                "stub_text_transform": "uppercase",
            },
        ),
        (
            LocRowGroups,
            {
                "row_group_font_size": "80%",
                "row_group_font_weight": "bolder",
                "row_group_text_transform": "uppercase",
            },
        ),
    ]
    d = {}
    for location, params in info:
        if location in locations:
            d |= params

    return tab_options(self, **d)


def opt_table_outline(
    self: GTSelf, style: str = "solid", width: str = "3px", color: str = "#D3D3D3"
) -> GTSelf:
    """
    Option to wrap an outline around the entire table.

    The `opt_table_outline()` method puts an outline of consistent `style=`, `width=`, and `color=`
    around the entire table. It'll write over any existing outside lines so long as the `width=`
    value is larger that of the existing lines. The default value of `style=` (`"solid"`) will draw
    a solid outline, whereas using `"none"` will remove any present outline.

    Parameters
    ----------
    style
        The style of the table outline. The default value is `"solid"`. The valid values are
        `"solid"`, `"dashed"`, `"dotted"`, and `"none"`.
    width
        The width of the table outline. The default value is `"3px"`. The value must be in pixels
        and it must be an integer value.
    color
        The color of the table outline, where the default is `"#D3D3D3"`. The value must either a
        hexadecimal color code or a color name.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    Using select columns from the `exibble` dataset, let's create a table with a number of
    components added. Following that, we'll put an outline around the entire table using the
    `opt_table_outline()` method.

    ```{python}
    from great_tables import GT, exibble, md

    (
      GT(
        exibble[["num", "char", "currency", "row", "group"]],
        rowname_col="row",
        groupname_col="group"
      )
      .tab_header(
        title=md("Data listing from **exibble**"),
        subtitle=md("`exibble` is a **Great Tables** dataset.")
      )
      .fmt_number(columns="num")
      .fmt_currency(columns="currency")
      .tab_source_note(source_note="This is only a subset of the dataset.")
      .opt_table_outline()
    )
    ```
    """

    # Validate the `style` argument
    style = _utils._match_arg(x=style, lst=["solid", "dashed", "dotted", "none"])

    # Create a dictionary of parameters to pass to the `tab_options()` method
    params = {
        "table_border_top_style": style,
        "table_border_bottom_style": style,
        "table_border_left_style": style,
        "table_border_right_style": style,
        "table_border_top_width": width,
        "table_border_bottom_width": width,
        "table_border_left_width": width,
        "table_border_right_width": width,
        "table_border_top_color": color,
        "table_border_bottom_color": color,
        "table_border_left_color": color,
        "table_border_right_color": color,
    }

    # Set the table outline options
    res = tab_options(self=self, **params)

    return res


def opt_table_font(
    self: GTSelf,
    font: str | list[str] | None = None,
    stack: FontStackName | None = None,
    weight: str | int | float | None = None,
    style: str | None = None,
    add: bool = True,
) -> GTSelf:
    """Options to define font choices for the entire table.

    The `opt_table_font()` method makes it possible to define fonts used for an entire table. Any
    font names supplied in `font=` will (by default, with `add=True`) be placed before the names
    present in the existing font stack (i.e., they will take precedence). You can choose to base the
    font stack on those provided by the [`system_fonts()`](`system_fonts.md`) helper function by
    providing a valid keyword for a themed set of fonts. Take note that you could still have
    entirely different fonts in specific locations of the table. To make that possible you would
    need to use [`tab_style()`](`great_tables.GT.tab_style`) in conjunction with
    [`style.text()`](`great_tables.style.text`).

    Parameters
    ----------
    font
        One or more font names available on the user system. This can be a string or a list of
        strings. The default value is `None` since you could instead opt to use `stack` to define
        a list of fonts.
    stack
        A name that is representative of a font stack (obtained via internally via the
        `system_fonts()` helper function. If provided, this new stack will replace any defined fonts
        and any `font=` values will be prepended.
    style
        An option to modify the text style. Can be one of either `"normal"`, `"italic"`, or
        `"oblique"`.
    weight
        Option to set the weight of the font. Can be a text-based keyword such as `"normal"`,
        `"bold"`, `"lighter"`, `"bolder"`, or, a numeric value between `1` and `1000`. Please note
        that typefaces have varying support for the numeric mapping of weight.
    add
        Should fonts be added to the beginning of any already-defined fonts for the table? By
        default, this is `True` and is recommended since those fonts already present can serve as
        fallbacks when everything specified in `font` is not available. If a `stack=` value is
        provided, then `add` will automatically set to `False`.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Possibilities for the `stack` argument
    --------------------------------------

    There are several themed font stacks available via the [`system_fonts()`](`system_fonts.md`)
    helper function. That function can be used to generate all or a segment of a list supplied to
    the `font=` argument. However, using the `stack=` argument with one of the 15 keywords for the
    font stacks available in [`system_fonts()`](`system_fonts.md`), we could be sure that the
    typeface class will work across multiple computer systems. Any of the following keywords can be
    used with `stack=`:

    - `"system-ui"`
    - `"transitional"`
    - `"old-style"`
    - `"humanist"`
    - `"geometric-humanist"`
    - `"classical-humanist"`
    - `"neo-grotesque"`
    - `"monospace-slab-serif"`
    - `"monospace-code"`
    - `"industrial"`
    - `"rounded-sans"`
    - `"slab-serif"`
    - `"antique"`
    - `"didone"`
    - `"handwritten"`

    Examples
    --------
    Let's use a subset of the `sp500` dataset to create a small table. With `opt_table_font()` we
    can add some preferred font choices for modifying the text of the entire table. Here we'll use
    the `"Superclarendon"` and `"Georgia"` fonts (the second font serves as a fallback).

    ```{python}
    import polars as pl
    from great_tables import GT
    from great_tables.data import sp500

    sp500_mini = pl.from_pandas(sp500).slice(0, 10).drop(["volume", "adj_close"])

    (
        GT(sp500_mini, rowname_col="date")
        .fmt_currency(use_seps=False)
        .opt_table_font(font=["Superclarendon", "Georgia"])
    )
    ```

    In practice, both of these fonts are not likely to be available on all systems. The
    `opt_table_font()` method safeguards against this by prepending the fonts in the `font=` list to
    the existing font stack. This way, if both fonts are not available, the table will fall back to
    using the list of default table fonts. This behavior is controlled by the `add=` argument, which
    is `True` by default.

    With the `sza` dataset we'll create a two-column, eleven-row table. Within `opt_table_font()`,
    the `stack=` argument will be supplied with the "rounded-sans" font stack. This sets up a family
    of fonts with rounded, curved letterforms that should be locally available in different
    computing environments.

    ```{python}
    from great_tables.data import sza

    sza_mini = (
        pl.from_pandas(sza)
        .filter((pl.col("latitude") == "20") & (pl.col("month") == "jan"))
        .drop_nulls()
        .drop(["latitude", "month"])
    )

    (
        GT(sza_mini)
        .opt_table_font(stack="rounded-sans")
        .opt_all_caps()
    )
    ```
    """

    if font is None and stack is None:
        raise ValueError("Either `font=` or `stack=` must be provided.")

    # Get the existing fonts for the table from the options; we may either prepend to this
    # list or replace it entirely
    existing_fonts = self._options.table_font_names.value

    # If `existing_fonts` is not a list, throw an error
    if not isinstance(existing_fonts, list):
        raise ValueError("The value from `_options.table_font_names` must be a list.")

    res = self

    if font is not None:

        # If `font` is a string, convert it to a list
        if isinstance(font, str):
            font = [font]

    else:
        font = []

    if stack is not None:

        # Case where value is given to `stack=` and this is a keyword that returns a
        # list of fonts (i.e., the font stack); in this case we combine with `font=` values
        # (if provided) and we *always* replace the existing fonts (`add=` is ignored)
        from great_tables._helpers import system_fonts

        font_stack = system_fonts(name=stack)
        combined_fonts = font + font_stack
    elif add:
        # Case where `font=` is prepended to existing fonts
        combined_fonts = font + existing_fonts
    else:
        # Case where  `font=` replacing existing fonts
        combined_fonts = font

    res = tab_options(res, table_font_names=combined_fonts)

    if weight is not None:

        if isinstance(weight, int) or isinstance(weight, float):

            weight = str(round(weight))

        elif not isinstance(weight, str):
            raise TypeError(
                "`weight=` must be a numeric value between 1 and 1000 or a text-based keyword."
            )

        res = tab_options(res, table_font_weight=weight)
        res = tab_options(res, column_labels_font_weight=weight)

    if style is not None:

        res = tab_options(res, table_font_style=style)

    return res


def opt_stylize(self: GTSelf, style: int = 1, color: str = "blue") -> GTSelf:
    """
    Stylize your table with a colorful look.

    With the `opt_stylize()` method you can quickly style your table with a carefully curated set of
    background colors, line colors, and line styles. There are six styles to choose from and they
    largely vary in the extent of coloring applied to different table locations. Some have table
    borders applied, some apply darker colors to the table stub and summary sections, and, some even
    have vertical lines. In addition to choosing a `style` preset, there are six `color` variations
    that each use a range of five color tints. Each of the color tints have been fine-tuned to
    maximize the contrast between text and its background. There are 36 combinations of `style` and
    `color` to choose from.

    Parameters
    ----------
    style
        Six numbered styles are available. Simply provide a number from `1` (the default) to `6` to
        choose a distinct look.
    color
        The color scheme of the table. The default value is `"blue"`. The valid values are `"blue"`,
        `"cyan"`, `"pink"`, `"green"`, `"red"`, and `"gray"`.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Examples
    --------
    Using select columns from the `exibble` dataset, let's create a table with a number of
    components added. Following that, we'll apply a predefined style to the table using the
    `opt_stylize()` method.

    ```{python}
    from great_tables import GT, exibble, md

    gt_tbl = (
          GT(
            exibble[["num", "char", "currency", "row", "group"]],
            rowname_col="row",
            groupname_col="group"
          )
          .tab_header(
            title=md("Data listing from **exibble**"),
            subtitle=md("`exibble` is a **Great Tables** dataset.")
          )
          .fmt_number(columns="num")
          .fmt_currency(columns="currency")
          .tab_source_note(source_note="This is only a subset of the dataset.")
          .opt_stylize()
        )

    gt_tbl
    ```

    The table has been stylized with the default style and color. The default style is `1` and the
    default color is `"blue"`. The resulting table style is a combination of color and border
    settings that are applied to the table.

    We can modify the overall style and choose a different color theme by providing different values
    to the `style=` and `color=` arguments.

    ```{python}
    gt_tbl.opt_stylize(style=2, color="green")
    ```
    """

    # Validate the `style` and `color` arguments
    if style not in [1, 2, 3, 4, 5, 6]:
        raise ValueError("`style` must be an integer value from `1` to `6`.")
    color = _utils._match_arg(x=color, lst=["gray", "blue", "cyan", "pink", "green", "red"])

    # Get the style parameters based on the `style` and `color` arguments
    params = _dict_styles_colors_params[f"{color}-{style}"]

    # Omit keys that are not needed for the `tab_options()` method
    # TODO: the omitted keys are for future use when:
    #  (1) row striping is implemented
    #  (2) summary rows are implemented
    #  (3) grand summary rows are implemented
    omit_keys = {
        "summary_row_background_color",
        "grand_summary_row_background_color",
        "row_striping_background_color",
        "table_outline_color",
    }

    def dict_omit_keys(dict: dict[str, str], omit_keys: set[str]) -> dict[str, str]:
        return {x: v for x, v in dict.items() if x not in omit_keys}

    params = dict_omit_keys(dict=params, omit_keys=omit_keys)

    mapped_params = StyleMapper(**params).map_all()

    # Apply the style parameters to the table using the `tab_options()` method
    res = tab_options(self=self, **mapped_params)

    return res


@dataclass
class StyleMapper:
    table_hlines_color: str
    location_hlines_color: str
    column_labels_background_color: str
    stub_background_color: str
    stub_border_style: str
    stub_border_color: str
    data_hlines_style: str
    data_hlines_color: str
    data_vlines_style: str
    data_vlines_color: str

    mappings: ClassVar[dict[str, list[str]]] = {
        "table_hlines_color": ["table_border_top_color", "table_border_bottom_color"],
        "location_hlines_color": [
            "heading_border_bottom_color",
            "column_labels_border_top_color",
            "column_labels_border_bottom_color",
            "row_group_border_top_color",
            "row_group_border_bottom_color",
            "table_body_border_top_color",
            "table_body_border_bottom_color",
        ],
        "column_labels_background_color": ["column_labels_background_color"],
        "stub_background_color": ["stub_background_color"],
        "stub_border_style": ["stub_border_style"],
        "stub_border_color": ["stub_border_color"],
        "data_hlines_style": ["table_body_hlines_style"],
        "data_hlines_color": ["table_body_hlines_color"],
        "data_vlines_style": ["table_body_vlines_style"],
        "data_vlines_color": ["table_body_vlines_color"],
    }

    def map_entry(self, name: str) -> dict[str, list[str]]:
        return {k: getattr(self, name) for k in self.mappings[name]}

    def map_all(self) -> dict[str, list[str]]:
        items: dict[str, list[str]] = {}
        for field in fields(self):
            items.update(self.map_entry(field.name))
        return items


_dict_styles_colors_params = {
    "gray-1": {
        "table_hlines_color": "#000000",
        "location_hlines_color": "#5F5F5F",
        "column_labels_background_color": "#FFFFFF",
        "stub_background_color": "#5F5F5F",
        "stub_border_style": "solid",
        "stub_border_color": "#5F5F5F",
        "data_hlines_style": "none",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "none",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#F4F4F4",
    },
    "blue-1": {
        "table_hlines_color": "#004D80",
        "location_hlines_color": "#0076BA",
        "column_labels_background_color": "#FFFFFF",
        "stub_background_color": "#0076BA",
        "stub_border_style": "solid",
        "stub_border_color": "#0076BA",
        "data_hlines_style": "none",
        "data_hlines_color": "#89D3FE",
        "data_vlines_style": "none",
        "data_vlines_color": "#89D3FE",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#89D3FE",
        "row_striping_background_color": "#F4F4F4",
    },
    "cyan-1": {
        "table_hlines_color": "#016763",
        "location_hlines_color": "#01837B",
        "column_labels_background_color": "#FFFFFF",
        "stub_background_color": "#01837B",
        "stub_border_style": "solid",
        "stub_border_color": "#01837B",
        "data_hlines_style": "none",
        "data_hlines_color": "#A5FEF2",
        "data_vlines_style": "none",
        "data_vlines_color": "#A5FEF2",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#A5FEF2",
        "row_striping_background_color": "#F4F4F4",
    },
    "pink-1": {
        "table_hlines_color": "#99195F",
        "location_hlines_color": "#CB2A7B",
        "column_labels_background_color": "#FFFFFF",
        "stub_background_color": "#CB2A7B",
        "stub_border_style": "solid",
        "stub_border_color": "#CB2A7B",
        "data_hlines_style": "none",
        "data_hlines_color": "#FFC6E3",
        "data_vlines_style": "none",
        "data_vlines_color": "#FFC6E3",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#FFC6E3",
        "row_striping_background_color": "#F4F4F4",
    },
    "green-1": {
        "table_hlines_color": "#027101",
        "location_hlines_color": "#038901",
        "column_labels_background_color": "#FFFFFF",
        "stub_background_color": "#038901",
        "stub_border_style": "solid",
        "stub_border_color": "#038901",
        "data_hlines_style": "none",
        "data_hlines_color": "#CAFFAF",
        "data_vlines_style": "none",
        "data_vlines_color": "#CAFFAF",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#CAFFAF",
        "row_striping_background_color": "#F4F4F4",
    },
    "red-1": {
        "table_hlines_color": "#A81600",
        "location_hlines_color": "#E4220C",
        "column_labels_background_color": "#FFFFFF",
        "stub_background_color": "#E4220C",
        "stub_border_style": "solid",
        "stub_border_color": "#E4220C",
        "data_hlines_style": "none",
        "data_hlines_color": "#FFCCC7",
        "data_vlines_style": "none",
        "data_vlines_color": "#FFCCC7",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#FFCCC7",
        "row_striping_background_color": "#F4F4F4",
    },
    "gray-2": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#000000",
        "stub_background_color": "#FFFFFF",
        "stub_border_style": "solid",
        "stub_border_color": "#5F5F5F",
        "data_hlines_style": "solid",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "solid",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#D5D5D5",
        "grand_summary_row_background_color": "#929292",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "blue-2": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#004D80",
        "stub_background_color": "#FFFFFF",
        "stub_border_style": "solid",
        "stub_border_color": "#5F5F5F",
        "data_hlines_style": "solid",
        "data_hlines_color": "#89D3FE",
        "data_vlines_style": "solid",
        "data_vlines_color": "#89D3FE",
        "summary_row_background_color": "#89D3FE",
        "grand_summary_row_background_color": "#00A1FF",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "cyan-2": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#016763",
        "stub_background_color": "#FFFFFF",
        "stub_border_style": "solid",
        "stub_border_color": "#5F5F5F",
        "data_hlines_style": "solid",
        "data_hlines_color": "#A5FEF2",
        "data_vlines_style": "solid",
        "data_vlines_color": "#A5FEF2",
        "summary_row_background_color": "#A5FEF2",
        "grand_summary_row_background_color": "#7FE9DB",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "pink-2": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#99195F",
        "stub_background_color": "#FFFFFF",
        "stub_border_style": "solid",
        "stub_border_color": "#5F5F5F",
        "data_hlines_style": "solid",
        "data_hlines_color": "#FFC6E3",
        "data_vlines_style": "solid",
        "data_vlines_color": "#FFC6E3",
        "summary_row_background_color": "#FFC6E3",
        "grand_summary_row_background_color": "#EF5FA7",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "green-2": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#027101",
        "stub_background_color": "#FFFFFF",
        "stub_border_style": "solid",
        "stub_border_color": "#5F5F5F",
        "data_hlines_style": "solid",
        "data_hlines_color": "#CAFFAF",
        "data_vlines_style": "solid",
        "data_vlines_color": "#CAFFAF",
        "summary_row_background_color": "#CAFFAF",
        "grand_summary_row_background_color": "#89FD61",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "red-2": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#A81600",
        "stub_background_color": "#FFFFFF",
        "stub_border_style": "solid",
        "stub_border_color": "#5F5F5F",
        "data_hlines_style": "solid",
        "data_hlines_color": "#FFCCC7",
        "data_vlines_style": "solid",
        "data_vlines_color": "#FFCCC7",
        "summary_row_background_color": "#FFCCC7",
        "grand_summary_row_background_color": "#FF644E",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "gray-3": {
        "table_hlines_color": "#929292",
        "location_hlines_color": "#929292",
        "column_labels_background_color": "#000000",
        "stub_background_color": "#D5D5D5",
        "stub_border_style": "none",
        "stub_border_color": "#FFFFFF",
        "data_hlines_style": "dashed",
        "data_hlines_color": "#929292",
        "data_vlines_style": "none",
        "data_vlines_color": "#929292",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#F4F4F4",
    },
    "blue-3": {
        "table_hlines_color": "#929292",
        "location_hlines_color": "#929292",
        "column_labels_background_color": "#004D80",
        "stub_background_color": "#D5D5D5",
        "stub_border_style": "none",
        "stub_border_color": "#FFFFFF",
        "data_hlines_style": "dashed",
        "data_hlines_color": "#929292",
        "data_vlines_style": "none",
        "data_vlines_color": "#929292",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#F4F4F4",
    },
    "cyan-3": {
        "table_hlines_color": "#929292",
        "location_hlines_color": "#929292",
        "column_labels_background_color": "#016763",
        "stub_background_color": "#D5D5D5",
        "stub_border_style": "none",
        "stub_border_color": "#FFFFFF",
        "data_hlines_style": "dashed",
        "data_hlines_color": "#929292",
        "data_vlines_style": "none",
        "data_vlines_color": "#929292",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#F4F4F4",
    },
    "pink-3": {
        "table_hlines_color": "#929292",
        "location_hlines_color": "#929292",
        "column_labels_background_color": "#99195F",
        "stub_background_color": "#D5D5D5",
        "stub_border_style": "none",
        "stub_border_color": "#FFFFFF",
        "data_hlines_style": "dashed",
        "data_hlines_color": "#929292",
        "data_vlines_style": "none",
        "data_vlines_color": "#929292",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#F4F4F4",
    },
    "green-3": {
        "table_hlines_color": "#929292",
        "location_hlines_color": "#929292",
        "column_labels_background_color": "#027101",
        "stub_background_color": "#D5D5D5",
        "stub_border_style": "none",
        "stub_border_color": "#FFFFFF",
        "data_hlines_style": "dashed",
        "data_hlines_color": "#929292",
        "data_vlines_style": "none",
        "data_vlines_color": "#929292",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#F4F4F4",
    },
    "red-3": {
        "table_hlines_color": "#929292",
        "location_hlines_color": "#929292",
        "column_labels_background_color": "#A81600",
        "stub_background_color": "#D5D5D5",
        "stub_border_style": "none",
        "stub_border_color": "#FFFFFF",
        "data_hlines_style": "dashed",
        "data_hlines_color": "#929292",
        "data_vlines_style": "none",
        "data_vlines_color": "#929292",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#F4F4F4",
    },
    "gray-4": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#5F5F5F",
        "stub_background_color": "#929292",
        "stub_border_style": "dashed",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "dashed",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "dashed",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#5F5F5F",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "blue-4": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#0076BA",
        "stub_background_color": "#929292",
        "stub_border_style": "dashed",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "dashed",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "dashed",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#0076BA",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "cyan-4": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#01837B",
        "stub_background_color": "#929292",
        "stub_border_style": "dashed",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "dashed",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "dashed",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#01837B",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "pink-4": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#CB2A7B",
        "stub_background_color": "#929292",
        "stub_border_style": "dashed",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "dashed",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "dashed",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#CB2A7B",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "green-4": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#038901",
        "stub_background_color": "#929292",
        "stub_border_style": "dashed",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "dashed",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "dashed",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#038901",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "red-4": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#E4220C",
        "stub_background_color": "#929292",
        "stub_border_style": "dashed",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "dashed",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "dashed",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#E4220C",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "gray-5": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#000000",
        "stub_background_color": "#929292",
        "stub_border_style": "solid",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "solid",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "solid",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#5F5F5F",
        "grand_summary_row_background_color": "#929292",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "blue-5": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#004D80",
        "stub_background_color": "#929292",
        "stub_border_style": "solid",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "solid",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "solid",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#5F5F5F",
        "grand_summary_row_background_color": "#929292",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "cyan-5": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#016763",
        "stub_background_color": "#929292",
        "stub_border_style": "solid",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "solid",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "solid",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#5F5F5F",
        "grand_summary_row_background_color": "#929292",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "pink-5": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#99195F",
        "stub_background_color": "#929292",
        "stub_border_style": "solid",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "solid",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "solid",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#5F5F5F",
        "grand_summary_row_background_color": "#929292",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "green-5": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#027101",
        "stub_background_color": "#929292",
        "stub_border_style": "solid",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "solid",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "solid",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#5F5F5F",
        "grand_summary_row_background_color": "#929292",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "red-5": {
        "table_hlines_color": "#D5D5D5",
        "location_hlines_color": "#D5D5D5",
        "column_labels_background_color": "#A81600",
        "stub_background_color": "#929292",
        "stub_border_style": "solid",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "solid",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "solid",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#5F5F5F",
        "grand_summary_row_background_color": "#929292",
        "row_striping_background_color": "#F4F4F4",
        "table_outline_color": "#D5D5D5",
    },
    "gray-6": {
        "table_hlines_color": "#5F5F5F",
        "location_hlines_color": "#5F5F5F",
        "column_labels_background_color": "#5F5F5F",
        "stub_background_color": "#D5D5D5",
        "stub_border_style": "solid",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "none",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "none",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#F4F4F4",
    },
    "blue-6": {
        "table_hlines_color": "#5F5F5F",
        "location_hlines_color": "#5F5F5F",
        "column_labels_background_color": "#0076BA",
        "stub_background_color": "#89D3FE",
        "stub_border_style": "solid",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "none",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "none",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#EDF7FC",
    },
    "cyan-6": {
        "table_hlines_color": "#5F5F5F",
        "location_hlines_color": "#5F5F5F",
        "column_labels_background_color": "#01837B",
        "stub_background_color": "#A5FEF2",
        "stub_border_style": "solid",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "none",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "none",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#EBFBF9",
    },
    "pink-6": {
        "table_hlines_color": "#5F5F5F",
        "location_hlines_color": "#5F5F5F",
        "column_labels_background_color": "#CB2A7B",
        "stub_background_color": "#FFC6E3",
        "stub_border_style": "solid",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "none",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "none",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#FCF2F7",
    },
    "green-6": {
        "table_hlines_color": "#5F5F5F",
        "location_hlines_color": "#5F5F5F",
        "column_labels_background_color": "#038901",
        "stub_background_color": "#CAFFAF",
        "stub_border_style": "solid",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "none",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "none",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#EDF6E8",
    },
    "red-6": {
        "table_hlines_color": "#5F5F5F",
        "location_hlines_color": "#5F5F5F",
        "column_labels_background_color": "#E4220C",
        "stub_background_color": "#FFCCC7",
        "stub_border_style": "solid",
        "stub_border_color": "#D5D5D5",
        "data_hlines_style": "none",
        "data_hlines_color": "#D5D5D5",
        "data_vlines_style": "none",
        "data_vlines_color": "#D5D5D5",
        "summary_row_background_color": "#FFFFFF",
        "grand_summary_row_background_color": "#D5D5D5",
        "row_striping_background_color": "#FEEDEC",
    },
}
