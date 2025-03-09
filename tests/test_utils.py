from collections.abc import Generator
import pytest


from great_tables import GT, exibble, md
from great_tables._tbl_data import is_na
from great_tables._utils import (
    _assert_list_is_subset,
    _assert_str_in_set,
    _assert_str_list,
    _assert_str_scalar,
    _collapse_list_elements,
    _handle_units_syntax,
    _insert_into_list,
    _match_arg,
    _migrate_unformatted_to_output,
    OrderedSet,
    _str_scalar_to_list,
    is_valid_http_schema,
    heading_has_subtitle,
    heading_has_title,
    seq_groups,
)


def test_heading_has_title():
    assert heading_has_title("title")
    assert not heading_has_title(None)


def test_heading_has_subtitle():
    assert heading_has_subtitle("subtitle")
    assert not heading_has_subtitle(None)


def test_match_arg():
    assert _match_arg("x", ["a", "b", "c", "x"]) == "x"


def test_match_arg_raises():
    with pytest.raises(ValueError) as exc_info:
        _match_arg("x", [])

    assert "The `lst` object must contain at least one element." in exc_info.value.args[0]

    with pytest.raises(ValueError) as exc_info:
        _match_arg("x", [1])

    assert "All elements in the `lst` object must be strings." in exc_info.value.args[0]

    with pytest.raises(ValueError) as exc_info:
        _match_arg("x", ["a", "a"])

    assert "The `lst` object must contain unique elements." in exc_info.value.args[0]

    with pytest.raises(ValueError) as exc_info:
        _match_arg("x", ["a"])

    assert "is not an allowed option." in exc_info.value.args[0]


def test_assert_str_scalar():
    _assert_str_scalar("a")


def test_assert_str_scalar_raises():
    with pytest.raises(AssertionError) as exc_info:
        _assert_str_scalar(1)

    assert "is not a string." in exc_info.value.args[0]


def test_assert_str_list():
    _assert_str_list(["a"])


def test_assert_str_list_raises():
    with pytest.raises(AssertionError) as exc_info:
        _assert_str_list(1)

    assert "is not a list." in exc_info.value.args[0]

    with pytest.raises(AssertionError) as exc_info:
        _assert_str_list([1])

    assert "Not all elements of the supplied list are strings." in exc_info.value.args[0]


def test_assert_str_in_set():
    _assert_str_in_set("a", ["a", "b", "c"])


def test_assert_str_in_set_raises():
    with pytest.raises(AssertionError) as exc_info:
        _assert_str_in_set("x", ["a", "b", "c"])

    assert "is not part of the defined `set`." in exc_info.value.args[0]


def test_assert_list_is_subset():
    _assert_list_is_subset([1, 2], [1, 2, 3])


def test_assert_list_is_subset_raises():
    with pytest.raises(AssertionError) as exc_info:
        _assert_list_is_subset([1, 2], [2, 3, 4])

    assert "The columns provided are not present in the table." in exc_info.value.args[0]


def test_str_scalar_to_list():
    x = _str_scalar_to_list("x")
    assert isinstance(x, list)
    assert x[0] == "x"


def test_orderedSet():
    o = OrderedSet([1, 2, "x", "y", 1, 2])

    assert all(x in o for x in [1, 2, "x", "y"])
    assert len(o) == 4
    assert list(o) == [1, 2, "x", "y"]
    assert o.as_list() == [1, 2, "x", "y"]
    assert o.as_set() == {1, 2, "x", "y"}
    assert o.as_dict() == {1: True, 2: True, "x": True, "y": True}
    assert repr(o) == "OrderedSet([1, 2, 'x', 'y'])"


@pytest.mark.parametrize(
    "iterable, ordered_list",
    [
        (["1", "2", "3"], ["1", "2", "3"]),
        (["1", "3", "2", "3", "1"], ["1", "3", "2"]),
        ((1, 3, 2, 3, 1, 1, 3, 2, 2), [1, 3, 2]),
        (iter("223311"), ["2", "3", "1"]),
    ],
)
def test_create_ordered_list(iterable, ordered_list):
    assert OrderedSet(iterable).as_list() == ordered_list


def test_collapse_list_elements():
    lst = ["a", "b", "c"]
    assert _collapse_list_elements(lst) == "abc"
    assert _collapse_list_elements(lst, "#") == "a#b#c"


