from __future__ import annotations

from dataclasses import dataclass, fields, replace
from typing import TYPE_CHECKING, Any, Callable, Literal, Union

from typing_extensions import Self, TypeAlias

from ._helpers import GoogleFont, px
from ._tbl_data import PlExpr, TblData, _get_cell, eval_transform

if TYPE_CHECKING:
    from ._locations import Loc


# Cell Styles ==========================================================================
# TODO: stubbed out the styles in helpers.R as dataclasses while I was reading it,
# but have no worked on any runtime validation, etc..
ColumnExpr: TypeAlias = Union["FromColumn", PlExpr, "FromValues"]


@dataclass
class FromColumn:
    """Specify that a style value should be fetched from a column in the data.

    Examples
    --------

    ```{python}
    import pandas as pd
    from great_tables import GT, exibble, from_column, loc, style

    df = pd.DataFrame({"x": [1, 2], "color": ["red", "blue"]})

    (
        GT(df)
        .tab_style(
            style=style.text(color=from_column("color")),
            locations=loc.body(columns=["x"])
        )
    )
    ```

    If you are using polars, you can just pass polars expressions in directly:

    ```{python}
    import polars as pl
    from great_tables import GT, exibble, from_column, loc, style

    df_polars = pl.from_pandas(df)

    (
        GT(df_polars)
        .tab_style(
            style=style.text(color=pl.col("color")),
            locations=loc.body(columns=["x"])
        )
    )
    ```
    """

    column: str
    # TODO: na_value currently unused
    na_value: Any | None = None
    fn: Callable[[Any], Any] | None = None


@dataclass
class FromValues:
    values: list[Any]
    expr: PlExpr | None = None


# TODO: what goes into CellStyle?
@dataclass
class CellStyle:
    """A style specification."""

    def _to_html_style(self) -> str:
        raise NotImplementedError

    def _evaluate_expressions(self, data: TblData) -> Self:
        new_fields: dict[str, FromValues] = {}
        for field in fields(self):
            attr = getattr(self, field.name)
            if isinstance(attr, PlExpr) or callable(attr):
                col_res = eval_transform(data, attr)
                new_fields[field.name] = FromValues(expr=attr, values=col_res)

        if not new_fields:
            return self

        return replace(self, **new_fields)

    def _from_row(self, data: TblData, row: int) -> Self:
        """Return a new object with FromColumn replaced with values from row.

        Note that if no FromColumn fields are present, this returns the original object.
        """

        new_fields: dict[str, Any] = {}
        for field in fields(self):
            attr = getattr(self, field.name)
            if isinstance(attr, FromColumn):
                # TODO: could validate that the value fetched from data is allowed.
                # e.g. that color is a string, etc..
                val = _get_cell(data, row, attr.column)

                new_fields[field.name] = attr.fn(val) if attr.fn is not None else val
            elif isinstance(attr, FromValues):
                new_fields[field.name] = attr.values[row]

        if not new_fields:
            return self

        return replace(self, **new_fields)

    def _raise_if_requires_data(self, loc: Loc):
        for field in fields(self):
            attr = getattr(self, field.name)
            if isinstance(attr, FromColumn):
                raise TypeError(
                    f"Location type {type(loc)} cannot use FromColumn."
                    f"\n\nStyle type: {type(self)}"
                    f"\nField with FromColumn: {field.name}"
                )


@dataclass
class CellStyleCss(CellStyle):
    """A style specification for custom CSS rules.

    The `style.css()` class is to be used with the `tab_style()` method, which itself allows for
    the setting of custom styles to one or more cells. With `style.css()`, you can specify any CSS
    rule that you would like to apply to the targeted cells.

    Parameters
    ----------
    rule
        The CSS rule to apply to the targeted cells. This can be any valid CSS rule, such as
        `background-color: red;` or `font-size: 14px;`.

    Returns
    -------
    CellStyleCss
        A CellStyleCss object, which is used for a `styles` argument if specifying a custom CSS
        rule.

    Examples
    --------
    See [`GT.tab_style()`](`great_tables.GT.tab_style`).
    """

    rule: str

    def _to_html_style(self):
        return self.rule


