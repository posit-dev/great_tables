from __future__ import annotations

import importlib
import itertools
import re
from collections.abc import Generator, Set
from types import ModuleType
from typing import TYPE_CHECKING, Any, Iterable, Iterator

from ._helpers import UnitStr
from ._tbl_data import _get_cell, _set_cell, get_column_names, n_rows
from ._text import BaseText, _process_text

if TYPE_CHECKING:
    from ._gt_data import FormatInfo, GTData
    from ._tbl_data import TblData


def _try_import(name: str, pip_install_line: str | None = None) -> ModuleType:
    try:
        return importlib.import_module(name)
    except ImportError:
        if pip_install_line is not None:
            raise ImportError(
                f"Module {name} not found. Run the following to install."
                f"\n\n`{pip_install_line}`"
            ) from None
        else:
            raise ImportError(f"Module {name} not found.")


def heading_has_title(title: str | BaseText | None) -> bool:
    return title is not None


def heading_has_subtitle(subtitle: str | BaseText | None) -> bool:
    return subtitle is not None


def _match_arg(x: str, lst: list[str]) -> str:
    # Ensure that `lst` has at least one element
    if len(lst) == 0:
        raise ValueError("The `lst` object must contain at least one element.")

    # Ensure that all elements in `lst` are strings
    if not all(isinstance(el, str) for el in lst):
        raise ValueError("All elements in the `lst` object must be strings.")

    # Ensure that `lst` does not have duplicates by comparing against
    # a set based on `lst` (using `set()` will remove duplicates)
    if len(lst) != len(set(lst)):
        raise ValueError("The `lst` object must contain unique elements.")

    matched = [el for el in lst if x in el]

    # Raise error if there is no match
    if len(matched) == 0:
        raise ValueError(f"The supplied value (`{x}`) is not an allowed option.")

    return matched.pop()


def _assert_str_scalar(x: Any) -> None:
    if not isinstance(x, str):
        raise AssertionError(f"The supplied value (`{x}`) is not a string.")


def _assert_str_list(x: Any) -> None:
    if not isinstance(x, list):
        raise AssertionError(f"The supplied value (`{x}`) is not a list.")
    if not all(map(lambda x: isinstance(x, str), x)):
        raise AssertionError("Not all elements of the supplied list are strings.")


def _assert_str_in_set(x: str, set: list[str]) -> None:
    if x not in set:
        raise AssertionError(f"The string `{x}` is not part of the defined `set`.")


def _assert_list_is_subset(x: list[Any], set_list: list[Any]) -> None:
    if not set(x).issubset(set(set_list)):
        raise AssertionError("The columns provided are not present in the table.")


def _str_scalar_to_list(x: str) -> list[str]:
    _assert_str_scalar(x)
    return [x]


class OrderedSet(Set[Any]):
    def __init__(self, d: Iterable[Any] = ()) -> None:
        self._d = self._create(d)

    def _create(self, d: Iterable[Any]) -> dict[Any, bool]:
        return {k: True for k in d}

    def as_set(self) -> set[Any]:
        return set(self._d)

    def as_list(self) -> list[Any]:
        return list(self._d)

    def as_dict(self) -> dict[Any, bool]:
        return dict(self._d)

    def __contains__(self, k: Any) -> bool:
        return k in self._d

    def __iter__(self) -> Iterator[Any]:
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def __repr__(self) -> str:
        cls_name = type(self).__name__
        lst = self.as_list()
        return f"{cls_name}({lst!r})"


def _as_css_font_family_attr(fonts: list[str], value_only: bool = False) -> str:
    fonts_w_spaces: list[str] = list(map(lambda x: f"'{x}'" if " " in x else x, fonts))

    fonts_str = ", ".join(fonts_w_spaces)

    if value_only:
        return fonts_str

    return f"font-family: {fonts_str};"


def _collapse_list_elements(lst: list[Any], separator: str = "") -> str:
    """
    Concatenates all elements of a list into a single string, separated by a given separator.

    Args:
        lst (list): The list to be collapsed.
        separator (str, optional): The separator to be used. Defaults to "".

    Returns:
        str: The collapsed string.
    """
    return separator.join(lst)


def _insert_into_list(lst: list[Any], el: Any) -> list[Any]:
    """
    Inserts an element into the beginning of a list and returns the updated list.

    Args:
        lst (list[Any]): The list to insert the element into.
        el (Any): The element to insert.

    Returns:
        list[Any]: The updated list with the element inserted at the beginning.
    """
    lst.insert(0, el)
    return lst


def _str_replace(string: str, pattern: str, replace: str) -> str:
    return string.replace(pattern, replace)


