from __future__ import annotations

import random
import re
import string
from dataclasses import dataclass
from typing import Any, Callable, Literal

from typing_extensions import Self, TypeAlias

from ._text import BaseText, Html, Md, _md_html

FontStackName: TypeAlias = Literal[
    "system-ui",
    "transitional",
    "old-style",
    "humanist",
    "geometric-humanist",
    "classical-humanist",
    "neo-grotesque",
    "monospace-slab-serif",
    "monospace-code",
    "industrial",
    "rounded-sans",
    "slab-serif",
    "antique",
    "didone",
    "handwritten",
]


FONT_STACKS = {
    "system-ui": [
        "system-ui",
        "sans-serif",
    ],
    "transitional": [
        "Charter",
        "Bitstream Charter",
        "Sitka Text",
        "Cambria",
        "serif",
    ],
    "old-style": [
        "Iowan Old Style",
        "Palatino Linotype",
        "URW Palladio L",
        "P052",
        "serif",
    ],
    "humanist": [
        "Seravek",
        "Gill Sans Nova",
        "Ubuntu",
        "Calibri",
        "DejaVu Sans",
        "source-sans-pro",
        "sans-serif",
    ],
    "geometric-humanist": [
        "Avenir",
        "Montserrat",
        "Corbel",
        "URW Gothic",
        "source-sans-pro",
        "sans-serif",
    ],
    "classical-humanist": [
        "Optima",
        "Candara",
        "Noto Sans",
        "source-sans-pro",
        "sans-serif",
    ],
    "neo-grotesque": [
        "Inter",
        "Roboto",
        "Helvetica Neue",
        "Arial Nova",
        "Nimbus Sans",
        "Arial",
        "sans-serif",
    ],
    "monospace-slab-serif": [
        "Nimbus Mono PS",
        "Courier New",
        "monospace",
    ],
    "monospace-code": [
        "ui-monospace",
        "Cascadia Code",
        "Source Code Pro",
        "Menlo",
        "Consolas",
        "DejaVu Sans Mono",
        "monospace",
    ],
    "industrial": [
        "Bahnschrift",
        "DIN Alternate",
        "Franklin Gothic Medium",
        "Nimbus Sans Narrow",
        "sans-serif-condensed",
        "sans-serif",
    ],
    "rounded-sans": [
        "ui-rounded",
        "Hiragino Maru Gothic ProN",
        "Quicksand",
        "Comfortaa",
        "Manjari",
        "Arial Rounded MT",
        "Arial Rounded MT Bold",
        "Calibri",
        "source-sans-pro",
        "sans-serif",
    ],
    "slab-serif": [
        "Rockwell",
        "Rockwell Nova",
        "Roboto Slab",
        "DejaVu Serif",
        "Sitka Small",
        "serif",
    ],
    "antique": [
        "Superclarendon",
        "Bookman Old Style",
        "URW Bookman",
        "URW Bookman L",
        "Georgia Pro",
        "Georgia",
        "serif",
    ],
    "didone": [
        "Didot",
        "Bodoni MT",
        "Noto Serif Display",
        "URW Palladio L",
        "P052",
        "Sylfaen",
        "serif",
    ],
    "handwritten": [
        "Segoe Print",
        "Bradley Hand",
        "Chilanka",
        "TSCu_Comic",
        "casual",
        "cursive",
    ],
}


def px(x: int | float) -> str:
    """
    Helper for providing a CSS length value in pixels.

    For certain parameters, a length value is required. Examples include the setting of font sizes
    (e.g., in `cell_text()`) and thicknesses of lines (e.g., in `cell_borders()`). Setting a length
    in pixels with `px()` allows for an absolute definition of size as opposed to the analogous
    helper function `pct()`.

    Parameters
    ----------
    x
        The integer or float value to format as a string (e.g., `"12px"`) for some arguments that
        can take values as units of pixels.

    Examples
    --------
        >>> from gt import *
        >>> x = gt.px(12)
        >>> x
        >>> print(x)
    """
    return f"{x}px"


def pct(x: int | float) -> str:
    """
    Helper for providing a CSS length value as a percentage.

    A percentage value acts as a length value that is relative to an initial state. For instance an
    80% value for something will size the target to 80% the size of its 'previous' value. This type
    of sizing is useful for sizing up or down a length value with an intuitive measure. This helper
    function can be used for the setting of font sizes (e.g., in `cell_text()`) and altering the
    thicknesses of lines (e.g., in `cell_borders()`. Should a more exact definition of size be
    required, the analogous helper function `pct()` will be more useful.

    Parameters
    ----------
    x
        The integer or float value to format as a string-based percentage value for some arguments
        that can take percentage values.

    Examples
    --------
        >>> from gt import *
        >>> x = gt.pct(80)
        >>> x
        >>> print(x)
    """
    return f"{x}%"


def md(text: str) -> Md:
    """Interpret input text as Markdown-formatted text.

    Markdown can be used in certain places (e.g., source notes, table title/subtitle, etc.) and we
    can expect it to render to HTML. There is also the [`html()`](`great_tables.html`) helper
    function that allows you to use raw HTML text.

    Parameters
    ----------
    text
        The text that is understood to contain Markdown formatting.

    Examples
    ------
    See [`GT.tab_header()`](`great_tables.GT.tab_header`).
    """
    return Md(text=text)


def html(text: str) -> Html:
    """Interpret input text as HTML-formatted text.

    For certain pieces of text (like in column labels or table headings) we may want to express them
    as raw HTML. In fact, with HTML, anything goes so it can be much more than just text. The
    `html()` function will guard the input HTML against escaping, so, your HTML tags will come
    through as HTML when rendered.

    Parameters
    ----------
    text
        The text that is understood to contain HTML formatting.

    Examples
    ------
    See [`GT.tab_header()`](`great_tables.GT.tab_header`).
    """
    return Html(text=text)


def random_id(n: int = 10) -> str:
    """Helper for creating a random `id` for an output table

    Parameters
    ----------
    n
        The number of lowercase letters to use in the random ID string. Defaults to 10.

    Returns
    -------
    str
        A string that constitutes a random ID value.
    """
    return "".join(random.choices(letters(), k=n))


def letters() -> list[str]:
    """Lowercase letters of the Roman alphabet

    Returns:
        list[str]: the 26 lowercase letters of the Roman alphabet
    """
    return list(string.ascii_lowercase)