@dataclass
class CellStyleText(CellStyle):
    """A style specification for cell text.

    The `style.text()` class is to be used with the `tab_style()` method, which itself allows for
    the setting of custom styles to one or more cells. With it, you can specify the color of the
    text, the font family, the font size, and the horizontal and vertical alignment of the text and
    more.

    Parameters
    ----------
    color
        The text color can be modified through the `color` argument.
    font
        The font or collection of fonts (subsequent font names are) used as fallbacks.
    size
        The size of the font. Can be provided as a number that is assumed to represent `px` values
        (or could be wrapped in the `px()` helper function). We can also use one of the following
        absolute size keywords: `"xx-small"`, `"x-small"`, `"small"`, `"medium"`, `"large"`,
        `"x-large"`, or `"xx-large"`.
    align
        The text in a cell can be horizontally aligned though one of the following options:
        `"center"`, `"left"`, `"right"`, or `"justify"`.
    v_align
        The vertical alignment of the text in the cell can be modified through the options
        `"middle"`, `"top"`, or `"bottom"`.
    style
        Can be one of either `"normal"`, `"italic"`, or `"oblique"`.
    weight
        The weight of the font can be modified thorough a text-based option such as `"normal"`,
        `"bold"`, `"lighter"`, `"bolder"`, or, a numeric value between `1` and `1000`, inclusive.
        Note that only variable fonts may support the numeric mapping of weight.
    stretch
        Allows for text to either be condensed or expanded. We can use one of the following
        text-based keywords to describe the degree of condensation/expansion: `"ultra-condensed"`,
        `"extra-condensed"`, `"condensed"`, `"semi-condensed"`, `"normal"`, `"semi-expanded"`,
        `"expanded"`, `"extra-expanded"`, or `"ultra-expanded"`. Alternatively, we can supply
        percentage values from `0%` to `200%`, inclusive. Negative percentage values are not
        allowed.
    decorate
        Allows for text decoration effect to be applied. Here, we can use `"overline"`,
        `"line-through"`, or `"underline"`.
    transform
        Allows for the transformation of text. Options are `"uppercase"`, `"lowercase"`, or
        `"capitalize"`.
    whitespace
        A white-space preservation option. By default, runs of white-space will be collapsed into
        single spaces but several options exist to govern how white-space is collapsed and how lines
        might wrap at soft-wrap opportunities. The options are `"normal"`, `"nowrap"`, `"pre"`,
        `"pre-wrap"`, `"pre-line"`, and `"break-spaces"`.

    Returns
    -------
    CellStyleText
        A CellStyleText object, which is used for a `styles` argument if specifying any cell text
        properties.

    Examples
    ------
    See [`GT.tab_style()`](`great_tables.GT.tab_style`).
    """

    color: str | ColumnExpr | None = None
    font: str | ColumnExpr | GoogleFont | None = None
    size: str | ColumnExpr | None = None
    align: Literal["center", "left", "right", "justify"] | ColumnExpr | None = None
    v_align: Literal["middle", "top", "bottom"] | ColumnExpr | None = None
    style: Literal["normal", "italic", "oblique"] | ColumnExpr | None = None
    weight: Literal["normal", "bold", "bolder", "lighter"] | ColumnExpr | None = None
    stretch: (
        Literal[
            "normal",
            "condensed",
            "ultra-condensed",
            "extra-condensed",
            "semi-condensed",
            "semi-expanded",
            "expanded",
            "extra-expanded",
            "ultra-expanded",
        ]
        | ColumnExpr
        | None
    ) = None
    decorate: (
        Literal["overline", "line-through", "underline", "underline overline"] | ColumnExpr | None
    ) = None
    transform: Literal["uppercase", "lowercase", "capitalize"] | ColumnExpr | None = None
    whitespace: (
        Literal["normal", "nowrap", "pre", "pre-wrap", "pre-line", "break-spaces"]
        | ColumnExpr
        | None
    ) = None

    def _to_html_style(self) -> str:
        rendered = ""

        if self.color:
            rendered += f"color: {self.color};"
        if self.font:
            font = self.font
            if isinstance(font, str) or isinstance(font, FromColumn):
                # Case where `font=` is a string or a FromColumn expression
                font_name = font
            elif isinstance(font, GoogleFont):
                # Case where `font=` is a GoogleFont
                font_name = font.get_font_name()
            else:
                # Case where font is of an invalid type
                raise ValueError(f"Invalid font type '{type(font)}' provided.")
            rendered += f"font-family: {font_name};"
        if self.size:
            rendered += f"font-size: {self.size};"
        if self.align:
            rendered += f"text-align: {self.align};"
        if self.v_align:
            rendered += f"vertical-align: {self.v_align};"
        if self.style:
            rendered += f"font-style: {self.style};"
        if self.weight:
            rendered += f"font-weight: {self.weight};"
        if self.stretch:
            rendered += f"font-stretch: {self.stretch};"
        if self.decorate:
            rendered += f"text-decoration: {self.decorate};"
        if self.transform:
            rendered += f"text-transform: {self.transform};"
        if self.whitespace:
            rendered += f"white-space: {self.whitespace};"

        return rendered


