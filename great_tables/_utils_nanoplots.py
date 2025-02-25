from __future__ import annotations

from typing import Any, Callable

import numpy as np

from ._tbl_data import Agnostic, is_na
from ._utils import _flatten_list, _match_arg

REFERENCE_LINE_KEYWORDS = ["mean", "median", "min", "max", "q1", "q3"]


def _is_na(x: Any) -> bool:
    return is_na(Agnostic(), x)


def _map_is_na(x: list[Any]) -> list[bool]:
    # TODO: all([]) returns True. Let's double check all places
    # in the code that call all() with this function. Do they work as intended?
    return [is_na(Agnostic(), val) for val in x]


def _val_is_numeric(x: Any) -> bool:
    """
    Determine whether a scalar value is numeric (i.e., either an integer or a float).
    """

    # If a list then signal a failure
    if isinstance(x, list):
        raise ValueError("The input cannot be a list. It must be a single value.")

    return isinstance(x, (int, float))


def _val_is_str(x: Any) -> bool:
    """
    Determine whether a scalar value is a string.
    """

    # If a list then signal a failure
    if isinstance(x, list):
        raise ValueError("The input cannot be a list. It must be a single value.")

    return isinstance(x, (str))


# This determines whether an entire list of values are integer-like; this skips
# over missing values and returns a single boolean
def _is_integerlike(val_list: list[Any]) -> bool:
    """
    Determine whether an entire list of values are integer-like; this skips
    over missing values and returns a single boolean.
    """

    # If the list is empty, return False
    if len(val_list) == 0:
        return False

    return all((isinstance(val, (int, np.integer)) or _is_na(val)) for val in val_list)


def _any_na_in_list(x: list[Any]) -> bool:
    """
    Determine whether a list of values contains any missing values.
    """

    return any(_is_na(val) for val in x)


def _check_any_na_in_list(x: list[int | float]) -> None:
    """
    Check whether a list of values contains any missing values; if so, raise an error.
    """

    if _any_na_in_list(x):
        raise ValueError("The list of values cannot contain missing values.")


# Remove missing values from a list of values
def _remove_na_from_list(x: list[int | float]) -> list[int | float]:
    """
    Remove missing values from a list of values.
    """

    return [val for val in x if not _is_na(val)]


def _normalize_option_list(option_list: Any | list[Any], num_y_vals: int) -> list[Any]:
    """
    Normalize an option list to have the same length as the number of `y` values.
    """

    # If `option_list` is a single value, then make it a list
    if not isinstance(option_list, list):
        option_list = [option_list]

    if len(option_list) != 1 and len(option_list) != num_y_vals:
        raise ValueError("Every option must have either length 1 or `length(y_vals)`.")

    if len(option_list) == 1:
        option_list = [option_list[0]] * num_y_vals

    return option_list


def calc_ref_value(val_or_calc: int | float | str, data) -> int | float | str:
    if _val_is_numeric(val_or_calc):
        return val_or_calc
    elif _val_is_str(val_or_calc) and val_or_calc in REFERENCE_LINE_KEYWORDS:
        return _generate_ref_line_from_keyword(vals=data, keyword=val_or_calc)

    raise ValueError(f"Unsupported nanoplot area value: {val_or_calc}")


def _format_number_compactly(
    val: int | float,
    currency: str | None = None,
    as_integer: bool = False,
    fn: Callable[..., str] | None = None,
) -> str:
    """
    Format a single numeric value compactly, using a currency if provided.
    """

    from great_tables.vals import fmt_currency, fmt_integer, fmt_number, fmt_scientific

    if fn is not None and isinstance(fn, Callable):
        res = fn(val)

        # Check whether the result is a single string value; if not, raise an error
        if not isinstance(res, str):
            raise ValueError("The result of the formatting function must be a single string value.")

        return res

    if _is_na(val):
        return "NA"

    if val == 0:
        return "0"

    if abs(val) < 0.01:
        use_subunits = True
        decimals = None

        n_sigfig = 2
        compact = False

    elif abs(val) < 1:
        use_subunits = True
        decimals = None

        n_sigfig = 2
        compact = False

    elif abs(val) < 100:
        use_subunits = True
        decimals = None

        n_sigfig = 3
        compact = False

    elif abs(val) < 1000:
        use_subunits = True
        decimals = None

        n_sigfig = 3
        compact = False

    elif abs(val) < 10000:
        use_subunits = False
        decimals = 2

        n_sigfig = 3
        compact = True

    elif abs(val) < 100000:
        use_subunits = False
        decimals = 1

        n_sigfig = 3
        compact = True

    elif abs(val) < 1000000:
        use_subunits = False
        decimals = 0

        n_sigfig = 3
        compact = True

    elif abs(val) < 1e15:
        use_subunits = False
        decimals = 1

        n_sigfig = 3
        compact = True

    else:
        use_subunits = False
        decimals = None
        n_sigfig = 2
        compact = False

    # Format value accordingly

    if currency is not None:
        if abs(val) >= 1e15:
            val_formatted = fmt_currency(
                1e15,
                currency=currency,
                use_subunits=False,
                decimals=0,
                # compact=True,
            )

            val_formatted = f">{val_formatted}"

        else:
            val_formatted = fmt_currency(
                val,
                currency=currency,
                use_subunits=use_subunits,
                decimals=decimals,
                # compact=compact,
            )

    else:
        if abs(val) < 0.01 or abs(val) >= 1e15:
            val_formatted = fmt_scientific(
                val,
                exp_style="E",
                n_sigfig=n_sigfig,
                decimals=1,
            )

        else:
            if as_integer and val > -100 and val < 100:
                val_formatted = fmt_integer(val)

            else:
                val_formatted = fmt_number(
                    val,
                    n_sigfig=n_sigfig,
                    decimals=1,
                    compact=compact,
                )

    return val_formatted[0]


#
# Collection of general functions to calculate the mean, min, max, median,
# and other statistical measures from a list of values; the list should not
# be expected to contain any missing values so we won't guard against them here
#


def _gt_mean(x: list[int | float]) -> float:
    """
    Calculate the mean of a list of values.
    """

    return sum(x) / len(x)


def _gt_min(x: list[int | float]) -> int | float:
    """
    Calculate the minimum value from a list of values.
    """
    return min(x)


def _gt_max(x: list[int | float]) -> int | float:
    """
    Calculate the maximum value from a list of values.
    """
    return max(x)