def test_insert_into_list():
    lst = ["b", "c"]
    assert _insert_into_list(lst, "a") == ["a", "b", "c"]


@pytest.mark.parametrize(
    "seq, grouped",
    [
        ("a", [("a", 1)]),
        ("abc", [("a", 1), ("b", 1), ("c", 1)]),
        ("aabbcc", [("a", 2), ("b", 2), ("c", 2)]),
        ("aabbccd", [("a", 2), ("b", 2), ("c", 2), ("d", 1)]),
        (("a", "b", "c"), [("a", 1), ("b", 1), ("c", 1)]),
        (("aa", "bb", "cc"), [("aa", 1), ("bb", 1), ("cc", 1)]),
        (iter("xyyzzz"), [("x", 1), ("y", 2), ("z", 3)]),
        ((i for i in "333221"), [("3", 3), ("2", 2), ("1", 1)]),
        (["a", "a", "b", None, "c"], [("a", 2), ("b", 1), (None, 1), ("c", 1)]),
        (["a", "a", "b", None, None, "c"], [("a", 2), ("b", 1), (None, 1), (None, 1), ("c", 1)]),
        ([None, "a", "a", "b"], [(None, 1), ("a", 2), ("b", 1)]),
        ([None, None, "a", "a", "b"], [(None, 1), (None, 1), ("a", 2), ("b", 1)]),
        ([None, None, None, "a", "a", "b"], [(None, 1), (None, 1), (None, 1), ("a", 2), ("b", 1)]),
        ([None, None, None], [(None, 1), (None, 1), (None, 1)]),
    ],
)
def test_seq_groups(seq, grouped):
    g = seq_groups(seq)
    assert isinstance(g, Generator)
    assert list(g) == grouped


def test_seq_groups_raises():
    """
    https://stackoverflow.com/questions/66566960/pytest-raises-does-not-catch-stopiteration-error
    """
    with pytest.raises(RuntimeError) as exc_info:
        next(seq_groups([]))
    assert "StopIteration" in str(exc_info.value)


def test_migrate_unformatted_to_output_latex():
    gt_tbl = GT(exibble.head(2)).fmt_number(columns="num", decimals=3)

    # After rendering the data cells all the unformatted cells will be NA values in the
    # body of the table
    rendered = gt_tbl._render_formats(context="latex")

    assert is_na(rendered._body.body, rendered._body.body["char"].tolist()).tolist() == [True, True]

    # Migrate unformatted data to their corresponding data cells, the expectation is that
    # unformatted cells will no longer be NA but have the values from the original data
    migrated = _migrate_unformatted_to_output(
        data=rendered, data_tbl=rendered._tbl_data, formats=rendered._formats, context="latex"
    )

    assert migrated._body.body["char"].tolist() == ["apricot", "banana"]


def test_migrate_unformatted_to_output_html():
    gt_tbl = GT(exibble.head(2)).fmt_number(columns="num", decimals=3)

    # After rendering the data cells all the unformatted cells will be NA values in the
    # body of the table
    rendered = gt_tbl._render_formats(context="html")

    assert is_na(rendered._body.body, rendered._body.body["char"].tolist()).tolist() == [True, True]

    # For HTML output, the `_migrate_unformatted_to_output()` has not been implemented yet so
    # we expect the same output as the input (NA values for unformatted cells)
    migrated = _migrate_unformatted_to_output(
        data=rendered, data_tbl=rendered._tbl_data, formats=rendered._formats, context="html"
    )

    assert is_na(migrated._body.body, migrated._body.body["char"].tolist()).tolist() == [True, True]


@pytest.mark.parametrize(
    "url", ["http://posit.co/", "http://posit.co", "https://posit.co/", "https://posit.co"]
)
def test_is_valid_http_schema(url: str):
    assert is_valid_http_schema(url)


def test_handle_units_syntax():
    from great_tables._text import BaseText

    new_kwargs = _handle_units_syntax({"column_label_1": "abc", "column_label_2": md(text="xyz")})

    assert all(isinstance(v, (str, BaseText)) for v in new_kwargs.values())


def test_handle_units_syntax_raises():
    with pytest.raises(ValueError) as exc_info:
        _handle_units_syntax({"column_label": 123})

    assert (
        "Column labels must be strings or BaseText objects. Use `md()` or `html()` for formatting."
        in exc_info.value.args[0]
    )