@dataclass
class CellStyleFill(CellStyle):
    """A style specification for the background fill of targeted cells.

    The `style.fill()` class is to be used with the `tab_style()` method, which itself allows for
    the setting of custom styles to one or more cells. Specifically, the call to `style.fill()`
    should be bound to the `styles` argument of `tab_style()`.

    Parameters
    ----------
    color
        The color to use for the cell background fill. This can be any valid CSS color value, such
        as a hex code, a named color, or an RGB value.

    Returns
    -------
    CellStyleFill
        A CellStyleFill object, which is used for a `styles` argument if specifying a cell fill
        value.

    Examples
    ------
    See [`GT.tab_style()`](`great_tables.GT.tab_style`).
    """

    color: str | ColumnExpr
    # alpha: float | None = None

    def _to_html_style(self) -> str:
        return f"background-color: {self.color};"


@dataclass
class CellStyleBorders(CellStyle):
    """A style specification for cell borders.

    The `styles.borders()` class is to be used with the `tab_style()` method, which itself allows
    for the setting of custom styles to one or more cells. The `sides` argument is where we define
    which borders should be modified (e.g., `"left"`, `"right"`, etc.). With that selection, the
    `color`, `style`, and `weight` of the selected borders can then be modified.

    Parameters
    ----------
    sides
        The border sides to be modified. Options include `"left"`, `"right"`, `"top"`, and
        `"bottom"`. For all borders surrounding the selected cells, we can use the `"all"` option.
    color
        The border `color` can be defined with any valid CSS color value, such as a hex code, a
        named color, or an RGB value. The default `color` value is `"#000000"` (black).
    style
        The border `style` can be one of either `"solid"` (the default), `"dashed"`, `"dotted"`,
        `"hidden"`, or `"double"`.
    weight
        The default value for `weight` is `"1px"` and higher values will become more visually
        prominent.

    Returns
    -------
    CellStyleBorders
        A CellStyleBorders object, which is used for a `styles` argument if specifying cell borders.

    Examples
    ------
    See [`GT.tab_style()`](`great_tables.GT.tab_style`).
    """

    sides: (
        Literal["all", "top", "bottom", "left", "right"]
        | list[Literal["all", "top", "bottom", "left", "right"]]
    ) = "all"
    color: str | ColumnExpr = "#000000"
    style: str | ColumnExpr = "solid"
    weight: str | ColumnExpr = "1px"

    def _to_html_style(self) -> str:
        # If sides is an empty list, return an empty string
        if isinstance(self.sides, list) and not self.sides:
            return ""

        # If self.sides is a string, convert to a list
        if isinstance(self.sides, str):
            self.sides = [self.sides]

        # If 'all' is provided then call the function recursively with all sides
        if "all" in self.sides:
            return CellStyleBorders(
                sides=["top", "bottom", "left", "right"],
                color=self.color,
                style=self.style,
                weight=self.weight,
            )._to_html_style()

        weight = self.weight
        if isinstance(weight, int):
            weight = px(weight)

        color = self.color
        style = self.style

        border_css_list: list[str] = []
        for side in self.sides:
            if side not in ["top", "bottom", "left", "right"]:
                raise ValueError(f"Invalid side '{side}' provided.")
            border_css_list.append(f"border-{side}: {weight} {style} {color};")

        border_css = "".join(border_css_list)
        return border_css