def LETTERS() -> list[str]:
    """Uppercase letters of the Roman alphabet

    Returns:
        list[str]: the 26 uppercase letters of the Roman alphabet
    """
    return list(string.ascii_uppercase)


@dataclass
class GoogleFont:
    font: str

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.font})"

    def make_import_stmt(self) -> str:
        return f"@import url('https://fonts.googleapis.com/css2?family={self.font.replace(' ', '+')}&display=swap');"

    def get_font_name(self) -> str:
        return self.font


def google_font(name: str) -> GoogleFont:
    """Specify a font from the *Google Fonts* service.

    The `google_font()` helper function can be used wherever a font name might be specified. There
    are two instances where this helper can be used:

    1. `opt_table_font(font=...)` (for setting a table font)
    2. `style.text(font=...)` (itself used in [`tab_style()`](`great_tables.GT.tab_style`))

    Parameters
    ----------
    name
        The name of the Google Font to use.

    Returns
    -------
    GoogleFont
        A GoogleFont object, which contains the name of the font and methods for incorporating the
        font in HTML output tables.

    Examples
    --------
    Let's use the `exibble` dataset to create a table of two columns and eight rows. We'll replace
    missing values with em dashes using [`sub_missing()`](`great_tables.GT.sub_missing`). For text
    in the time column, we will use the font called `"IBM Plex Mono"` which is available from Google
    Fonts. This is defined inside the `google_font()` call, itself within the
    [`style.text()`](`great_tables.style.text`) method that's applied to the `style=` parameter of
    [`tab_style()`](`great_tables.GT.tab_style`).

    ```{python}
    from great_tables import GT, exibble, style, loc, google_font

    (
        GT(exibble[["char", "time"]])
        .sub_missing()
        .tab_style(
            style=style.text(font=google_font(name="IBM Plex Mono")),
            locations=loc.body(columns="time")
        )
    )
    ```

    We can use a subset of the `sp500` dataset to create a small table. With
    [`fmt_currency()`](`great_tables.GT.fmt_currency`), we can display values as monetary values.
    Then, we'll set a larger font size for the table and opt to use the `"Merriweather"` font by
    calling `google_font()` within [`opt_table_font()`](`great_tables.GT.opt_table_font`). In cases
    where that font may not materialize, we include two font fallbacks: `"Cochin"` and the catchall
    `"Serif"` group.

    ```{python}
    from great_tables import GT, google_font
    from great_tables.data import sp500

    (
        GT(sp500.drop(columns=["volume", "adj_close"]).head(10))
        .fmt_currency(columns=["open", "high", "low", "close"])
        .tab_options(table_font_size="20px")
        .opt_table_font(font=[google_font(name="Merriweather"), "Cochin", "Serif"])
    )
    ```
    """

    return GoogleFont(font=name)


