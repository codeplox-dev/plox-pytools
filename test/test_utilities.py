from plox.tools.utilities import (
    composite_function,
    is_listlike,
    is_same_list,
    partition,
    to_tuples,
    unnest,
    window_iterator,
)


def test_composite_functions():
    def square(x: int) -> int:
        return x**2

    def half(x: int) -> int:
        return x // 2

    assert composite_function(square, half)(3) == 4
    assert composite_function(square, half)(2) == 2


def test_is_listlist():
    assert not is_listlike("a")
    assert not is_listlike(0)
    assert not is_listlike({"A": "A"})
    assert not is_listlike({"A": {"B": "B"}})

    assert is_listlike([])
    assert is_listlike([1])
    assert is_listlike([1, {"a": "b"}])
    assert is_listlike((1, 2, 3))


def test_is_same_list():
    l1 = ["a", "b", "c", "d"]
    l2 = ["a", "b", "c", "d"]
    l3 = ["a", "b", "c", "d", ""]
    l4 = ["a", "b", "d", "c"]
    assert is_same_list(l1, l2)
    assert not is_same_list(l1, l3)
    assert not is_same_list(l1, l4)


def test_partition():
    assert (partition({"a": "b", "c": "d"}, lambda k: k == "default")) == ({}, {"a": "b", "c": "d"})
    assert (partition({"default": "a", "b": "c"}, lambda k: k == "default")) == (
        {"default": "a"},
        {"b": "c"},
    )


def test_to_tuples():
    d = {"a": "b", "c": "d", "e": "f"}
    assert to_tuples(d) == [("a", "b"), ("c", "d"), ("e", "f")]


def test_unnest():
    assert unnest() == []
    assert unnest([]) == []
    assert unnest("a", "b", ["c"]) == ["a", "b", "c"]
    assert unnest("a") == ["a"]
    assert unnest(["a"]) == ["a"]
    assert unnest([[[["a"]]]]) == ["a"]
    assert unnest("a", {"b": "c"}, ["d", "e"], "f") == ["a", {"b": "c"}, "d", "e", "f"]


def test_window_iterator():
    assert list(window_iterator(["a", "b", "c", "d"])) == [("a", "b"), ("b", "c"), ("c", "d")]
    assert list(window_iterator(["a", "b", "c"])) == [("a", "b"), ("b", "c")]
    assert list(window_iterator(["a", "b", "c", "d"], 57)) == [("a", "b", "c", "d")]
    assert list(window_iterator(["a", "b", "c", "d"], 3)) == [("a", "b", "c"), ("b", "c", "d")]
