"""Miscellaneous tools/utils that don't have a specific theme but are still valuable.

.. code-block:: python

    from plox.tools import utilities
"""

from collections.abc import Generator, Iterable
from functools import reduce
from itertools import islice
from logging import getLogger
from typing import Any, Callable, Optional, TypeVar

logger = getLogger(__name__)

T = TypeVar("T")
TupleVal = tuple[str, Optional[str], str]


def partition(
    d: dict[Any, Any], key_fn: Callable[[Any], bool]
) -> tuple[dict[Any, Any], dict[Any, Any]]:
    """Split a dictionary into two separate ones based on a filtering function.

    Example:

        >> one, two = partition({"a": 10, "B": 20, "c": 30}, lambda key: key.islower())
        >> one
        {"a": 10, "c": 30}
        >> two
        {"B": 20}

    Args:
        d (dict[Any, Any]): The original dictionary to split.
        key_fn (Callable[[Any], bool]): The function to operate against each
            dictionary key in the original dictionary. If successful for a
            given key, adds key:value to the first dictionary returned.
            Otherwise, adds the key:value to the second dictionary returned.

    Returns:
        tuple[dict[Any, Any], dict[Any, Any]]: The two sets of dictionaries
        resulting from applying the filtering function to every key in the
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


def is_same_list(o1: list[str], o2: list[str]) -> bool:
    """Check if two lists are identical.

    Args:
        o1 (list[str]): First list to compare.
        o2 (list[str]): Second list to compare.

    Returns:
        bool: True if identical, false otherwise.
    """
    if len(o1) != len(o2):
        return False

    return all(li == o2[ix] for ix, li in enumerate(o1))


def to_tuples(d: dict[str, Any]) -> list[tuple[str, TupleVal]]:
    """Convert a dictionary of key:value pairs to a list of tuples.

    The list of tuples will be of key:value pairing.

    Example:

        >>> to_tuples({"a": "b", "c": "d"})
        [("a", "b"), ("c", "d")]

    Args:
        d (dict[str, Any]): The dictionary whose values will be split to
            a list of tuples.

    Returns:
        list[tuple[str, TupleVal]]: A list of tuples representing the input
        dict's key:value pairs.
    """
    acc: list[tuple[str, TupleVal]] = []

    for k, v in d.items():
        acc.append((k, v))

    return acc


def composite_function(*functions: Any) -> Callable[[Any], Optional[Any]]:
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
        functions (Any): A variable number of callable functions to compose.

    Returns:
        Callable[[Any], Optional[Any]]: The resulting composite function.
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
        thing (Any): Item to check if behaves like a list.

    Returns:
        bool: ``True`` if item behaves like list, else ``False``.
    """
    return isinstance(thing, (tuple, list))


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
        p (Any): Arbitrarily nested list to flatten.

    Returns:
        list[Any]: The input list with 1 level nesting.
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


def window_iterator(seq: Iterable[T], n: int = 2) -> Generator[tuple[T, T], None, None]:
    """Return a sliding window (of width n) over data from the iterable.

    s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...

    Args:
        seq (Iterator[T]): The iterator to generate windows from.
        n (int): The width of window to generate; default is 2.

    Returns:
        Generator[tuple[T, T], None, None]: A generator of windows of desired size, containing a
        tuple of two objects of the same type of the original iterator.
    """
    seq_size = sum(1 for _ in seq)
    it = iter(seq)
    if n > seq_size:
        yield tuple(islice(it, seq_size))  # type: ignore
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result  # type: ignore
    for elem in it:
        result = result[1:] + (elem,)
        yield result  # type: ignore