def system_fonts(name: FontStackName = "system-ui") -> list[str]:
    """Get a themed font stack that works well across systems.

    A font stack can be obtained from `system_fonts()` using one of various keywords such as
    `"system-ui"`, `"old-style"`, and `"humanist"` (there are 15 in total) representing a themed set
    of fonts. These sets comprise a font family that has been tested to work across a wide range of
    computer systems.

    Parameters
    ----------
    name
        The name of a font stack. Must be drawn from the set of `"system-ui"` (the default),
        `"transitional"`, `"old-style"`, `"humanist"`, `"geometric-humanist"`,
        `"classical-humanist"`, `"neo-grotesque"`, `"monospace-slab-serif"`, `"monospace-code"`,
        `"industrial"`, `"rounded-sans"`, `"slab-serif"`, `"antique"`, `"didone"`, and
        `"handwritten"`.

    Returns
    -------
    list[str]
        A list of font names that make up the font stack.

    The font stacks and the individual fonts used by platform
    ---------------------------------------------------------
    ### System UI (`"system-ui"`)

    ```css
    font-family: system-ui, sans-serif;
    ```

    The operating system interface's default typefaces are known as system UI fonts. They contain a
    variety of font weights, are quite readable at small sizes, and are perfect for UI elements.
    These typefaces serve as a great starting point for text in data tables and so this font stack
    is the default for **Great Tables**.

    ### Transitional (`"transitional"`)

    ```css
    font-family: Charter, 'Bitstream Charter', 'Sitka Text', Cambria, serif;
    ```

    The Enlightenment saw the development of transitional typefaces, which combine Old Style and
    Modern typefaces. *Times New Roman*, a transitional typeface created for the Times of London
    newspaper, is among the most well-known instances of this style.

    ### Old Style (`"old-style"`)

    ```css
    font-family: 'Iowan Old Style', 'Palatino Linotype', 'URW Palladio L', P052, serif;
    ```

    Old style typefaces were created during the Renaissance and are distinguished by diagonal
    stress, a lack of contrast between thick and thin strokes, and rounded serifs. *Garamond* is
    among the most well-known instances of an antique typeface.

    ### Humanist (`"humanist"`)

    ```css
    font-family: Seravek, 'Gill Sans Nova', Ubuntu, Calibri, 'DejaVu Sans', source-sans-pro, sans-serif;
    ```

    Low contrast between thick and thin strokes and organic, calligraphic forms are traits of
    humanist typefaces. These typefaces, which draw their inspiration from Renaissance calligraphy,
    are frequently regarded as being more readable and easier to read than other sans serif
    typefaces.

    ### Geometric Humanist (`"geometric-humanist"`)

    ```css
    font-family: Avenir, Montserrat, Corbel, 'URW Gothic', source-sans-pro, sans-serif;
    ```

    Clean, geometric forms and consistent stroke widths are characteristics of geometric humanist
    typefaces. These typefaces, which are frequently used for headlines and other display purposes,
    are frequently thought to be contemporary and slick in appearance. A well-known example of this
    classification is *Futura*.

    ### Classical Humanist (`"classical-humanist"`)

    ```css
    font-family: Optima, Candara, 'Noto Sans', source-sans-pro, sans-serif;
    ```

    The way the strokes gradually widen as they approach the stroke terminals without ending in a
    serif is what distinguishes classical humanist typefaces. The stone carving on Renaissance-era
    tombstones and classical Roman capitals served as inspiration for these typefaces.

    ### Neo-Grotesque (`"neo-grotesque"`)

    ```css
    font-family: Inter, Roboto, 'Helvetica Neue', 'Arial Nova', 'Nimbus Sans', Arial, sans-serif;
    ```

    Neo-grotesque typefaces are a form of sans serif that originated in the late 19th and early 20th
    centuries. They are distinguished by their crisp, geometric shapes and regular stroke widths.
    *Helvetica* is among the most well-known examples of a Neo-grotesque typeface.

    ### Monospace Slab Serif (`"monospace-slab-serif"`)

    ```css
    font-family: 'Nimbus Mono PS', 'Courier New', monospace;
    ```

    Monospace slab serif typefaces are distinguished by their fixed-width letters, which are the
    same width irrespective of their shape, and their straightforward, geometric forms. For reports,
    tabular work, and technical documentation, this technique is used to simulate typewriter output.

    ### Monospace Code (`"monospace-code"`)

    ```css
    font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace;
    ```

    Specifically created for use in programming and other technical applications, monospace code
    typefaces are used in these fields. These typefaces are distinguished by their clear, readable
    forms and monospaced design, which ensures that all letters and characters are the same width.

    ### Industrial (`"industrial"`)

    ```css
    font-family: Bahnschrift, 'DIN Alternate', 'Franklin Gothic Medium', 'Nimbus Sans Narrow', sans-serif-condensed, sans-serif;
    ```

    The development of industrial typefaces began in the late 19th century and was greatly
    influenced by the industrial and technological advancements of the time. Industrial typefaces
    are distinguished by their strong sans serif letterforms, straightforward appearance, and use of
    geometric shapes and straight lines.

    ### Rounded Sans (`"rounded-sans"`)

    ```css
    font-family: ui-rounded, 'Hiragino Maru Gothic ProN', Quicksand, Comfortaa, Manjari, 'Arial Rounded MT', 'Arial Rounded MT Bold', Calibri, source-sans-pro, sans-serif;
    ```

    The rounded, curved letterforms that define rounded typefaces give them a softer, friendlier
    appearance. The typeface's rounded edges give it a more natural and playful feel, making it
    appropriate for use in casual or kid-friendly designs. Since the 1950s, the rounded sans-serif
    design has gained popularity and is still frequently used in branding, graphic design, and other
    fields.

    ### Slab Serif (`"slab-serif"`)

    ```css
    font-family: Rockwell, 'Rockwell Nova', 'Roboto Slab', 'DejaVu Serif', 'Sitka Small', serif;
    ```

    Slab Serif typefaces are distinguished by the thick, block-like serifs that appear at the ends
    of each letterform. Typically, these serifs are unbracketed, which means that they do not have
    any curved or tapered transitions to the letter's main stroke.

    ### Antique (`"antique"`)

    ```css
    font-family: Superclarendon, 'Bookman Old Style', 'URW Bookman', 'URW Bookman L', 'Georgia Pro', Georgia, serif;
    ```

    Serif typefaces that were popular in the 19th century include antique typefaces, also referred
    to as Egyptians. They are distinguished by their thick, uniform stroke weight and block-like
    serifs. The typeface *Clarendon* is a highly regarded example of this style and *Superclarendon*
    is a modern take on that revered typeface.

    ### Didone (`"didone"`)

    ```css
    font-family: Didot, 'Bodoni MT', 'Noto Serif Display', 'URW Palladio L', P052, Sylfaen, serif;
    ```

    Didone typefaces, also referred to as Modern typefaces, are distinguished by their vertical
    stress, sharp contrast between thick and thin strokes, and hairline serifs without bracketing.
    The Didone style first appeared in the late 18th century and became well-known in the early
    19th century. *Bodoni* and *Didot* are two of the most well-known typefaces in this category.

    ### Handwritten (`"handwritten"`)

    ```css
    font-family: 'Segoe Print', 'Bradley Hand', Chilanka, TSCu_Comic, casual, cursive;
    ```

    The appearance and feel of handwriting are replicated by handwritten typefaces. Although there
    are a wide variety of handwriting styles, this font stack tends to use a more casual and
    commonplace style. In regards to these types of fonts in tables, one can say that any table
    having a handwritten font will evoke a feeling of gleefulness.

    Examples
    --------
    Using select columns from the `exibble` dataset, let's create a table with a number of
    components added. Following that, we'll set a font for the entire table using the
    `tab_options()` method with the `table_font_names` parameter. Instead of passing a list of font
    names, we'll use the `system_fonts()` helper function to get a font stack. In this case, we'll
    use the `"industrial"` font stack.

    ```{python}
    from great_tables import GT, exibble, md, system_fonts

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
      .tab_options(table_font_names=system_fonts("industrial"))
    )
    ```

    Invoking the `system_fonts()` helper function with the `"industrial"` argument will return a
    list of font names that make up the font stack. This is exactly the type of input that the
    `table_font_names` parameter requires.
    """
    return _get_font_stack(name)


def _get_font_stack(name: FontStackName = "system-ui", add_emoji: bool = True) -> list[str]:
    font_stack = FONT_STACKS.get(name)

    if font_stack is None:
        raise ValueError(f"Invalid font stack name: {name}")

    if add_emoji:
        font_stack.extend(
            ["Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"]
        )

    return font_stack


def _generate_tokens_list(units_notation: str) -> list[str]:
    # Remove any surrounding double braces before splitting the string into a list of tokens
    tokens_list = re.split(r"\s+", re.sub(r"^\{\{\s*|\s*\}\}$", "", units_notation))

    # Remove any empty tokens (i.e., `None` or `""`)
    tokens_list = [token for token in tokens_list if token != "" and token is not None]

    # Replace any instances of `/<text>` with `<text>^-1`
    tokens_list = [
        re.sub(r"^/", "", x) + "^-1" if re.match(r"^/", x) and len(x) > 1 else x
        for x in tokens_list
    ]

    return tokens_list


def _intify_scaled_px(v: str, scale: float) -> int:
    return int(float(v.removesuffix("px")) * scale)


