from __future__ import annotations

import tempfile
import time
import warnings
import webbrowser
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from typing_extensions import TypeAlias

from ._helpers import random_id
from ._scss import compile_scss
from ._utils import _try_import
from ._utils_render_latex import _render_as_latex

if TYPE_CHECKING:
    # Note that as_raw_html uses methods on the GT class, not just data
    from IPython.core.interactiveshell import InteractiveShell
    from selenium import webdriver

    from ._types import GTSelf
    from .gt import GT


class PatchedHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Patched handler, which does not log requests to stderr"""


class MISSING:
    """Represent a missing argument (where None has a special meaning)."""


def _create_temp_file_server(fname: Path) -> HTTPServer:
    """Return a HTTPServer, so we can serve a single request (to show the table)."""

    Handler = partial(PatchedHTTPRequestHandler, directory=str(fname.parent))
    server = HTTPServer(("127.0.0.1", 0), Handler)

    return server


def _infer_render_target(
    ipy: InteractiveShell | None | type = MISSING,
) -> Literal["auto", "notebook", "browser"]:
    # adapted from py-htmltools
    # Note that `ipy` arguments are possible return values of IPython.get_ipython()
    # They are manually passed in from unit tests to validate this function.
    target: Literal["auto", "notebook", "browser"]
    try:
        import IPython  # pyright: ignore[reportUnknownVariableType]
        from IPython.terminal.interactiveshell import TerminalInteractiveShell

        if ipy is MISSING:
            # Note that get_ipython may be None, to indicate no shell in use
            # e.g. if you're in the normal python repl
            ipy = IPython.get_ipython()

        if isinstance(ipy, TerminalInteractiveShell):
            target = "browser"
        elif ipy is None:
            target = "browser"
        else:
            target = "notebook"

    except ImportError:
        target = "browser"

    return target


def show(
    self: GTSelf,
    target: Literal["auto", "notebook", "browser"] = "auto",
):
    """Display the table in a notebook or a web browser.

    Note that this function is often unecessary in a notebook. However, it's sometimes useful for
    manually triggering display within a code cell.

    Parameters
    ----------
    target:
        Where to show the table. If "auto", infer whether the table can be displayed inline (e.g. in
        a notebook), or whether a browser is needed (e.g. in a console).

    Examples
    --------

    The example below when in the Great Tables documentation, should appear on the page.

    ```{python}
    from great_tables import GT, exibble

    GT(exibble.head(2)).show()
    GT(exibble.tail(2)).show()
    ```

    """

    if target == "auto":
        target = _infer_render_target()

    if target == "notebook":
        from IPython.core.display import display_html

        html = self._repr_html_()

        # https://github.com/ipython/ipython/pull/10962
        display_html(  # pyright: ignore[reportUnknownVariableType]
            html, raw=True, metadata={"text/html": {"isolated": True}}
        )
    elif target == "browser":
        html = self.as_raw_html(make_page=True)
        with tempfile.TemporaryDirectory() as tmp_dir:
            f_path = Path(tmp_dir) / "index.html"
            f_path.write_text(html, encoding="utf-8")

            # create a server that closes after 1 request ----
            server = _create_temp_file_server(f_path)
            webbrowser.open(f"http://127.0.0.1:{server.server_port}/{f_path.name}")
            server.handle_request()
    else:
        raise Exception(f"Unknown target display: {target}")


def as_raw_html(
    self: GT,
    inline_css: bool = False,
    make_page: bool = False,
    all_important: bool = False,
) -> str:
    """
    Get the HTML content of a GT object.

    Get the HTML content from a GT object as a string. By default, the generated HTML will have
    inlined styles, where CSS styles (that were previously contained in CSS rule sets external to
    the `<table>` element are included as style attributes in the HTML table's tags. This option is
    preferable when using the output HTML table in an emailing context.

    Parameters
    ----------
    gt
        A GT object.
    inline_css
        An option to supply styles to table elements as inlined CSS styles. This is useful when
        including the table HTML as part of an HTML email message body, since inlined styles are
        largely supported in email clients over using CSS in a `<style>` block.
    make_page
        An option to wrap the table in a complete HTML page. This is useful when you want to display
        the table in a web browser.

    Returns
    -------
    str
        An HTML fragment containing a table.

    Examples:
    ------
    Let's use a subset of the `gtcars` dataset to create a new table.

    ```{python}
    from great_tables import GT, md, style, loc
    from great_tables.data import gtcars
    import polars as pl

    gtcars_mini = (
        pl.from_pandas(gtcars)
        .select(["mfr", "model", "msrp"])
        .head(5)
    )

    gt_tbl = (
        GT(gtcars_mini)
        .tab_header(
            title=md("Data listing from **gtcars**"),
            subtitle=md("gtcars is an R dataset")
        )
        .tab_style(
            style=style.fill(color="LightCyan"),
            locations=loc.body(columns="mfr")
        )
        .fmt_currency(columns="msrp")
        .tab_options(
            heading_background_color="Azure",
            table_body_hlines_color="Lavender",
            table_body_hlines_width="2px"
        )
        .opt_horizontal_padding(scale=2)
    )

    gt_tbl
    ```

    Now we can return the table as an HTML string using the `as_raw_html()` method.

    ```{python}
    gt_tbl.as_raw_html()
    ```

    The HTML string contains the HTML for the table. It has only the table so it's not a complete
    HTML document but rather an HTML fragment. While this useful for embedding a table in an
    existing HTML document, you could also use the `make_page=True` argument to get a complete HTML
    page with the table contained within.

    ```{python}
    gt_tbl.as_raw_html(make_page=True)
    ```

    Should you want to include all of the CSS styles as inline styles, you can use `inline_css=True`
    to get an HTML string with all CSS inlined into the HTML tags.

    ```{python}
    gt_tbl.as_raw_html(inline_css=True)
    ```
    """

    built_table = self._build_data(context="html")

    table_html = built_table._render_as_html(
        make_page=make_page,
        all_important=all_important,
    )

    if inline_css:
        _try_import(name="css_inline", pip_install_line="pip install css-inline")
        from css_inline import inline, inline_fragment

        if make_page:
            return inline(html=table_html)

        else:
            # Obtain the `table_id` value from the Options (might be set, might be None)
            table_id = self._options.table_id.value

            if table_id is None:
                id = random_id()
            else:
                id = table_id

            # Compile the SCSS as CSS
            table_css = str(compile_scss(self, id=id, compress=False, all_important=all_important))

            return inline_fragment(html=table_html, css=table_css)

    return table_html


def as_latex(self: GT, use_longtable: bool = False, tbl_pos: str | None = None) -> str:
    """
    Output a GT object as LaTeX

    The `as_latex()` method outputs a GT object as a LaTeX fragment. This method is useful for when
    you need to include a table as part of a LaTeX document. The LaTeX fragment contains the table
    as a string.

    :::{.callout-warning}
    `as_latex()` is still experimental.
    :::

    Parameters
    ----------

    use_longtable
        An option to use the `longtable` environment in LaTeX output. This is useful for tables that
        span multiple pages and don't require precise positioning.
    tbl_pos
        The position of the table in the LaTeX output when `use_longtable=False`. Valid values for
        positioning include `"!t"` (top of page), `"!b"` (bottom of the page), `"!h"` (here),
        `"!p"` (on a separate page), and `"!H"` (exactly here). If a value is not provided then the
        table will be placed at the top of the page; if in the Quarto render then the table
        positioning option will be ignored in favor of any setting within the Quarto rendering
        environment.

    Returns
    -------
    str
        A LaTeX fragment that contains the table.

    Limitations
    -----------
    The `as_latex()` method is still experimental and has some limitations. The following
    functionality that is supported in HTML output tables is not currently supported in LaTeX
    output tables:

    - the rendering of the stub and row group labels (via the `=rowname_col` and `=groupname_col`
      args in the `GT()` class)
    - the use of the `md()` helper function to signal conversion of Markdown text
    - units notation within the `cols_labels()` and `tab_spanner()` methods
    - the `fmt_markdown()`, `fmt_units()`, `fmt_image()`, and `fmt_nanoplot()` methods
    - the `sub_missing()` and `sub_zero()` methods
    - most options in the `tab_options()` method, particularly those that are specific to styling
      text, borders, or adding fill colors to cells

    As development continues, we will work to expand the capabilities of the `as_latex()` method to
    reduce these limitations and more clearly document what is and is not supported.

    Examples
    --------
    Let's use a subset of the `gtcars` dataset to create a new table.

    ```{python}
    from great_tables import GT
    from great_tables.data import gtcars
    import polars as pl

    gtcars_mini = (
        pl.from_pandas(gtcars)
        .select(["mfr", "model", "msrp"])
        .head(5)
    )

    gt_tbl = (
        GT(gtcars_mini)
        .tab_header(
            title="Data Listing from the gtcars Dataset",
            subtitle="Only five rows from the dataset are shown here."
        )
        .fmt_currency(columns="msrp")
    )

    gt_tbl
    ```

    Now we can return the table as string of LaTeX code using the `as_latex()` method.

    ```{python}
    gt_tbl.as_latex()
    ```

    The LaTeX string contains the code just for the table (it's not a complete LaTeX document).
    This output can be useful for embedding a GT table in an existing LaTeX document.
    """
    built_table = self._build_data(context="latex")

    latex_table = _render_as_latex(data=built_table, use_longtable=use_longtable, tbl_pos=tbl_pos)

    return latex_table


# Create a list of all selenium webdrivers
WebDrivers: TypeAlias = Literal[
    "chrome",
    "firefox",
    "safari",
    "edge",
]

DebugDumpOptions: TypeAlias = Literal["zoom", "width_resize", "final_resize"]


def save(
    self: GT,
    file: Path | str,
    selector: str = "table",
    scale: float = 1.0,
    expand: int = 5,
    web_driver: WebDrivers | webdriver.Remote = "chrome",
    window_size: tuple[int, int] = (6000, 6000),
    debug_port: None | int = None,
    encoding: str = "utf-8",
    _debug_dump: DebugDumpOptions | None = None,
) -> GTSelf:
    """
    Produce a high-resolution image file or PDF of the table.

    The output file is created by taking a screenshot of the table using a headless browser.

    Parameters
    ----------
    file
        The name of the file to save the image to. Accepts names ending with .png, .bmp, and other
        image extensions. Also accepts the extension .pdf.
    selector
        (NOT IMPLEMENTED) The HTML element name used to select table. Defaults to the whole table.
    scale
        The scaling factor that will be used when generating the image.  Lower values decrease
        resolution. A scale of 2 is equivalent to doubling the width of the table in pixels. Note
        that higher resolution results in larger file sizes.
    expand
        (NOT IMPLEMENTED) The number of pixels to expand the screenshot by.  This can be
        increased to capture more of the surrounding area, or decreased to capture less.
    web_driver
        The webdriver to use when taking the screenshot. Either a driver name, or webdriver
        instance. By default, uses Google Chrome. Supports `"firefox"` (Mozilla Firefox), `"safari"`
        (Apple Safari), and `"edge"` (Microsoft Edge).

        Specified browser must be installed. Note that if a webdriver instance is passed, options
        that require setting up a webdriver, like debug_port, will not be used.
    window_size
        The size of the browser window to use when laying out the table. This shouldn't be necessary
        to capture a table, but may affect the tables appearance.
    debug_port
        Port number to use for debugging. By default no debugging port is opened.
    encoding
        The character encoding used for the HTML content.
    _debug_dump
        Whether the saved image should be a big browser window, with key elements outlined. This is
        helpful for debugging this function's resizing, cropping heuristics. This is an internal
        parameter and subject to change.

    Returns
    -------
    GT
        The GT object is returned. This is the same object that the method is called on so that we
        can facilitate method chaining.

    Details
    -------
    We create the output file based on the HTML version of the table.

    This process is facilitated by two libraries:

    - `selenium`, which is used to control the Chrome browser and take a screenshot of the table.
    - `PIL`, which is used to crop the screenshot to only include the table element of the page.

    Both of these packages needs to be installed before attempting to save any table as an image
    file. The `selenium` package also requires the Chrome browser to be installed on the system.

    A pip-based reinstallation of **Great Tables** through the following command will install these
    required packages:

    ```bash
    pip install great_tables[extra]
    ```

    """
    # Import the required packages
    _try_import(name="selenium", pip_install_line="pip install selenium")

    from ._utils_selenium import _get_web_driver

    if selector != "table":
        raise NotImplementedError("Currently, only selector='table' is supported.")

    # If there is no file extension, add the .png extension
    if Path(file).suffix == "":
        file = str(Path(file).with_suffix(".png"))

    # Get the HTML content from the displayed output
    html_content = as_raw_html(self)

    wdriver = _get_web_driver(web_driver)

    # run browser ----
    with (
        tempfile.TemporaryDirectory() as tmp_dir,
        wdriver(debug_port=debug_port) as headless_browser,
    ):
        # Write the HTML content to the temp file
        with open(f"{tmp_dir}/table.html", "w", encoding=encoding) as temp_file:
            temp_file.write(html_content)

        # Open the HTML file in the headless browser
        headless_browser.set_window_size(*window_size)
        headless_browser.get("file://" + temp_file.name)

        _save_screenshot(headless_browser, scale, file, debug=_debug_dump)

    if debug_port and web_driver not in {"chrome", "firefox"}:
        warnings.warn("debug_port argument only supported on chrome and firefox")
        debug_port = None

    if debug_port:
        input(
            f"Currently debugging on port {debug_port}.\n\n"
            "If you are using Chrome, enter chrome://inspect to preview the headless browser."
            "Other browsers may have different ways to preview headless browser sessions.\n\n"
            "Press enter to continue."
        )

    return self


def _save_screenshot(
    driver: webdriver.Chrome, scale: float, path: str, debug: DebugDumpOptions | None
) -> None:
    from io import BytesIO

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    # Based on: https://stackoverflow.com/a/52572919/
    # In some headless browsers, element position and width do not always reflect
    # css transforms like zoom.
    #
    # This approach works on the following assumptions:
    #   * Zoomed table width cannot always be obtained directly, but is its clientWidth * scale
    #   * Zoomed table height is obtained by the height of the div wrapping it
    #   * A sleep may be necessary before the final screen capture
    #
    # I can't say for sure whether the final sleep is needed. Only that it seems like
    # on CI with firefox sometimes the final screencapture is wider than necessary.
    original_size = driver.get_window_size()

    # set table zoom ----
    driver.execute_script(
        "var el = document.getElementsByTagName('table')[0]; "
        f"el.style.zoom = '{scale}'; "
        "el.parentNode.style.display='none'; "
        "el.parentNode.style.display='';"
    )

    if debug == "zoom":
        return _dump_debug_screenshot(driver, path)

    # get table width and height, resizing window as we go ----

    # the window can be bigger than the table, but smaller risks pushing text
    # onto new lines. this pads width and height for a little slack.
    # note that this is mostly to account for body, div padding, and table borders.
    crud_factor = 20
    outer_width, outer_height = driver.execute_script(
        "var w = window; return [w.outerWidth - w.innerWidth, w.outerHeight - w.innerHeight]"
    )
    offset_left, offset_top = driver.execute_script(
        "var div = document.body.childNodes[0]; return [div.offsetLeft, div.offsetTop];"
    )
    reported_width = driver.execute_script(
        "var el = document.getElementsByTagName('table')[0]; return el.clientWidth;"
    )
    required_width = (reported_width + offset_left * 2) * scale + crud_factor + outer_width

    # set to our required_width first, in case it changes the height of the table
    driver.set_window_size(required_width, original_size["height"])

    time.sleep(0.05)

    if debug == "width_resize":
        return _dump_debug_screenshot(driver, path)

    # height accounts for top-padding supplied by the browser (doubled to pad top and bottom)
    div_height = driver.execute_script(
        "var div = document.body.childNodes[0]; return div.scrollHeight;"
    )
    required_height = div_height + offset_top * 2 + outer_height

    # final resize window and capture image ----
    driver.set_window_size(required_width, required_height)

    if debug == "final_resize":
        return _dump_debug_screenshot(driver, path)

    el = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.TAG_NAME, "body")))

    _try_import(name="PIL", pip_install_line="pip install pillow")

    from PIL import Image

    # convert to other formats (e.g. pdf, bmp) using PIL
    Image.open(fp=BytesIO(el.screenshot_as_png)).save(fp=path)


def _dump_debug_screenshot(driver, path):
    driver.execute_script(
        "document.body.style.border = '3px solid blue'; "
        "document.body.childNodes[0].style.border = '3px solid orange'; "
        "document.getElementsByTagName('table')[0].style.border = '3px solid green'; "
    )
    driver.save_screenshot(path)


def write_raw_html(
    gt: GT,
    filename: str | Path,
    encoding: str = "utf-8",
    inline_css: bool = False,
    newline: str | None = None,
    make_page: bool = False,
    all_important: bool = False,
) -> None:
    """
    Write the table to an HTML file.

    This helper function saves the output of `GT.as_raw_html()` to an HTML file specified by the
    user.

    Parameters
    ----------
    gt
        A GT object.
    filename
        The name of the file to save the HTML. Can be a string or a `pathlib.Path` object.
    encoding
        The encoding used when writing the file. Defaults to 'utf-8'.
    inline_css
        An option to supply styles to table elements as inlined CSS styles. This is useful when
        including the table HTML as part of an HTML email message body, since inlined styles are
        largely supported in email clients over using CSS in a `<style>` block.
    newline
        The newline character to use when writing the file. Defaults to `os.linesep`.
    Returns
    -------
    None
        An HTML file is written to the specified path and the method returns `None`.
    """
    import os

    html_content = as_raw_html(
        gt, inline_css=inline_css, make_page=make_page, all_important=all_important
    )

    newline = newline if newline is not None else os.linesep

    with open(filename, "w", encoding=encoding, newline=newline) as f:
        f.write(html_content)
