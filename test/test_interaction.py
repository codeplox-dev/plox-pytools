from _pytest.monkeypatch import MonkeyPatch
from pytest import CaptureFixture

from plox.tools.interaction import confirm


def test_confirm_yes(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")
    assert confirm("test")


def test_confirm_no(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")
    assert not confirm("test")


def test_confirm_yes_default(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert confirm("test", yes_is_default=True)


def test_confirm_no_default(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert not confirm("test", yes_is_default=False)


def test_confirm_bad_resp(monkeypatch: MonkeyPatch, capsys: CaptureFixture[bytes]):
    resps = iter(["garbage", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(resps))
    assert confirm("test", yes_is_default=False)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Incorrect response 'garbage'"
    assert captured.err.strip() == ""


def test_confirm_silent():
    assert confirm("", False, silent=True)
    assert confirm("", True, silent=True)