@dataclass
class UnitDefinition:
    token: str
    unit: str
    unit_subscript: str | None = None
    exponent: str | None = None
    sub_super_overstrike: bool = False
    chemical_formula: bool = False
    built: str | None = None

    @classmethod
    def from_token(cls, token: str) -> UnitDefinition:
        unit_subscript = None
        sub_super_overstrike = False
        chemical_formula = False
        exponent = None

        # Case: Chemical formula
        #   * e.g. "%C6H12O6%", where the '%' characters are used to denote a chemical formula
        if re.match(r"^%.*%$", token) and len(token) > 2:
            chemical_formula = True

            # Extract the formula w/o the surrounding `%` signs
            unit = re.sub(r"^%|%$", "", token)

        # Case: Subscript and exponent present inside square brackets, so overstriking required
        #   * e.g., 'm_[0^3]'
        elif re.search(r".+?\[_.+?\^.+?\]", token):
            sub_super_overstrike = True

            # Extract the unit w/o subscript from the string
            unit = re.sub(r"(.+?)\[_.+?\^.+?\]", r"\1", token)

            # Obtain only the subscript/exponent of the string
            sub_exponent = re.sub(r".+?\[(_.+?\^.+?)\]", r"\1", token)

            # Extract the content after the underscore
            unit_subscript = re.sub(r"^_(.+?)(\^.+?)$", r"\1", sub_exponent)

            # Extract the content after the caret
            exponent = re.sub(r"_.+?\^(.+?)", r"\1", sub_exponent)

        # Case: Subscript and exponent present (overstriking is *not* required here)
        #   * e.g., 'm_2^3'
        elif re.search(r".+?_.+?\^.+?", token):
            # Extract the unit w/o subscript from the string
            unit = re.sub(r"^(.+?)_.+?\^.+?$", r"\1", token)

            # Obtain only the subscript/exponent portion of the string
            sub_exponent = re.sub(r".+?(_.+?\^.+?)$", r"\1", token)

            # Extract the content after the underscore
            unit_subscript = re.sub(r"^_(.+?)\^.+?$", r"\1", sub_exponent)

            # Extract the content after the caret
            exponent = re.sub(r"^_.+?\^(.+?)$", r"\1", sub_exponent)

        # Case: Only an exponent is present
        #   * the previous cases handled the presence of a subscript and exponent, but this case
        #     only handles the presence of an exponent (indicated by the '^' character anywhere
        #     in the string)
        #   * e.g., 'm^2'
        elif re.search(r"\^", token):
            # Extract the unit w/o exponent from the string
            unit = re.sub(r"^(.+?)\^.+?$", r"\1", token)

            # Obtain only the exponent portion of the string
            exponent = re.sub(r"^.+?\^(.+?)$", r"\1", token)

        # Case: Only a subscript is present
        #   * this case handles the presence of a single subscript (indicated by the '_' character
        #     anywhere in the string)
        #   * e.g., 'm_2'
        elif re.search(r"_", token):
            # Extract the unit w/o subscript from the string
            unit = re.sub(r"^(.+?)_.+?$", r"\1", token)

            # Obtain only the subscript portion of the string
            unit_subscript = re.sub(r"^.+?_(.+?)$", r"\1", token)
        else:
            unit = token

        return cls(token, unit, unit_subscript, exponent, sub_super_overstrike, chemical_formula)

    def to_html(self):
        units_str = ""

        units_object = self

        # Perform formatting of of the unit:
        #   * The `unit` attribute is the main part of the unit (e.g., 'm' in 'm^2')
        #   * The `unit` component should never be `None`
        #   * We take a simpler approach to formatting the unit when it only contains
        #     a single character (no use of `_units_symbol_replacements()` here)
        if len(units_object.unit) > 1:
            unit = _md_html(
                _escape_html_tags(
                    _units_symbol_replacements(text=units_object.unit.replace("-", "&minus;"))
                )
            )

        else:
            unit = _md_html(units_object.unit.replace("-", "&minus;"))

        # In the special case where the unit is 'x10', we replace the 'x' with a
        # multiplication symbol:
        #   * This isn't done unit is a chemical formula since it's not necessary
        #   * This is practical for having scalar multipliers mixed in with units and typically
        #     this is raised to a power (e.g., 'x10^6') and often placed before the inline units
        if "x10" in unit and not units_object.chemical_formula:
            unit = unit.replace("x", "&times;")

        # Perform formatting of the exponent:
        #   * The `exponent` attribute is the exponent part of the unit (e.g., '2' in 'm^2')
        #   * The `exponent` component can be `None` if the unit does not have an exponent
        #   * When the `exponent` component is a string of length greater than 2, we also use
        #     `_units_symbol_replacements()` function to format the exponent)
        if units_object.exponent is None:
            exponent = None

        elif len(units_object.exponent) > 2:
            exponent = _units_to_superscript(
                _md_html(
                    _escape_html_tags(
                        _units_symbol_replacements(
                            text=units_object.exponent.replace("-", "&minus;")
                        )
                    )
                )
            )

        else:
            exponent = _units_to_superscript(content=units_object.exponent.replace("-", "&minus;"))

        # Perform formatting of the unit subscript:
        #   * The `unit_subscript` attribute is the subscript part of the unit (e.g., '2' in
        #     'm_2')
        #   * The `unit_subscript` component can be `None` if the unit does not have a subscript
        #   * When the `unit_subscript` component is a string of length greater than 2, we also
        #     use `_units_symbol_replacements()` function to format the subscript)
        if units_object.unit_subscript is None:
            unit_subscript = None

        elif len(units_object.unit_subscript) > 2:
            unit_subscript = _units_to_subscript(
                _md_html(
                    _escape_html_tags(
                        _units_symbol_replacements(
                            text=units_object.unit_subscript.replace("-", "&minus;")
                        )
                    )
                )
            )

        else:
            unit_subscript = _units_to_subscript(
                content=units_object.unit_subscript.replace("-", "&minus;")
            )

        units_str += unit

        # In the special case where the subscript and exponents are present and overstriking
        # is required, we use the `_units_html_sub_super()` function to format the subscript
        # and exponent:
        #   * The subscript and exponent are placed on top of each other, with left alignment
        #   * This bypasses the earlier formatting of the subscript and exponent
        #   * The result is placed to the right of the unit
        if (
            units_object.sub_super_overstrike
            and units_object.unit_subscript is not None
            and units_object.exponent is not None
        ):
            units_str += _units_html_sub_super(
                content_sub=_md_html(
                    _escape_html_tags(
                        _units_symbol_replacements(
                            text=units_object.unit_subscript.replace("-", "&minus;")
                        )
                    )
                ),
                content_sup=_md_html(
                    _escape_html_tags(
                        _units_symbol_replacements(
                            text=units_object.exponent.replace("-", "&minus;")
                        )
                    )
                ),
            )

        # In the special case where the unit is a chemical formula, we take the formatted unit
        # and place all numbers (which are recognized now to be part of the chemical formula)
        # into spans that are styled to be subscripts:
        elif units_object.chemical_formula:
            units_str = re.sub(
                "(\\d+)",
                '<span style="white-space:nowrap;"><sub style="line-height:0;">\\1</sub></span>',
                units_str,
            )

        else:
            if unit_subscript is not None:
                units_str += unit_subscript

            if exponent is not None:
                units_str += exponent

        return units_str