def _str_detect(string: str, pattern: str) -> bool:
    return bool(re.match(pattern, string))


def pairwise(iterable: Iterable[Any]) -> Generator[tuple[Any, Any], None, None]:
    """
    https://docs.python.org/3/library/itertools.html#itertools.pairwise
    pairwise('ABCDEFG') → AB BC CD DE EF FG
    """
    # This function can be replaced by `itertools.pairwise` if we only plan to support
    # Python 3.10+ in the future.
    iterator = iter(iterable)
    a = next(iterator, None)
    for b in iterator:
        yield a, b
        a = b


def seq_groups(seq: Iterable[Any]) -> Generator[tuple[Any, int], None, None]:
    iterator = iter(seq)

    # TODO: 0-length sequence
    a = next(iterator)  # will raise StopIteration if `seq` is empty

    try:
        b = next(iterator)
    except StopIteration:
        yield a, 1
        return

    # We can confirm that we have two elements and both are not `None`,
    # so we can chain them back together as the original seq.
    seq = itertools.chain([a, b], iterator)

    crnt_ttl = 1
    for crnt_el, next_el in pairwise(seq):
        if is_equal(crnt_el, next_el):
            crnt_ttl += 1
        else:
            yield crnt_el, crnt_ttl
            crnt_ttl = 1

    # final step has same elements, so we need to yield one last time
    if is_equal(crnt_el, next_el):
        yield crnt_el, crnt_ttl
    else:
        yield next_el, 1


def is_equal(x: Any, y: Any) -> bool:
    return x is not None and x == y


def _flatten_list(x: Any) -> list[Any]:
    """
    Flatten a list of values.
    """

    flat_list: list[Any] = []
    for element in x:
        if isinstance(element, list):
            flat_list.extend(_flatten_list(element))
        else:
            flat_list.append(element)
    return flat_list


# TODO: type annotations for `data`, `data_tbl`, `formats`, and the return value are not included
# yet since that would result in a circular import. This will be fixed in the future (when HTML
# escaping is implemented).
def _migrate_unformatted_to_output(
    data: GTData, data_tbl: TblData, formats: list[FormatInfo], context: str
) -> GTData:
    """
    Escape unformatted cells so they are safe for a specific output context.
    """

    # TODO: This function will eventually be applied to all context types but for now
    # it's just used for LaTeX output
    if context != "latex":
        return data

    all_formatted_cells: list[list[tuple[str, int]]] = []

    for fmt in formats:
        eval_func = getattr(fmt.func, context, fmt.func.default)
        if eval_func is None:
            raise Exception("Internal Error")

        # Accumulate all formatted cells in the table
        all_formatted_cells.append(fmt.cells.resolve())

    # Deduplicate the list of formatted cells
    deduplicate_formatted_cells = list(set(_flatten_list(all_formatted_cells)))

    # Get all visible cells in the table
    all_visible_cells = _get_visible_cells(data=data_tbl)

    # Get the difference between the visible cells and the formatted cells
    all_unformatted_cells = list(set(all_visible_cells) - set(deduplicate_formatted_cells))

    # TODO: this currently will only be used for LaTeX (HTML escaping will be performed
    # in the future)

    for col, row in all_unformatted_cells:
        # Get the cell value and cast as string
        cell_value = _get_cell(data_tbl, row, col)
        cell_value_str = str(cell_value)

        result = _process_text(cell_value_str, context=context)

        _set_cell(data._body.body, row, col, result)

    return data


# Get a list of tuples for all visible cells in the table
# Define the type of `data` as `TblData` when doing so won't result in a circular import
def _get_visible_cells(data: TblData) -> list[tuple[str, int]]:
    return [(col, row) for col in get_column_names(data) for row in range(n_rows(data))]


def is_valid_http_schema(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def _handle_units_syntax(cases: dict[str, str | BaseText]) -> dict[str, UnitStr | str | BaseText]:
    # Handle units syntax in labels (e.g., "Density ({{ppl / mi^2}})")
    kwargs: dict[str, UnitStr | str | BaseText] = {}

    for k, v in cases.items():
        if isinstance(v, str):
            unitstr_v = UnitStr.from_str(v)

            if len(unitstr_v.units_str) == 1 and isinstance(unitstr_v.units_str[0], str):
                kwargs[k] = unitstr_v.units_str[0]
            else:
                kwargs[k] = unitstr_v

        elif isinstance(v, BaseText):
            kwargs[k] = v

        else:
            raise ValueError(
                "Column labels must be strings or BaseText objects. Use `md()` or `html()` for formatting."
            )
    return kwargs
