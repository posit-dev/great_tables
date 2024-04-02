from __future__ import annotations
from typing import TYPE_CHECKING, Union, List, Callable

from ._gt_data import TextTransformFn, TextTransformFns, TextTransformInfo
from ._tbl_data import SelectExpr
from ._locations import resolve_rows_i, resolve_cols_c

if TYPE_CHECKING:
    from ._types import GTSelf


def text_transform(
    self: GTSelf,
    fns: Union[TextTransformFn, TextTransformFns],
    columns: SelectExpr = None,
    rows: Union[int, List[int], None] = None,
) -> GTSelf:

    # If a single function is supplied to `fns` then
    # repackage that into a list as the `default` function
    if isinstance(fns, Callable):
        fns = TextTransformFns(default=fns)

    row_res = resolve_rows_i(self, rows)
    row_pos = [name_pos[1] for name_pos in row_res]

    col_res = resolve_cols_c(self, columns)

    text_transformer = TextTransformInfo(fns, col_res, row_pos)

    return self._replace(_text_transforms=[*self._text_transforms, text_transformer])