class UnitStr(BaseText):
    def __init__(self, units_str: list[str | UnitDefinitionList]):
        self.units_str = units_str

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.units_str})"

    def to_html(self) -> str:
        built_units = "".join(
            [
                unit_def.to_html() if isinstance(unit_def, UnitDefinitionList) else unit_def
                for unit_def in self.units_str
            ]
        )

        return built_units

    def to_latex(self) -> str:
        raise NotImplementedError("LaTeX conversion of units is not yet supported.")

    def _repr_html_(self):
        return self.to_html()

    def __len__(self) -> int:
        return len(self.units_str)

    @classmethod
    def from_str(cls, string: str) -> Self:
        # "energy ({{J m^-1}})"
        # UnitStr(["energy (", define_units("J m^-1"), ")"])

        # "speed {{m s^-1}} and acceleration {{m s^-2}}"
        # UnitStr(["speed ", define_units("m s^-1"), " and acceleration ", define_units("m s^-2")])

        # "speed {{ s^-1"
        # UnitStr(["speed {{m s^-1"])

        # "speed m s^-1}}"
        # UnitStr(["speed m s^-1}}"])

        token_parts: list[str | UnitDefinitionList] = []

        for part in re.split(r"(\{\{.*?\}\})", string):
            m = re.match(r"\{\{(.*?)\}\}", part)

            if m:
                token_parts.append(define_units(m.group(1)))
            else:
                token_parts.append(part)

        return cls(token_parts)


@dataclass
class UnitDefinitionList:
    units_list: list[UnitDefinition]

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.units_list})"

    def __len__(self) -> int:
        return len(self.units_list)

    def __getitem__(self, index: int) -> UnitDefinition:
        return self.units_list[index]

    def to_html(self) -> str:
        built_units = [unit_def.to_html() for unit_def in self.units_list]

        units_str = ""

        for unit_add in built_units:
            if re.search("\\($|\\[$", units_str) or re.search("^\\)|^\\]", unit_add):
                spacer = ""
            else:
                spacer = " "

            if len(self) == 3 and self[1].unit == "/":
                spacer = ""

            units_str += f"{spacer}{unit_add}"

        units_str = re.sub("^\\s+|\\s+$", "", units_str)

        return units_str

    def _repr_html_(self):
        return self.to_html()


def _units_to_subscript(content: str) -> str:
    return (
        '<span style="white-space:nowrap;"><sub style="line-height:0;">' + content + "</sub></span>"
    )


def _units_to_superscript(content: str) -> str:
    return (
        '<span style="white-space:nowrap;"><sup style="line-height:0;">' + content + "</sup></span>"
    )


def _units_html_sub_super(content_sub: str, content_sup: str) -> str:
    return (
        '<span style="display:inline-block;line-height:1em;text-align:left;font-size:60%;vertical-align:-0.25em;margin-left:0.1em;">'
        + content_sup
        + "<br>"
        + content_sub
        + "</span>"
    )


def _replace_units_symbol(text: str, detect: str, pattern: str, replace: str) -> str:
    if re.search(detect, text):
        text = re.sub(pattern, replace, text)

    return text


def _units_symbol_replacements(text: str) -> str:
    # Replace certain units symbols with HTML entities; these are cases where the parsed
    # text should be at the beginning of a string (or should be the entire string)
    text = _replace_units_symbol(text, "^-", "^-", "&minus;")
    text = _replace_units_symbol(text, "^um$", "um", "&micro;m")
    text = _replace_units_symbol(text, "^uL$", "uL", "&micro;L")
    text = _replace_units_symbol(text, "^umol", "^umol", "&micro;mol")
    text = _replace_units_symbol(text, "^ug$", "ug", "&micro;g")
    text = _replace_units_symbol(text, "^ohm$", "ohm", "&#8486;")

    # Loop through the dictionary of units symbols and replace them with their HTML entities
    for key, value in UNITS_SYMBOLS_HTML.items():
        text = _replace_units_symbol(text, key, key, value)

    return text


def _escape_html_tags(text: str) -> str:
    # Replace the '<' and '>' characters with their HTML entity equivalents
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    return text


UNITS_SYMBOLS_HTML = {
    "degC": "&deg;C",
    "degF": "&deg;F",
    ":pm:": "&plusmn;",
    ":mp:": "&mnplus;",
    ":lt:": "&lt;",
    ":gt:": "&gt;",
    ":le:": "&le;",
    ":ge:": "&ge;",
    ":cdot:": "&sdot;",
    ":times:": "&times;",
    ":div:": "&divide;",
    ":ne:": "&ne;",
    ":prime:": "&prime;",
    ":rightarrow:": "&rarr;",
    ":leftarrow:": "&larr;",
    ":micro:": "&micro;",
    ":ohm:": "&#8486;",
    ":angstrom:": "&#8491;",
    ":plusminus:": "&plusmn;",
    ":permil:": "&permil;",
    ":permille:": "&permil;",
    ":degree:": "&deg;",
    ":degrees:": "&deg;",
    ":space:": "&nbsp;",
    ":Alpha:": "&Alpha;",
    ":alpha:": "&alpha;",
    ":Beta:": "&Beta;",
    ":beta:": "&beta;",
    ":Gamma:": "&Gamma;",
    ":gamma:": "&gamma;",
    ":Delta:": "&Delta;",
    ":delta:": "&delta;",
    ":Epsilon:": "&Epsilon;",
    ":epsilon:": "&epsilon;",
    ":varepsilon:": "&varepsilon;",
    ":Zeta:": "&Zeta;",
    ":zeta:": "&zeta;",
    ":Eta:": "&Eta;",
    ":eta:": "&eta;",
    ":Theta:": "&Theta;",
    ":theta:": "&theta;",
    ":vartheta:": "&vartheta;",
    ":Iota:": "&Iota;",
    ":iota:": "&iota;",
    ":Kappa:": "&Kappa;",
    ":kappa:": "&kappa;",
    ":Lambda:": "&Lambda;",
    ":lambda:": "&lambda;",
    ":Mu:": "&Mu;",
    ":mu:": "&mu;",
    ":Nu:": "&Nu;",
    ":nu:": "&nu;",
    ":Xi:": "&Xi;",
    ":xi:": "&xi;",
    ":Omicron:": "&Omicron;",
    ":omicron:": "&omicron;",
    ":Pi:": "&Pi;",
    ":pi:": "&pi;",
    ":Rho:": "&Rho;",
    ":rho:": "&rho;",
    ":Sigma:": "&Sigma;",
    ":sigma:": "&sigma;",
    ":sigmaf:": "&sigmaf;",
    ":varsigma:": "&varsigma;",
    ":Tau:": "&Tau;",
    ":tau:": "&tau;",
    ":Upsilon:": "&Upsilon;",
    ":upsilon:": "&upsilon;",
    ":Phi:": "&Phi;",
    ":phi:": "&phi;",
    ":Chi:": "&Chi;",
    ":chi:": "&chi;",
    ":Psi:": "&Psi;",
    ":psi:": "&psi;",
    ":Omega:": "&Omega;",
    ":omega:": "&omega;",
}