def _gt_median(x: list[int | float]) -> int | float:
    """
    Calculate the median of a list of values.
    """
    x.sort()
    n = len(x)
    if n % 2 == 0:
        return (x[n // 2 - 1] + x[n // 2]) / 2
    else:
        return x[n // 2]


def _gt_first(x: list[int | float]) -> int | float:
    """
    Get the first value from a list of values.
    """
    return x[0]


def _gt_last(x: list[int | float]) -> int | float:
    """
    Get the last value from a list of values.
    """
    return x[-1]


def _gt_quantile(x: list[int | float], q: float) -> int | float:
    """
    Calculate the quantile of a list of values.
    """
    x.sort()
    n = len(x)
    return x[int(n * q)]


def _gt_q1(x: list[int | float]) -> float:
    """
    Calculate the first quartile of a list of values.
    """
    return _gt_quantile(x, 0.25)


def _gt_q3(x: list[int | float]) -> float:
    """
    Calculate the third quartile of a list of values.
    """
    return _gt_quantile(x, 0.75)


def _get_extreme_value(
    *args: int | float,
    stat: str = "max",
) -> int | float:
    """
    Get either the maximum or minimum value from a list of numeric values.
    """

    # Ensure that `stat` is either 'max' or 'min'
    _match_arg(stat, lst=["max", "min"])

    # Remove any None values from the `args` list
    args = [val for val in args if val is not None]

    # Flatten the `args` list which may contain lists and scalar values
    val_list = _flatten_list(args)

    # Remove missing values from the `val_list`
    val_list = _remove_na_from_list(val_list)

    # Remove None values from the `val_list`
    val_list = [val for val in val_list if val is not None]

    if stat == "max":
        extreme_val = max(val_list)
    else:
        extreme_val = min(val_list)

    return extreme_val


def _generate_ref_line_from_keyword(vals: list[int | float], keyword: str) -> int | float:
    """
    Generate a value for a reference line from a valid keyword.
    """

    _match_arg(
        x=keyword,
        lst=REFERENCE_LINE_KEYWORDS,
    )

    _check_any_na_in_list(vals)

    # Remove missing values from the `vals` list
    vals = [val for val in vals if not _is_na(val)]

    if keyword == "mean":
        ref_line = _gt_mean(vals)
    elif keyword == "median":
        ref_line = _gt_median(vals)
    elif keyword == "min":
        ref_line = _gt_min(vals)
    elif keyword == "max":
        ref_line = _gt_max(vals)
    elif keyword == "first":
        ref_line = _gt_first(vals)
    elif keyword == "last":
        ref_line = _gt_last(vals)
    elif keyword == "q1":
        ref_line = _gt_q1(vals)
    else:
        ref_line = _gt_q3(vals)

    return ref_line


def _normalize_vals(x: list[int] | list[float] | list[int | float]) -> list[int | float]:
    """
    Normalize a list of numeric values to be between 0 and 1. Account for missing values.
    """

    x_missing = [i for i, val in enumerate(x) if _is_na(val)]
    mean_x = np.mean([val for val in x if not _is_na(val)])
    x = [mean_x if _is_na(val) else val for val in x]
    x = np.array(x)
    min_attr = np.min(x, axis=0)
    max_attr = np.max(x, axis=0)
    x = x - min_attr
    x = x / (max_attr - min_attr)
    x = x.tolist()
    x = [np.nan if i in x_missing else val for i, val in enumerate(x)]
    return x


# TODO: example nanoplot showing when jitter vals might be applied
# Looks like it's on the x-axis:
# GT(pd.DataFrame({'x': [{"x": [1, 1, 1], "y": [2, 3, 4]}]})).fmt_nanoplot("x")
def _jitter_vals(x: list[int | float], amount: float) -> list[int | float]:
    """
    Jitter a list of numeric values by a small amount.
    """

    return [val + np.random.uniform(-amount, amount) for val in x]


def _normalize_to_dict(**kwargs: list[int | float]) -> dict[str, list[int | float]]:
    """
    Normalize a collection of numeric values to be between 0 and 1. Account for missing values.
    This only accepts values (scalar or list) associated with keyword arguments. A dictionary
    is returned with the same keys but the values are normalized lists. This is done so that
    any disparate collection of normalized values are distinguishable by their original keys.
    """

    # Ensure that at least two values are provided
    if len(kwargs) < 2:
        raise ValueError("At least two values must be provided.")

    # Get args as a dictionary
    args = dict(kwargs)

    # Extract the values from the dictionary as a list
    all_vals = list(args.values())
    all_keys = list(args.keys())

    # Remove any None values from the `all_vals` list
    all_vals = [val for val in all_vals if val is not None]

    # Get the length of each arg in the args dictionary (if single value, length is 1; if
    # a list, length is the length of the list)
    arg_lens = [len(val) if type(val) is list else 1 for val in all_vals]

    # Flatten the `all_vals` list which may contain lists and scalar values
    all_vals = _flatten_list(all_vals)

    # If all values are the same, then jitter the values
    if len(set(all_vals)) == 1:
        all_vals = _jitter_vals(all_vals, 0.1)

    # Get the normalized values across the collection of all values
    normalized_vals = _normalize_vals(all_vals)

    # Use the `arg_lens` list to put the sequence of normalized values back into
    # the original structure of args; do this with iteration
    for i in range(len(arg_lens)):
        normalized_vals_i = normalized_vals[0 : arg_lens[i]]

        # Assign these values back to the original args dictionary at the ith key
        args[all_keys[i]] = normalized_vals_i

        # Remove the first n elements from `normalized_vals` and assign the result
        normalized_vals = normalized_vals[arg_lens[i] :]

    return args


def _construct_nanoplot_svg(
    viewbox: str,
    svg_height: str,
    svg_defs: str,
    svg_style: str,
    show_data_points: bool,
    show_data_line: bool,
    show_data_area: bool,
    show_reference_line: bool,
    show_reference_area: bool,
    show_vertical_guides: bool,
    show_y_axis_guide: bool,
    ref_area_tags: str | None = None,
    area_path_tags: str | None = None,
    data_path_tags: str | None = None,
    zero_line_tags: str | None = None,
    bar_tags: str | None = None,
    ref_line_tags: str | None = None,
    circle_tags: str | None = None,
    g_y_axis_tags: str | None = None,
    g_guide_tags: str | None = None,
) -> str:
    """
    Construct an SVG nanoplot from a collection of SVG tags.
    """

    # For the optional strings, transform None to an empty string
    ref_area_tags = "" if ref_area_tags is None or show_reference_area is False else ref_area_tags
    area_path_tags = "" if area_path_tags is None or show_data_area is False else area_path_tags
    data_path_tags = "" if data_path_tags is None or show_data_line is False else data_path_tags
    zero_line_tags = "" if zero_line_tags is None else zero_line_tags
    bar_tags = "" if bar_tags is None else bar_tags
    ref_line_tags = "" if ref_line_tags is None or show_reference_line is False else ref_line_tags
    circle_tags = "" if circle_tags is None or show_data_points is False else circle_tags
    g_y_axis_tags = "" if g_y_axis_tags is None or show_y_axis_guide is False else g_y_axis_tags
    g_guide_tags = "" if g_guide_tags is None or show_vertical_guides is False else g_guide_tags

    return f'<div><svg role="img" viewBox="{viewbox}" style="height: {svg_height}; margin-left: auto; margin-right: auto; font-size: inherit; overflow: visible; vertical-align: middle; position:relative;">{svg_defs}{svg_style}{ref_area_tags}{area_path_tags}{data_path_tags}{zero_line_tags}{bar_tags}{ref_line_tags}{circle_tags}{g_y_axis_tags}{g_guide_tags}</svg></div>'


def _generate_nanoplot(
    y_vals: list[int] | list[float] | list[int | float],
    y_ref_line: str | None = None,
    y_ref_area: str | None = None,
    x_vals: list[int | float] | None = None,
    expand_x: list[int] | list[float] | list[int | float] | None = None,
    expand_y: list[int] | list[float] | list[int | float] | None = None,
    missing_vals: str = "marker",
    all_y_vals: list[int] | list[float] | list[int | float] | None = None,
    all_single_y_vals: list[int] | list[float] | list[int | float] | None = None,
    plot_type: str = "line",
    data_line_type: str = "curved",
    currency: str | None = None,
    y_val_fmt_fn: Callable[..., str] | None = None,
    y_axis_fmt_fn: Callable[..., str] | None = None,
    y_ref_line_fmt_fn: Callable[..., str] | None = None,
    data_point_radius: int | list[int] = 10,
    data_point_stroke_color: str | list[str] = "#FFFFFF",
    data_point_stroke_width: int | list[int] = 4,
    data_point_fill_color: str | list[str] = "#FF0000",
    data_line_stroke_color: str = "#4682B4",
    data_line_stroke_width: int = 8,
    data_area_fill_color: str = "#FF0000",
    data_bar_stroke_color: str | list[str] = "#3290CC",
    data_bar_stroke_width: int | list[int] = 4,
    data_bar_fill_color: str | list[str] = "#3FB5FF",
    data_bar_negative_stroke_color: str = "#CC3243",
    data_bar_negative_stroke_width: int = 4,
    data_bar_negative_fill_color: str = "#D75A68",
    reference_line_color: str = "#75A8B0",
    reference_area_fill_color: str = "#A6E6F2",
    vertical_guide_stroke_color: str = "#911EB4",
    vertical_guide_stroke_width: int = 12,
    show_data_points: bool = True,
    show_data_line: bool = True,
    show_data_area: bool = True,
    show_reference_line: bool = True,
    show_reference_area: bool = True,
    show_vertical_guides: bool = True,
    show_y_axis_guide: bool = True,
    interactive_data_values: bool = True,
    svg_height: str = "2em",
) -> str:
    """
    Generate a nanoplot SVG from a collection of parameters.
    """

    # Ensure that arguments are matched
    _match_arg(
        x=missing_vals,
        lst=["marker", "gap", "zero", "remove"],
    )
    _match_arg(
        x=data_line_type,
        lst=["curved", "straight"],
    )

    #
    # Determine where a zero line is considered and provide the stroke color and width
    #

    zero_line_considered = True if plot_type in ["bar", "boxplot"] else False

    zero_line_stroke_color = "#BFBFBF"
    zero_line_stroke_width = 4

    # Initialize several local `*_tags` variables with `None`
    ref_area_tags = None
    area_path_tags = None
    data_path_tags = None
    zero_line_tags = None
    bar_tags = None
    boxplot_tags = None
    ref_line_tags = None
    circle_tags = None
    g_y_axis_tags = None
    g_guide_tags = None

    # Initialize the `single_horizontal_plot` variable with `False`
    single_horizontal_plot = False

    # If the number of `y` values in a list is zero or if all consist of NA values,
    # return an empty string
    if isinstance(y_vals, list) and len(y_vals) == 0:
        return ""

    # If all `y` values are NA, return an empty string
    # TODO: all([]) evaluates to True. In that case does this produce the intended behavior?
    if isinstance(y_vals, list) and all(_map_is_na(y_vals)):
        return ""

    # Get the number of data points for `y`
    if type(y_vals) is list:
        num_y_vals = len(y_vals)
    else:
        num_y_vals = 1

    # Handle case where `x_vals` exists (i.e., is not `NULL`)
    if x_vals is not None:
        # If the number of `x` values is zero or an empty string,
        # return an empty string
        if len(x_vals) == 0:
            return ""
        if all(_map_is_na(x_vals)):
            return ""

        # Get the number of data points for `x`
        num_x_vals = len(x_vals)

        # Ensure that, if there are `x` values, the number of `x`
        # and `y` values matches
        if num_x_vals != num_y_vals:
            raise ValueError(
                f"""The number of `x` and `y` values must match.
                The `x` value length is: {num_x_vals}
                The `y` value length is: {num_y_vals}
                """
            )

        # Handle missing values in `x_vals` through removal (i.e., missing
        # values in `x_vals` means removal of positional values from both
        # `x_vals` and `y_vals`)
        if any(_map_is_na(x_vals)):
            # TODO: this code did not have test coverage and likely didn't
            # work. It should work now, but we need to test it.

            # Determine which values from `x_vals` are non-missing values
            x_vals_non_missing = [~_is_na(val) for val in x_vals]

            # Retain only `x_vals_non_missing` from `x_vals` and `y_vals`
            x_vals = [x for x, keep in zip(x_vals, x_vals_non_missing) if keep]
            y_vals = [y for y, keep in zip(y_vals, x_vals_non_missing) if keep]

        # If `x` values are present, we cannot use a curved line so
        # we'll force the use of the 'straight' line type
        # TODO: if someone specifies the options curved, and we can't do it
        # then we should raise an error.
        data_line_type = "straight"

    # If `missing_vals` is set to 'gap' raise an error
    # TODO: Implement the 'gap' option for missing values
    if missing_vals == "gap":
        raise NotImplementedError("The 'gap' option for missing values is not yet implemented.")

    # For the `missing_vals` options of 'zero' or 'remove', either replace NAs
    # with `0` or remove NAs entirely
    if missing_vals == "zero":
        y_vals = y_vals.fillna(0)

    # If `missing_vals` is 'remove', remove NAs from `y_vals`
    if missing_vals == "remove":
        y_vals = y_vals.dropna()

        if x_vals is not None:
            # Remove the corresponding `x` values for the removed `y` values
            x_vals = x_vals[y_vals.index]

    # Get the number of data points for `y`
    if isinstance(y_vals, list):
        num_y_vals = len(y_vals)
    else:
        num_y_vals = 1

    # If `y_vals` is a scalar value we requested a 'line' or 'bar' plot, then
    # reset several parameters
    if isinstance(y_vals, (int, float)) and plot_type in ["line", "bar"]:
        single_horizontal_plot = True
        show_data_points = True
        show_data_line = True
        show_data_area = False
        show_reference_line = False
        show_reference_area = False
        show_vertical_guides = False
        show_y_axis_guide = False

        y_vals = [y_vals]

    # If this is a box plot, set several parameters
    if plot_type == "boxplot":
        show_data_points = False
        show_data_line = False
        show_data_area = False
        show_reference_line = False
        show_reference_area = False
        show_vertical_guides = False
        show_y_axis_guide = False

    # Find out whether the collection of non-NA `y` values are all integer-like
    y_vals_integerlike = _is_integerlike(val_list=y_vals)

    # Get the max and min of the `y` scale from the `y` data values
    y_scale_max = _get_extreme_value(y_vals, stat="max")
    y_scale_min = _get_extreme_value(y_vals, stat="min")

    # Handle cases where collection of `y_vals` is invariant
    if y_scale_min == y_scale_max and expand_y is None:
        if y_scale_min == 0:
            expand_y_dist = 5
        else:
            expand_y_dist = (y_scale_min / 10) * 2

        # Expand the `y` scale, centering around the `y_scale_min` value
        expand_y = [y_scale_min - expand_y_dist, y_scale_min + expand_y_dist]

    # Ensure that a reference line or reference area isn't shown if None or
    # any of its directives is missing
    if _is_na(y_ref_line):
        show_reference_line = False

    if y_ref_area is None:
        show_reference_area = False
    elif _is_na(y_ref_area[0]) or _is_na(y_ref_area[1]):
        show_reference_area = False

    # Determine the width of the data plot area; for plots where `x_vals`
    # are available, we'll use a fixed width of `500` (px), and for plots
    # where `x_vals` aren't present, we'll adjust the final width based
    # on the fixed interval between data points (this is dependent on the
    # number of data points)
    if x_vals is not None or single_horizontal_plot or plot_type == "boxplot":
        data_x_width = 600
        # TODO: what should x_d be in this case?
    else:
        # Obtain a sensible, fixed interval between data points in px
        if num_y_vals <= 20:
            x_d = 50
        elif num_y_vals <= 30:
            x_d = 40
        elif num_y_vals <= 40:
            x_d = 30
        elif num_y_vals <= 50:
            x_d = 25
        else:
            x_d = 20

        data_x_width = num_y_vals * x_d

    # Define the top-left of the plot area
    left_x = 0
    top_y = 0

    # Define the safe zone distance from top/bottom and left/right edges
    safe_y_d = 15
    safe_x_d = 50

    # Define the height of the plot area that bounds the data points
    data_y_height = 100

    # Determine the bottom-right of the plot area based on the quantity of data
    bottom_y = safe_y_d + data_y_height + safe_y_d
    right_x = safe_x_d + data_x_width + safe_x_d

    viewbox = f"{left_x} {top_y} {right_x} {bottom_y}"

    #
    # If there is a reference line and/or reference area, the values for these
    # need to be generated and integrated in the `normalize_y_vals()` operation
    # so that there are normalized values in relation to the data points
    #

    if show_reference_line and show_reference_area:
        # Case where there is both a reference line and a reference area

        #
        # Resolve the reference line
        #

        if (
            y_ref_line is not None
            and _val_is_str(y_ref_line)
            and y_ref_line in REFERENCE_LINE_KEYWORDS
        ):
            y_ref_line = _generate_ref_line_from_keyword(vals=y_vals, keyword=y_ref_line)

        #
        # Resolve the reference area
        #

        # Note if y_ref_area were None, we would not be in this clause
        y_ref_area_line_1 = calc_ref_value(y_ref_area[0], y_vals)
        y_ref_area_line_2 = calc_ref_value(y_ref_area[1], y_vals)

        y_ref_area_lines_sorted = sorted([y_ref_area_line_1, y_ref_area_line_2])
        y_ref_area_l = y_ref_area_lines_sorted[0]
        y_ref_area_u = y_ref_area_lines_sorted[1]

        _all_y_data = [y_vals, y_ref_line, y_ref_area_l, y_ref_area_u, expand_y]

        # Recompute the `y` scale min and max values
        y_scale_max = _get_extreme_value(*_all_y_data, stat="max")
        y_scale_min = _get_extreme_value(*_all_y_data, stat="min")

        # Scale to proportional values
        y_proportions_list = _normalize_to_dict(
            vals=y_vals,
            ref_line=y_ref_line,
            ref_area_l=y_ref_area_l,
            ref_area_u=y_ref_area_u,
            zero=0 if zero_line_considered else None,
            expand_y=expand_y,
        )

        y_proportions = y_proportions_list["vals"]
        y_proportion_ref_line = y_proportions_list["ref_line"][0]
        y_proportions_ref_area_l = y_proportions_list["ref_area_l"][0]
        y_proportions_ref_area_u = y_proportions_list["ref_area_u"][0]

        # Scale reference line and reference area boundaries
        data_y_ref_line = safe_y_d + ((1 - y_proportion_ref_line) * data_y_height)
        data_y_ref_area_l = safe_y_d + ((1 - y_proportions_ref_area_l) * data_y_height)
        data_y_ref_area_u = safe_y_d + ((1 - y_proportions_ref_area_u) * data_y_height)

    elif show_reference_line:
        # Case where there is a reference line

        if (
            y_ref_line is not None
            and _val_is_str(y_ref_line)
            and y_ref_line in REFERENCE_LINE_KEYWORDS
        ):
            y_ref_line = _generate_ref_line_from_keyword(vals=y_vals, keyword=y_ref_line)

        # Recompute the `y` scale min and max values
        args = [y_vals, y_ref_line, expand_y] + ([0] if zero_line_considered else [])
        y_scale_max = _get_extreme_value(*args, stat="max")
        y_scale_min = _get_extreme_value(*args, stat="min")

        # Scale to proportional values
        y_proportions_list = _normalize_to_dict(
            vals=y_vals,
            ref_line=y_ref_line,
            zero=0 if zero_line_considered else None,
            expand_y=expand_y,
        )

        y_proportions = y_proportions_list["vals"]
        y_proportion_ref_line = y_proportions_list["ref_line"][0]

        # Scale reference line
        data_y_ref_line = safe_y_d + ((1 - y_proportion_ref_line) * data_y_height)

    elif show_reference_area:
        # Case where there is a reference area

        # Note if y_ref_area were None, we would not be in this clause
        y_ref_area_line_1 = calc_ref_value(y_ref_area[0], y_vals)
        y_ref_area_line_2 = calc_ref_value(y_ref_area[1], y_vals)

        y_ref_area_lines_sorted = sorted([y_ref_area_line_1, y_ref_area_line_2])
        y_ref_area_l = y_ref_area_lines_sorted[0]
        y_ref_area_u = y_ref_area_lines_sorted[1]

        # Recompute the `y` scale min and max values

        # Recompute the `y` scale min and max values
        _all_y_data = [y_vals, y_ref_area_l, y_ref_area_u, expand_y] + (
            [0] if zero_line_considered else []
        )
        y_scale_max = _get_extreme_value(*_all_y_data, stat="max")
        y_scale_min = _get_extreme_value(*_all_y_data, stat="min")

        y_proportions_list = _normalize_to_dict(
            vals=y_vals,
            ref_area_l=y_ref_area_l,
            ref_area_u=y_ref_area_u,
            zero=0 if zero_line_considered else None,
            expand_y=expand_y,
        )

        y_proportions = y_proportions_list["vals"]
        y_proportions_ref_area_l = y_proportions_list["ref_area_l"][0]
        y_proportions_ref_area_u = y_proportions_list["ref_area_u"][0]

        # Scale reference area boundaries
        data_y_ref_area_l = safe_y_d + ((1 - y_proportions_ref_area_l) * data_y_height)
        data_y_ref_area_u = safe_y_d + ((1 - y_proportions_ref_area_u) * data_y_height)

    else:
        # Case where there is no reference line or reference area

        # Recompute the `y` scale min and max values
        args = [y_vals, expand_y] + ([0] if zero_line_considered else [])
        y_scale_max = _get_extreme_value(*args, stat="max")
        y_scale_min = _get_extreme_value(*args, stat="min")

        y_proportions_list = _normalize_to_dict(
            vals=y_vals,
            zero=0 if zero_line_considered else None,
            expand_y=expand_y,
        )

        y_proportions = y_proportions_list["vals"]

    # Calculate the `data_y0_point` value for zero-line-inclusive plots
    if zero_line_considered:
        y_proportions_zero = y_proportions_list["zero"][0]
        data_y0_point = safe_y_d + ((1 - y_proportions_zero) * data_y_height)

    # If x values are present then normalize them between [0, 1]; if
    # there are no x values, generate equally-spaced x values according
    # to the number of y values
    if plot_type == "line" and x_vals is not None:
        if isinstance(expand_x, str) or (
            isinstance(expand_x, list) and any(isinstance(item, str) for item in expand_x)
        ):
            # TODO: the line below lacked tests, and called non-existent methods.
            # replace with something that doesn't use pandas and returns the correct thing.

            # Assume that string values are dates and convert them to timestamps
            # expand_x = pd.to_datetime(expand_x, utc=True).timestamp()
            raise NotImplementedError("Currently, passing expand_x as a string is unsupported.")

        # Scale to proportional values
        x_proportions_list = _normalize_to_dict(vals=x_vals, expand_x=expand_x)

        x_proportions = x_proportions_list["vals"]

    else:
        x_proportions = np.linspace(0, 1, num_y_vals)

    #
    # Create normalized (and inverted for SVG) data `x` and `y` values for the
    # plot area; these are named `data_x_points` and `data_y_points`
    #

    for i in range(len(y_proportions)):
        y_proportions[i] = safe_y_d + ((1 - y_proportions[i]) * data_y_height)

    for i in range(len(x_proportions)):
        x_proportions[i] = (data_x_width * x_proportions[i]) + safe_x_d

    data_y_points = y_proportions
    data_x_points = x_proportions

    #
    # Ensure that certain options have their lengths checked and
    # expanded to length `num_y_vals`
    #

    data_point_radius = _normalize_option_list(option_list=data_point_radius, num_y_vals=num_y_vals)
    data_point_stroke_color = _normalize_option_list(
        option_list=data_point_stroke_color, num_y_vals=num_y_vals
    )
    data_point_stroke_width = _normalize_option_list(
        option_list=data_point_stroke_width, num_y_vals=num_y_vals
    )
    data_point_fill_color = _normalize_option_list(
        option_list=data_point_fill_color, num_y_vals=num_y_vals
    )
    data_bar_stroke_color = _normalize_option_list(
        option_list=data_bar_stroke_color, num_y_vals=num_y_vals
    )
    data_bar_stroke_width = _normalize_option_list(
        option_list=data_bar_stroke_width, num_y_vals=num_y_vals
    )
    data_bar_fill_color = _normalize_option_list(
        option_list=data_bar_fill_color, num_y_vals=num_y_vals
    )

    #
    # Generate data segments by defining `start` and `end` vectors (these
    # are guaranteed to be of the same length); these the segments of data
    # they receive line segments and adjoining areas
    #

    # Use run-length encoding to determine the segments of data

    # rle_data_y_points = pd.Series(data_y_points).diff().ne(0).cumsum()

    # end_data_y_points = np.cumsum(rle_data_y_points.lengths)

    # start_data_y_points = end_data_y_points - rle_data_y_points.lengths + 1

    start_data_y_points = [0]
    end_data_y_points = [len(data_y_points)]
    n_segments = 1

    #
    # Generate a curved data line
    #

    if plot_type == "line" and show_data_line and data_line_type == "curved":
        data_path_tags = []

        for i in range(n_segments):
            curve_x = data_x_points[start_data_y_points[i] : end_data_y_points[i]]
            curve_y = data_y_points[start_data_y_points[i] : end_data_y_points[i]]

            curved_path_string = [f"M {curve_x[0]},{curve_y[0]}"]

            for j in range(1, len(curve_x)):
                point_b1 = f"{curve_x[j - 1] + x_d / 2},{curve_y[j - 1]}"
                point_b2 = f"{curve_x[j] - x_d / 2},{curve_y[j]}"
                point_i = f"{curve_x[j]},{curve_y[j]}"

                path_string_j = f"C {point_b1} {point_b2} {point_i}"

                curved_path_string.append(path_string_j)

            curved_path_string_i = " ".join(curved_path_string)

            data_path_tags_i = f'<path d="{curved_path_string_i}" stroke="{data_line_stroke_color}" stroke-width="{data_line_stroke_width}" fill="none"></path>'

            data_path_tags.append(data_path_tags_i)

        data_path_tags = "\n".join(data_path_tags)

    if plot_type == "line" and show_data_line and data_line_type == "straight":
        data_path_tags = []

        for i in range(n_segments):
            line_x = data_x_points[start_data_y_points[i] : end_data_y_points[i]]
            line_y = data_y_points[start_data_y_points[i] : end_data_y_points[i]]

            line_xy = " ".join([f"{x},{y}" for x, y in zip(line_x, line_y)])

            data_path_tags_i = f'<polyline points="{line_xy}" stroke="{data_line_stroke_color}" stroke-width="{data_line_stroke_width}" fill="none"></polyline>'

            data_path_tags.append(data_path_tags_i)

        data_path_tags = "".join(data_path_tags)

    #
    # Generate data points
    #

    if plot_type == "line" and show_data_points:
        circle_strings = []

        for i, _ in enumerate(data_x_points):
            data_point_radius_i = data_point_radius[i]
            data_point_stroke_color_i = data_point_stroke_color[i]
            data_point_stroke_width_i = data_point_stroke_width[i]
            data_point_fill_color_i = data_point_fill_color[i]

            if data_y_points[i] is None:
                if missing_vals == "marker":
                    # Create a symbol that should denote that a missing value is present
                    circle_strings_i = f'<circle cx="{data_x_points[i]}" cy="{safe_y_d + (data_y_height / 2)}" r="{data_point_radius_i + (data_point_radius_i / 2)}" stroke="red" stroke-width="{data_point_stroke_width_i}" fill="white"></circle>'

                else:
                    continue

            else:
                circle_strings_i = f'<circle cx="{data_x_points[i]}" cy="{data_y_points[i]}" r="{data_point_radius_i}" stroke="{data_point_stroke_color_i}" stroke-width="{data_point_stroke_width_i}" fill="{data_point_fill_color_i}"></circle>'

            circle_strings.append(circle_strings_i)

        circle_tags = "".join(circle_strings)

    #
    # Generate data bars
    #

    if plot_type == "bar" and single_horizontal_plot is False:
        bar_strings = []

        for i, _ in enumerate(data_x_points):
            data_point_radius_i = data_point_radius[i]
            data_bar_stroke_color_i = data_bar_stroke_color[i]
            data_bar_stroke_width_i = data_bar_stroke_width[i]
            data_bar_fill_color_i = data_bar_fill_color[i]

            if data_y_points[i] is None:
                if missing_vals == "marker":
                    # Create a symbol that should denote that a missing value is present
                    bar_strings_i = f'<circle cx="{data_x_points[i]}" cy="{safe_y_d + (data_y_height / 2)}" r="{data_point_radius_i + (data_point_radius_i / 2)}" stroke="red" stroke-width="{data_bar_stroke_width_i}" fill="transparent"></circle>'

                else:
                    continue

            else:
                if y_vals[i] < 0:
                    y_value_i = data_y0_point
                    y_height = data_y_points[i] - data_y0_point
                    data_bar_stroke_color_i = data_bar_negative_stroke_color
                    data_bar_stroke_width_i = data_bar_negative_stroke_width
                    data_bar_fill_color_i = data_bar_negative_fill_color

                elif y_vals[i] > 0:
                    y_value_i = data_y_points[i]
                    y_height = data_y0_point - data_y_points[i]

                elif y_vals[i] == 0:
                    y_value_i = data_y0_point - 1
                    y_height = 2
                    data_bar_stroke_color_i = "#808080"
                    data_bar_stroke_width_i = 4
                    data_bar_fill_color_i = "#808080"

                bar_strings_i = f'<rect x="{data_x_points[i] - (x_d - 10) / 2}" y="{y_value_i}" width="{x_d - 10}" height="{y_height}" stroke="{data_bar_stroke_color_i}" stroke-width="{data_bar_stroke_width_i}" fill="{data_bar_fill_color_i}"></rect>'

            bar_strings.append(bar_strings_i)

        bar_tags = "".join(bar_strings)

    #
    # Generate single horizontal data bars
    #

    if plot_type == "bar" and single_horizontal_plot:
        # This type of display assumes there is only a single `y` value and there
        # are possibly several such horizontal bars across different rows that
        # need to be on a common scale

        bar_thickness = data_point_radius[0] * 4

        if all(val == 0 for val in all_single_y_vals):
            # Handle case where all values across rows are `0`

            y_proportion = 0.5
            y_proportion_zero = 0.5

        else:
            # Scale to proportional values
            y_proportions_list = _normalize_to_dict(val=y_vals, all_vals=all_single_y_vals, zero=0)

            y_proportion = y_proportions_list["val"][0]
            y_proportion_zero = y_proportions_list["zero"][0]

        y0_width = y_proportion_zero * data_x_width
        y_width = y_proportion * data_x_width

        if y_vals[0] < 0:
            data_bar_stroke_color = data_bar_negative_stroke_color
            data_bar_stroke_width = data_bar_negative_stroke_width
            data_bar_fill_color = data_bar_negative_fill_color

            rect_x = y_width
            rect_width = y0_width - y_width

        elif y_vals[0] > 0:
            data_bar_stroke_color = data_bar_stroke_color[0]
            data_bar_stroke_width = data_bar_stroke_width[0]
            data_bar_fill_color = data_bar_fill_color[0]

            rect_x = y0_width
            rect_width = y_width - y0_width

        elif y_vals[0] == 0:
            data_bar_stroke_color = "#808080"
            data_bar_stroke_width = 4
            data_bar_fill_color = "#808080"

            rect_x = y0_width - 2.5
            rect_width = 5

        # Format number compactly
        y_value = _format_number_compactly(
            val=y_vals[0], currency=currency, as_integer=y_vals_integerlike, fn=y_val_fmt_fn
        )

        rect_strings = f'<rect x="0" y="{bottom_y / 2 - bar_thickness / 2}" width="600" height="{bar_thickness}" stroke="transparent" stroke-width="{vertical_guide_stroke_width}" fill="transparent"></rect>'

        if y_vals[0] > 0:
            text_strings = f'<text x="{y0_width + 10}" y="{safe_y_d + 10}" fill="transparent" stroke="transparent" font-size="30px">{y_value}</text>'

        elif y_vals[0] < 0:
            text_strings = f'<text x="{y0_width - 10}" y="{safe_y_d + 10}" fill="transparent" stroke="transparent" font-size="30px" text-anchor="end">{y_value}</text>'

        elif y_vals[0] == 0:
            if all(val == 0 for val in all_single_y_vals):
                text_anchor = "start"
                x_position_text = y0_width + 10

            elif all(val < 0 for val in all_single_y_vals):
                text_anchor = "end"
                x_position_text = y0_width - 10

            else:
                text_anchor = "start"
                x_position_text = y0_width + 10

            text_strings = f'<text x="{x_position_text}" y="{bottom_y / 2 + 10}" fill="transparent" stroke="transparent" font-size="30px" text-anchor="{text_anchor}">{y_value}</text>'

        g_guide_tags = f'<g class="horizontal-line">{rect_strings}{text_strings}</g>'

        bar_tags = f'<rect x="{rect_x}" y="{bottom_y / 2 - bar_thickness / 2}" width="{rect_width}" height="{bar_thickness}" stroke="{data_bar_stroke_color}" stroke-width="{data_bar_stroke_width}" fill="{data_bar_fill_color}"></rect>{g_guide_tags}'

        zero_line_tags = f'<line x1="{y0_width}" y1="{(bottom_y / 2) - (bar_thickness * 1.5)}" x2="{y0_width}" y2="{(bottom_y / 2) + (bar_thickness * 1.5)}" stroke="{zero_line_stroke_color}" stroke-width="{zero_line_stroke_width}"></line>'

        # Redefine the `viewbox` in terms of the `data_x_width` value; this ensures
        # that the horizontal bars are centered about their extreme values
        viewbox = f"{left_x} {top_y} {data_x_width} {bottom_y}"

    #
    # Generate single horizontal data lines
    #

    # TODO: Make this a line with a single point
    if plot_type == "line" and single_horizontal_plot:
        # This type of display assumes there is only a single `y` value and there
        # are possibly several such horizontal bars across different rows that
        # need to be on a common scale

        data_point_radius_i = data_point_radius[0]
        data_point_stroke_color_i = data_point_stroke_color[0]
        data_point_stroke_width_i = data_point_stroke_width[0]
        data_point_fill_color_i = data_point_fill_color[0]

        bar_thickness = data_point_radius[0] * 4

        if all(val == 0 for val in all_single_y_vals):
            # Handle case where all values across rows are `0`

            y_proportion = 0.5
            y_proportion_zero = 0.5

        else:
            # Scale to proportional values
            y_proportions_list = _normalize_to_dict(val=y_vals, all_vals=all_single_y_vals, zero=0)

            y_proportion = y_proportions_list["val"][0]
            y_proportion_zero = y_proportions_list["zero"][0]

        y0_width = y_proportion_zero * data_x_width
        y_width = y_proportion * data_x_width

        if y_vals[0] < 0:
            x1_val = y_width
            x2_val = y0_width

            circle_x_val = x1_val

        elif y_vals[0] > 0:
            x1_val = y0_width
            x2_val = y_width

            circle_x_val = x2_val

        elif y_vals[0] == 0:
            x1_val = y_width
            x2_val = y0_width

            circle_x_val = x2_val

        # Format number compactly
        y_value = _format_number_compactly(
            val=y_vals[0], currency=currency, as_integer=y_vals_integerlike, fn=y_val_fmt_fn
        )

        rect_strings = f'<rect x="0" y="{bottom_y / 2 - bar_thickness / 2}" width="600" height="{bar_thickness}" stroke="transparent" stroke-width="{vertical_guide_stroke_width}" fill="transparent"></rect>'

        if y_vals[0] > 0:
            text_strings = f'<text x="{y0_width + 10}" y="{safe_y_d + 10}" fill="transparent" stroke="transparent" font-size="30px">{y_value}</text>'

        elif y_vals[0] < 0:
            text_strings = f'<text x="{y0_width - 10}" y="{safe_y_d + 10}" fill="transparent" stroke="transparent" font-size="30px" text-anchor="end">{y_value}</text>'

        elif y_vals[0] == 0:
            if all(val == 0 for val in all_single_y_vals):
                text_anchor = "start"
                x_position_text = y0_width + 10

            elif all(val < 0 for val in all_single_y_vals):
                text_anchor = "end"
                x_position_text = y0_width - 10

            else:
                text_anchor = "start"
                x_position_text = y0_width + 15

            text_strings = f'<text x="{x_position_text}" y="{bottom_y / 2 + 10}" fill="transparent" stroke="transparent" font-size="30px" text-anchor="{text_anchor}">{y_value}</text>'

        g_guide_tags = f'<g class="horizontal-line">{rect_strings}{text_strings}</g>'

        data_path_tags = f'<line x1="{x1_val}" y1="{bottom_y / 2}" x2="{x2_val}" y2="{bottom_y / 2}" stroke="{data_line_stroke_color}" stroke-width="{data_line_stroke_width}"></line>{g_guide_tags}'

        circle_tags = f'<circle cx="{circle_x_val}" cy="{bottom_y / 2}" r="{data_point_radius_i}" stroke="{data_point_stroke_color_i}" stroke-width="{data_point_stroke_width_i}" fill="{data_point_fill_color_i}"></circle>'

        zero_line_tags = f'<line x1="{y0_width}" y1="{(bottom_y / 2) - (bar_thickness * 1.5)}" x2="{y0_width}" y2="{(bottom_y / 2) + (bar_thickness * 1.5)}" stroke="{zero_line_stroke_color}" stroke-width="{zero_line_stroke_width}"></line>'

        # Redefine the `viewbox` in terms of the `data_x_width` value; this ensures
        # that the horizontal bars are centered about their extreme values
        viewbox = f"{left_x} {top_y} {data_x_width} {bottom_y}"

    #
    # Generate box plots
    #

    if plot_type == "boxplot":
        pass

    #
    # Generate zero line for vertical bar plots
    #

    if plot_type == "bar" and single_horizontal_plot is False:
        zero_line_tags = f'<line x1="{data_x_points[0] - 27.5}" y1="{data_y0_point}" x2="{data_x_points[-1] + 27.5}" y2="{data_y0_point}" stroke="{zero_line_stroke_color}" stroke-width="{zero_line_stroke_width}"></line>'

    #
    # Generate reference line
    #

    if show_reference_line:
        stroke = reference_line_color
        stroke_width = 1
        stroke_dasharray = "4 3"
        transform = ""
        stroke_linecap = "round"
        vector_effect = "non-scaling-stroke"

        # Format value in a compact manner
        y_ref_line = _format_number_compactly(
            val=y_ref_line, currency=currency, as_integer=y_vals_integerlike, fn=y_ref_line_fmt_fn
        )

        ref_line_tags = f'<g class="ref-line"><rect x="{data_x_points[0] - 10}" y="{data_y_ref_line - 10}" width="{data_x_width + 20}" height="20" stroke="transparent" stroke-width="1" fill="transparent"></rect><line class="ref-line" x1="{data_x_points[0]}" y1="{data_y_ref_line}" x2="{data_x_width + safe_x_d}" y2="{data_y_ref_line}" stroke="{stroke}" stroke-width="{stroke_width}" stroke-dasharray="{stroke_dasharray}" transform="{transform}" stroke-linecap="{stroke_linecap}" vector-effect="{vector_effect}"></line><text x="{data_x_width + safe_x_d + 10}" y="{data_y_ref_line + 10}" fill="transparent" stroke="transparent" font-size="30px">{y_ref_line}</text></g>'

    #
    # Generate reference area
    #

    if show_reference_area:
        fill = reference_area_fill_color

        p_ul = f"{data_x_points[0]},{data_y_ref_area_u}"
        p_ur = f"{data_x_points[-1]},{data_y_ref_area_u}"
        p_lr = f"{data_x_points[-1]},{data_y_ref_area_l}"
        p_ll = f"{data_x_points[0]},{data_y_ref_area_l}"

        ref_area_path = f"M{p_ul},{p_ur},{p_lr},{p_ll}Z"

        ref_area_tags = f'<path d="{ref_area_path}" stroke="transparent" stroke-width="2" fill="{fill}" fill-opacity="0.8"></path>'

    #
    # Generate y-axis guide
    #

    if show_y_axis_guide:
        is_all_intify_y_axis = len(y_vals) == _get_n_intlike(y_vals)

        rect_tag = f'<rect x="{left_x}" y="{top_y}" width="{safe_x_d + 15}" height="{bottom_y}" stroke="transparent" stroke-width="0" fill="transparent"></rect>'

        if _is_integerlike(val_list=[y_scale_max]) and _is_integerlike(val_list=[y_scale_min]):
            y_axis_guide_vals_integerlike = True
        else:
            y_axis_guide_vals_integerlike = False

        # Format values in a compact manner
        y_value_max_label = _format_number_compactly(
            val=y_scale_max,
            currency=currency,
            as_integer=y_axis_guide_vals_integerlike,
            fn=y_axis_fmt_fn,
        )

        y_value_min_label = _format_number_compactly(
            val=y_scale_min,
            currency=currency,
            as_integer=y_axis_guide_vals_integerlike,
            fn=y_axis_fmt_fn,
        )

        if is_all_intify_y_axis:
            y_value_max_label = _remove_exponent(y_value_max_label)
            y_value_min_label = _remove_exponent(y_value_min_label)

        text_strings_min = f'<text x="{left_x}" y="{safe_y_d + data_y_height + safe_y_d - data_y_height / 25}" fill="transparent" stroke="transparent" font-size="25">{y_value_min_label}</text>'

        text_strings_max = f'<text x="{left_x}" y="{safe_y_d + data_y_height / 25}" fill="transparent" stroke="transparent" font-size="25">{y_value_max_label}</text>'

        g_y_axis_tags = f'<g class="y-axis-line">{rect_tag}{text_strings_max}{text_strings_min}</g>'

    #
    # Generate vertical data point guidelines
    #

    if show_vertical_guides:
        is_all_intify_v_guides = len(y_vals) == _get_n_intlike(y_vals)

        g_guide_strings = []

        for i, _ in enumerate(data_x_points):
            rect_strings_i = f'<rect x="{data_x_points[i] - 10}" y="{top_y}" width="20" height="{bottom_y}" stroke="transparent" stroke-width="{vertical_guide_stroke_width}" fill="transparent"></rect>'

            # Format value in a compact manner
            y_value_i = _format_number_compactly(
                val=y_vals[i], currency=currency, as_integer=y_vals_integerlike, fn=y_val_fmt_fn
            )

            x_text = data_x_points[i] + 10

            if y_value_i == "NA":
                x_text = x_text + 2

            if is_all_intify_v_guides:
                y_value_i = _remove_exponent(y_value_i)

            text_strings_i = f'<text x="{x_text}" y="{safe_y_d + 5}" fill="transparent" stroke="transparent" font-size="30px">{y_value_i}</text>'

            g_guide_strings_i = f'<g class="vert-line">{rect_strings_i}{text_strings_i}</g>'

            g_guide_strings.append(g_guide_strings_i)

        g_guide_tags = "".join(g_guide_strings)

    #
    # Generate background with repeating line pattern
    #

    svg_defs = (
        f"<defs>"
        f'<pattern id="area_pattern" width="8" height="8" patternUnits="userSpaceOnUse">'
        f'<path class="pattern-line" d="M 0,8 l 8,-8 M -1,1 l 4,-4 M 6,10 l 4,-4" stroke="'
        f"{data_area_fill_color}"
        f'" stroke-width="1.5" stroke-linecap="round" shape-rendering="geometricPrecision">'
        f"</path>"
        f"</pattern>"
        f"</defs>"
    )

    if plot_type == "line" and show_data_area:
        area_path_tags = []

        for i in range(n_segments):
            area_x = data_x_points[start_data_y_points[i] : end_data_y_points[i]]
            area_y = data_y_points[start_data_y_points[i] : end_data_y_points[i]]

            area_path_string = []

            for j in range(0, len(area_x)):
                area_path_j = f"{area_x[j]},{area_y[j]}"
                area_path_string.append(area_path_j)

            area_path_i = f"M {' '.join(area_path_string)} {area_x[-1]},{bottom_y - safe_y_d + data_point_radius[0]} {area_x[0]},{bottom_y - safe_y_d + data_point_radius[0]} Z"

            area_path_tag_i = f'<path class="area-closed" d="{area_path_i}" stroke="transparent" stroke-width="2" fill="url(#area_pattern)" fill-opacity="0.7"></path>'

            area_path_tags.append(area_path_tag_i)

        area_path_tags = " ".join(area_path_tags)

    #
    # Generate style tag for vertical guidelines and y-axis
    #

    hover_param = ":hover" if interactive_data_values else ""

    svg_style = (
        f"<style> text {{ font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace; stroke-width: 0.15em; paint-order: stroke; stroke-linejoin: round; cursor: default; }} "
        f".vert-line{hover_param} rect {{ fill: {vertical_guide_stroke_color}; fill-opacity: 40%; stroke: #FFFFFF60; color: red; }} "
        f".vert-line{hover_param} text {{ stroke: white; fill: #212427; }} "
        f".horizontal-line{hover_param} text {{stroke: white; fill: #212427; }} "
        f".ref-line{hover_param} rect {{ stroke: #FFFFFF60; }} "
        f".ref-line{hover_param} line {{ stroke: #FF0000; }} "
        f".ref-line{hover_param} text {{ stroke: white; fill: #212427; }} "
        f".y-axis-line{hover_param} rect {{ fill: #EDEDED; fill-opacity: 60%; stroke: #FFFFFF60; color: red; }} "
        f".y-axis-line{hover_param} text {{ stroke: white; stroke-width: 0.20em; fill: #1A1C1F; }} "
        f"</style>"
    )

    nanoplot_svg = _construct_nanoplot_svg(
        viewbox=viewbox,
        svg_height=svg_height,
        svg_defs=svg_defs,
        svg_style=svg_style,
        show_data_points=show_data_points,
        show_data_line=show_data_line,
        show_data_area=show_data_area,
        show_reference_line=show_reference_line,
        show_reference_area=show_reference_area,
        show_vertical_guides=show_vertical_guides,
        show_y_axis_guide=show_y_axis_guide,
        ref_area_tags=ref_area_tags,
        area_path_tags=area_path_tags,
        data_path_tags=data_path_tags,
        zero_line_tags=zero_line_tags,
        bar_tags=bar_tags,
        ref_line_tags=ref_line_tags,
        circle_tags=circle_tags,
        g_y_axis_tags=g_y_axis_tags,
        g_guide_tags=g_guide_tags,
    )

    return nanoplot_svg


def _is_intlike(n: Any, scaled_by: float = 1e17) -> bool:
    """
    https://stackoverflow.com/a/71373152
    """
    import numbers
    from decimal import Decimal

    if isinstance(n, str):
        try:
            # Replacement of minus sign (U+2212) with hyphen (necessary in some locales)
            n = float(n.replace("−", "-"))
        except ValueError:
            return False
    elif isinstance(n, Decimal):
        n = float(n)
    return isinstance(n, numbers.Real) and ((n * scaled_by - int(n) * scaled_by) == 0)


def _get_n_intlike(nums: list[Any]) -> int:
    return len([n for n in nums if _is_intlike(n)])


def _remove_exponent(n: "str | int | float") -> str:
    """
    https://docs.python.org/3/library/decimal.html#decimal-faq
    """
    from decimal import Decimal, InvalidOperation

    if isinstance(n, str):
        # Replacement of minus sign (U+2212) with hyphen (necessary in some locales)
        n = n.replace("−", "-")

    # TODO: note that in the nanoplot code, this function only runs when
    # GT believes everything is an integer. However, _format_number_compactly
    # may have run on each value and formatted them compactly (e.g. 7045 to "704K")
    # The InvalidOperation catch prevents errors on compact numbers, but is a
    # hacky patch. We need to consolidate the processing steps run for value
    # formatting.
    try:
        d = Decimal(n)
        if d == d.to_integral():
            x = d.quantize(Decimal(1))
        else:
            x = d.normalize()
        return str(int(x))
    except InvalidOperation:
        return str(n)
