"""Miscellaneous tools/utils that don't have a specific theme but are still valuable.

.. code-block:: python

    from plox.tools import utilities

These functions are not tied to a particular area (e.g. file system utils) but have
use cases/functionality that comes up often enough to warrant existing as a tested,
well formed module.

It is usually the case that new utilities are added to this location, and potentially,
after some time of forming mass, there is enough continuity of a set of function to
warrant splitting into their own module (e.g :py:mod:`plox.tools.files`).
"""

from __future__ import annotations

from collections.abc import Generator, Iterable
from functools import reduce
from itertools import islice
from logging import getLogger
from typing import Any, Callable, Optional, TypeVar

logger = getLogger(__name__)

_T = TypeVar("_T")
TupleVal = tuple[str, Optional[str], str]


def composite_function(*functions: Callable[[Any], Any]) -> Callable[[Any], Optional[Any]]:
    """Compose multiple functions to a single callable.

    Example:

        >>> def square(x: int) -> int:
        ...     return x**2
        >>>
        >>> def half(x: int) -> int:
        >>>     return x // 2
        >>>
        >>> composite_function(square, half)(3)
        4
        >>> composite_function(square, half)(2)
        2

    Args:
        functions: A variable number of
            callable functions to compose.

    Returns:
        typing.Callable[[typing.Any], typing.Optional[typing.Any]]: The resulting composite
        function.
    """

    def compose(f: Any, g: Any) -> Any:
        return lambda x: g(f(x))  # pyright: ignore

    return reduce(compose, functions, lambda x: x)  # pyright: ignore


def is_listlike(thing: Any) -> bool:
    """Check if a given thing is seemingly a list.

    Python has iterable strings, and when iterating over something that is sometimes
    a list or sometimes a string, usually don't want to iterate over the chars in the
    string, but want to iterate over the items in the list (see
    :func:`~plox.tools.utilities.unnest`)

    Example:

        >>> is_listlike("a")
        False
        >>> is_listlike("[]")
        False
        >>> is_listlike([])
        True
        >>> is_listlike([1, 2, 3])
        True

    Args:
        thing: Item to check if behaves like a list.

    Returns:
        bool: ``True`` if item behaves like list, else ``False``.
    """
    return isinstance(thing, (tuple, list))


def is_same_list(l1: list[str], l2: list[str]) -> bool:
    """Check if two lists are identical.

    Args:
        l1: First list to compare.
        l2: Second list to compare.

    Returns:
        bool: True if identical, false otherwise.
    """
    if len(l1) != len(l2):
        return False

    return all(li == l2[ix] for ix, li in enumerate(l1))


def partition(
    d: dict[Any, Any], key_fn: Callable[[Any], bool]
) -> tuple[dict[Any, Any], dict[Any, Any]]:
    """Split a dictionary into two separate ones based on a filtering function.

    Example:

        >>> d = {"a": 10, "B": 20, "c": 30, "D": 50}
        >>> one, two = partition(d, lambda key: key.islower())
        >>> one
        {"a": 10, "c": 30}
        >>> two
        {"B": 20, "D": 50}

    Args:
        d: The original dictionary to split.
        key_fn: The function to operate against each
            dictionary key in the original dictionary. If successful for a
            given key, adds key:value to the first dictionary returned.
            Otherwise, adds the key:value to the second dictionary returned.

    Returns:
        tuple[dict[typing.Any, typing.Any], dict[typing.Any, typing.Any]]: The two sets of
        dictionaries resulting from applying the filtering function to every key in the
        original dictionary.
    """
    in_g: dict[Any, Any] = {}
    out_g: dict[Any, Any] = {}

    for k, v in d.items():
        if key_fn(k):
            in_g[k] = v
        else:
            out_g[k] = v

    return in_g, out_g


def to_tuples(d: dict[str, Any]) -> list[tuple[str, TupleVal]]:
    """Convert a dictionary of key:value pairs to a list of tuples.

    The list of tuples will be of key:value pairing.

    Example:

        >>> to_tuples({"a": "b", "c": "d"})
        [("a", "b"), ("c", "d")]

    Args:
        d: The dictionary whose values will be split to
            a list of tuples.

    Returns:
        list[tuple[str, TupleVal]]: A list of tuples representing the input
        dict's key:value pairs.
    """
    acc: list[tuple[str, TupleVal]] = []

    for k, v in d.items():
        acc.append((k, v))

    return acc


def unnest(*p: Any) -> list[Any]:
    """Unnest arbitrarily nested items in a list to flat level list.

    Note: This is done particularly because otherwise if a string occurs in
    the list, it gets exploded to individual characters, which is not desired.

    Examples:

        >>> unnest()
        []
        >>> unnest([])
        []
        >>> unnest("a", "b", ["c"])
        ["a", "b", "c"]
        >>> unnest("a")
        ["a"]
        >>> unnest(["a"])
        ["a"]
        >>> unnest([[[["a"]]]])
        ["a"]
        >>> unnest("a", {"b": "c"}, ["d", "e"], "f")
        ["a", {"b": "c"}, "d", "e", "f"]

    Args:
        p: Arbitrarily nested list to flatten.

    Returns:
        list[typing.Any]: The input list with 1 level nesting.
    """

    # b/c more_itertools.recipes.flatten doesn't recur down deep structures and
    # doesn't exclude nulls / empty iterables
    def extract(acc: list[Any], items: list[Any]) -> Optional[Any]:
        if not is_listlike(items):
            return items
        if len(items) == 0:
            return None
        for item in items:
            if (extracted := extract(acc, item)) is not None:
                acc.append(extracted)
        return None

    acc: list[Any] = []
    if p != ():
        extract(acc, list(p))
    return acc


def window_iterator(seq: Iterable[_T], n: int = 2) -> Generator[tuple[_T, ...], None, None]:
    """Return a sliding window (of width n) over data from the iterable.

    s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...

    Example:

        >>> for window in window_iterator(range(10)):
        ...     print(window)
        (0, 1)
        (1, 2)
        (2, 3)
        (3, 4)
        (4, 5)
        (5, 6)
        (6, 7)
        (7, 8)
        (8, 9)

        >>> for window in window_iterator(range(6), 3):
        ...     print(",".join(map(str, window)))
        0,1,2
        1,2,3
        2,3,4
        3,4,5

    Args:
        seq: The iterator to generate windows from.
        n: The width of window to generate; default is 2.

    Returns:
        typing.Generator[tuple[_T, ...], None, None]: A generator of windows of desired size,
        containing a tuple of two objects of the same type of the original iterator.
    """
    seq_size = sum(1 for _ in seq)
    it = iter(seq)
    if n > seq_size:
        yield tuple(islice(it, seq_size))
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result