def define_units(units_notation: str) -> UnitDefinitionList:
    """
    With `define_units()` you can work with a specially-crafted units notation string and emit the
    units as HTML (with the `.to_html()` method). This function is useful as a standalone utility
    and it powers the `fmt_units()` method in **Great Tables**.

    Parameters
    ----------
    units_notation : str
        A string of units notation.

    Returns
    -------
    UnitDefinitionList
        A list of unit definitions.

    Specification of units notation
    -------------------------------

    The following table demonstrates the various ways in which units can be specified in the
    `units_notation` string and how the input is processed by the `define_units()` function. The
    concluding step for display of the units in HTML is to use the `to_html()` method.

    ```{python}
    #| echo: false

    from great_tables import GT, style, loc
    import polars as pl

    units_tbl = pl.DataFrame(
        {
            "rule": [
                "'^' creates a superscript",
                "'_' creates a subscript",
                "subscripts and superscripts can be combined",
                "use '[_subscript^superscript]' to create an overstrike",
                "a '/' at the beginning adds the superscript '-1'",
                "hyphen is transformed to minus sign when preceding a unit",
                "'x' at the beginning is transformed to '×'",
                "ASCII terms from biology/chemistry turned into terminology forms",
                "can create italics with '*' or '_'; create bold text with '**' or '__'",
                "special symbol set surrounded by colons",
                "chemistry notation: '%C6H6%'",
            ],
            "input": [
                "m^2",
                "h_0",
                "h_0^3",
                "h[_0^3]",
                "/s",
                "-h^2",
                "x10^3 kg^2 m^-1",
                "ug",
                "*m*^**2**",
                ":permille:C",
                "g/L %C6H12O6%",
            ],
        }
    ).with_columns(output=pl.col("input"))

    (
        GT(units_tbl)
        .fmt_units(columns="output")
        .tab_style(
            style=style.text(font="courier"),
            locations=loc.body(columns="input")
        )
    )
    ```

    Examples
    --------

    Let’s demonstrate a use case where we utilize `define_units()` to render an equation as
    the subtitle in the table header, which currently doesn’t accept unit notation as input.

    We'll start by creating a Polars DataFrame representing the calculations of the equation
    $y= a_2x^2 + a_1x + a_0$.

    ```{python}
    #| code-fold: true

    import polars as pl
    from great_tables import GT, html, define_units

    df = pl.DataFrame(
        {"x": [1, 2, 3], "a2": [2, 3, 4], "a1": [3, 4, 5], "a0": [4, 5, 6]}
    ).with_columns(
        y=(
            pl.col("a2").mul(pl.col("x").pow(2))
            + pl.col("a1").mul(pl.col("x"))
            + pl.col("a0")
        )
    )

    df
    ```

    If we try to use unit annotations to format the equation as the subtitle in the header, it
    won’t work as expected:

    ```{python}
    (
        GT(df)
        .cols_label(a2="{{a_2}}", a1="{{a_1}}", a0="{{a_0}}")
        .tab_header(title="Linear Algebra", subtitle="y={{a_2}}{{x^2}}+{{a_1}}x+{{a_0}}")
    )
    ```

    To address this, we can create a small helper function, `u2html()`, which wraps a given string
    in `define_units()` and emits the units to HTML. Next, we can build the subtitle by applying
    `u2html()` to the string with unit annotations. Finally, we pass the assembled subtitle string
    through `html()` to ensure it renders correctly.

    ```{python}
    def u2html(x: str) -> str:
        return define_units(x).to_html()


    subtitle = (
        "y"
        + "="
        + u2html("{{a_2}}")
        + u2html("{{x^2}}")
        + "+"
        + u2html("{{a_1}}")
        + "x"
        + "+"
        + u2html("{{a_0}}")
    )

    (
        GT(df)
        .cols_label(a2="{{a_2}}", a1="{{a_1}}", a0="{{a_0}}")
        .tab_header(title="Linear Algebra", subtitle=html(subtitle))
    )
    ```

    """

    # Get a list of raw tokens
    tokens_list = _generate_tokens_list(units_notation=units_notation)

    # Initialize a list to store the units
    units_list = []

    if len(tokens_list) == 0:
        return UnitDefinitionList(units_list=[])

    units_list = [UnitDefinition.from_token(token) for token in tokens_list]
    return UnitDefinitionList(units_list=units_list)


# This could probably be removed and nanoplot_options made into a dataclass
# the built-in dataclass decorator doesn't do any validation / coercion, but
# we could do that in the a __post_init__ hook. (I would switch it over to a
# dataclass and then pair on a post_init hook).
# Check that certain values are either a list or a single value
def _normalize_listable_nanoplot_options(nano_opt: Any, option_type: Any) -> list[Any] | None:
    if nano_opt is None:
        return None

    if not isinstance(nano_opt, (option_type, list)):
        raise ValueError(f"Nanoplot option must be a {option_type} or a list of {option_type}s")

    # If it is a list, check that the values are same as `option_type`
    if isinstance(nano_opt, list):
        if not all(isinstance(x, option_type) for x in nano_opt):
            raise ValueError(f"Nanoplot option must be a list of {option_type}s")

    # If it is a single value, convert it to a list
    if not isinstance(nano_opt, list):
        nano_opt = [nano_opt]

    return nano_opt


def nanoplot_options(
    data_point_radius: int | list[int] | None = None,
    data_point_stroke_color: str | list[str] | None = None,
    data_point_stroke_width: int | list[int] | None = None,
    data_point_fill_color: str | list[str] | None = None,
    data_line_type: str | None = None,
    data_line_stroke_color: str | None = None,
    data_line_stroke_width: int | None = None,
    data_area_fill_color: str | None = None,
    data_bar_stroke_color: str | list[str] | None = None,
    data_bar_stroke_width: int | list[int] | None = None,
    data_bar_fill_color: str | list[str] | None = None,
    data_bar_negative_stroke_color: str | None = None,
    data_bar_negative_stroke_width: int | None = None,
    data_bar_negative_fill_color: str | None = None,
    reference_line_color: str | None = None,
    reference_area_fill_color: str | None = None,
    vertical_guide_stroke_color: str | None = None,
    vertical_guide_stroke_width: int | None = None,
    show_data_points: bool | None = None,
    show_data_line: bool | None = None,
    show_data_area: bool | None = None,
    show_reference_line: bool | None = None,
    show_reference_area: bool | None = None,
    show_vertical_guides: bool | None = None,
    show_y_axis_guide: bool | None = None,
    interactive_data_values: bool | None = None,
    y_val_fmt_fn: Callable[..., str] | None = None,
    y_axis_fmt_fn: Callable[..., str] | None = None,
    y_ref_line_fmt_fn: Callable[..., str] | None = None,
    currency: str | None = None,
) -> dict[str, Any]:
    """
    Helper for setting the options for a nanoplot.

    When using `cols_nanoplot()`, the defaults for the generated nanoplots can be modified with
    `nanoplot_options()` within the `options=` argument.

    Parameters
    ----------

    data_point_radius
        The `data_point_radius=` option lets you set the radius for each of the data points. By
        default this is set to `10`. Individual radius values can be set by using a list of numeric
        values; however, the list provided must match the number of data points.
    data_point_stroke_color
        The default stroke color of the data points is `"#FFFFFF"` (`"white"`). This works well when
        there is a visible data line combined with data points with a darker fill color. The stroke
        color can be modified with `data_point_stroke_color=` for all data points by supplying a
        single color value. With a list of colors, each data point's stroke color can be changed
        (ensure that the list length matches the number of data points).
    data_point_stroke_width
        The width of the outside stroke for the data points can be modified with the
        `data_point_stroke_width=` option. By default, a value of `4` (as in '4px') is used.
    data_point_fill_color
        By default, all data points have a fill color of `"#FF0000"` (`"red"`). This can be changed
        for all data points by providing a different color to `data_point_fill_color=`. And, a list
        of different colors can be supplied so long as the length is equal to the number of data
        points; the fill color values will be applied in order of left to right.
    data_line_type
        This can accept either `"curved"` or `"straight"`. Curved lines are recommended when the
        nanoplot has less than 30 points and data points are evenly spaced. In most other cases,
        straight lines might present better.
    data_line_stroke_color
        The color of the data line can be modified from its default `"#4682B4"` (`"steelblue"`)
        color by supplying a color to the `data_line_stroke_color=` option.
    data_line_stroke_width
        The width of the connecting data line can be modified with `data_line_stroke_width=`. By
        default, a value of `4` (as in '4px') is used.
    data_area_fill_color
        The fill color for the area that bounds the data points in line plot. The default is
        `"#FF0000"` (`"red"`) but can be changed by providing a color value to
        `data_area_fill_color=`.
    data_bar_stroke_color
        The color of the stroke used for the data bars can be modified from its default `"#3290CC"`
        color by supplying a color to `data_bar_stroke_color=`.
    data_bar_stroke_width
        The width of the stroke used for the data bars can be modified with the
        `data_bar_stroke_width=` option. By default, a value of `4` (as in '4px') is used.
    data_bar_fill_color
        By default, all data bars have a fill color of `"#3FB5FF"`. This can be changed for all data
        bars by providing a different color to `data_bar_fill_color=`. And, a list of different
        colors can be supplied so long as the length is equal to the number of data bars; the fill
        color values will be applied in order of left to right.
    data_bar_negative_stroke_color
        The color of the stroke used for the data bars that have negative values. The default color
        is `"#CC3243"` but this can be changed by supplying a color value to the
        `data_bar_negative_stroke_color=` option.
    data_bar_negative_stroke_width
        The width of the stroke used for negative value data bars. This has the same default as
        `data_bar_stroke_width=` with a value of `4` (as in '4px'). This can be changed by giving a
        numeric value to the `data_bar_negative_stroke_width=` option.
    data_bar_negative_fill_color
        By default, all negative data bars have a fill color of `"#D75A68"`. This can however be
        changed by providing a color value to `data_bar_negative_fill_color=`.
    reference_line_color
        The reference line will have a color of `"#75A8B0"` if it is set to appear. This color can
        be changed by providing a single color value to `reference_line_color=`.
    reference_area_fill_color
        If a reference area has been defined and is visible it has by default a fill color of
        `"#A6E6F2"`. This can be modified by declaring a color value in the
        `reference_area_fill_color=` option.
    vertical_guide_stroke_color
        Vertical guides appear when hovering in the vicinity of data points. Their default color is
        `"#911EB4"` (a strong magenta color) and a fill opacity value of `0.4` is automatically
        applied to this. However, the base color can be changed with the
        `vertical_guide_stroke_color=` option.
    vertical_guide_stroke_width
        The vertical guide's stroke width, by default, is relatively large at `12` (this is '12px').
        This is modifiable by setting a different value with `vertical_guide_stroke_width=`.
    show_data_points
        By default, all data points in a nanoplot are shown but this layer can be hidden by setting
        `show_data_points=` to `False`.
    show_data_line
        The data line connects data points together and it is shown by default. This data line layer
        can be hidden by setting `show_data_line=` to `False`.
    show_data_area
        The data area layer is adjacent to the data points and the data line. It is shown by default
        but can be hidden with `show_data_area=False`.
    show_reference_line
        The layer with a horizontal reference line appears underneath that of the data points and
        the data line. Like vertical guides, hovering over a reference will show its value. The
        reference line (if available) is shown by default but can be hidden by setting
        `show_reference_line=` to `False`.
    show_reference_area
        The reference area appears at the very bottom of the layer stack, if it is available (i.e.,
        defined in `cols_nanoplot()`). It will be shown in the default case but can be hidden by
        using `show_reference_area=False`.
    show_vertical_guides
        Vertical guides appear when hovering over data points. This hidden layer is active by
        default but can be deactivated by using `show_vertical_guides=False`.
    show_y_axis_guide
        The *y*-axis guide will appear when hovering over the far left side of a nanoplot. This
        hidden layer is active by default but can be deactivated by using `show_y_axis_guide=False`.
    interactive_data_values
        By default, numeric data values will be shown only when the user interacts with certain
        regions of a nanoplot. This is because the values may be numerous (i.e., clutter the display
        when all are visible) and it can be argued that the values themselves are secondary to the
        presentation. However, for some types of plots (like horizontal bar plots), a persistent
        display of values alongside the plot marks may be desirable. By setting
        `interactive_data_values=False` we can opt for always displaying the data values alongside
        the plot components.
    y_val_fmt_fn
        If providing a function to `y_val_fmt_fn=`, customized formatting of the *y* values
        associated with the data points/bars is possible.
    y_axis_fmt_fn
        A function supplied to `y_axis_fmt_fn=` will result in customized formatting of the *y*-axis
        label values.
    y_ref_line_fmt_fn
        Providing a function for `y_ref_line_fmt_fn=` yields customized formatting of the reference
        line (if present).
    currency
        If the values are to be displayed as currency values, supply either: (1) a 3-letter currency
        code (e.g., `"USD"` for U.S. Dollars, `"EUR"` for the Euro currency), or (2) a common
        currency name (e.g., `"dollar"`, `"pound"`, `"yen"`, etc.).

    Examples
    --------
    See [`fmt_nanoplot()`](`great_tables.GT.fmt_nanoplot`).
    """

    data_point_radius = _normalize_listable_nanoplot_options(
        nano_opt=data_point_radius, option_type=int
    )
    data_point_stroke_color = _normalize_listable_nanoplot_options(
        nano_opt=data_point_stroke_color, option_type=str
    )
    data_point_stroke_width = _normalize_listable_nanoplot_options(
        nano_opt=data_point_stroke_width, option_type=int
    )
    data_point_fill_color = _normalize_listable_nanoplot_options(
        nano_opt=data_point_fill_color, option_type=str
    )
    data_bar_stroke_color = _normalize_listable_nanoplot_options(
        nano_opt=data_bar_stroke_color, option_type=str
    )
    data_bar_stroke_width = _normalize_listable_nanoplot_options(
        nano_opt=data_bar_stroke_width, option_type=int
    )
    data_bar_fill_color = _normalize_listable_nanoplot_options(
        nano_opt=data_bar_fill_color, option_type=str
    )

    data_point_radius = data_point_radius or 10
    data_point_stroke_color = data_point_stroke_color or "#FFFFFF"
    data_point_stroke_width = data_point_stroke_width or 4
    data_point_fill_color = data_point_fill_color or "#FF0000"

    data_line_type = data_line_type or "curved"
    data_line_stroke_color = data_line_stroke_color or "#4682B4"
    data_line_stroke_width = data_line_stroke_width or 8

    data_area_fill_color = data_area_fill_color or "#FF0000"

    data_bar_stroke_color = data_bar_stroke_color or "#3290CC"
    data_bar_stroke_width = data_bar_stroke_width or 4
    data_bar_fill_color = data_bar_fill_color or "#3FB5FF"

    data_bar_negative_stroke_color = data_bar_negative_stroke_color or "#CC3243"
    data_bar_negative_stroke_width = data_bar_negative_stroke_width or 4
    data_bar_negative_fill_color = data_bar_negative_fill_color or "#D75A68"

    reference_line_color = reference_line_color or "#75A8B0"
    reference_area_fill_color = reference_area_fill_color or "#A6E6F2"

    vertical_guide_stroke_color = vertical_guide_stroke_color or "#911EB4"
    vertical_guide_stroke_width = vertical_guide_stroke_width or 12

    show_data_points = True if show_data_points is None else show_data_points
    show_data_line = True if show_data_line is None else show_data_line
    show_data_area = True if show_data_area is None else show_data_area
    show_reference_line = True if show_reference_line is None else show_reference_line
    show_reference_area = True if show_reference_area is None else show_reference_area
    show_vertical_guides = True if show_vertical_guides is None else show_vertical_guides
    show_y_axis_guide = True if show_y_axis_guide is None else show_y_axis_guide

    interactive_data_values = interactive_data_values or True

    # y_val_fmt_fn, y_axis_fmt_fn, and y_ref_line_fmt_fn
    # are not assigned to a default value

    # currency is also not assigned a default value.

    nanoplot_options_dict = {
        "data_point_radius": data_point_radius,
        "data_point_stroke_color": data_point_stroke_color,
        "data_point_stroke_width": data_point_stroke_width,
        "data_point_fill_color": data_point_fill_color,
        "data_line_type": data_line_type,
        "data_line_stroke_color": data_line_stroke_color,
        "data_line_stroke_width": data_line_stroke_width,
        "data_area_fill_color": data_area_fill_color,
        "data_bar_stroke_color": data_bar_stroke_color,
        "data_bar_stroke_width": data_bar_stroke_width,
        "data_bar_fill_color": data_bar_fill_color,
        "data_bar_negative_stroke_color": data_bar_negative_stroke_color,
        "data_bar_negative_stroke_width": data_bar_negative_stroke_width,
        "data_bar_negative_fill_color": data_bar_negative_fill_color,
        "reference_line_color": reference_line_color,
        "reference_area_fill_color": reference_area_fill_color,
        "vertical_guide_stroke_color": vertical_guide_stroke_color,
        "vertical_guide_stroke_width": vertical_guide_stroke_width,
        "show_data_points": show_data_points,
        "show_data_line": show_data_line,
        "show_data_area": show_data_area,
        "show_reference_line": show_reference_line,
        "show_reference_area": show_reference_area,
        "show_vertical_guides": show_vertical_guides,
        "show_y_axis_guide": show_y_axis_guide,
        "interactive_data_values": interactive_data_values,
        "y_val_fmt_fn": y_val_fmt_fn,
        "y_axis_fmt_fn": y_axis_fmt_fn,
        "y_ref_line_fmt_fn": y_ref_line_fmt_fn,
        "currency": currency,
    }

    return nanoplot_options_dict
