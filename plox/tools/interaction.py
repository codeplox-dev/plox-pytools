"""Methods for user input/interaction/etc.

.. code-block:: python

    from plox.tools import interaction
"""

from typing import Optional, cast

from pick import pick

_reset = "\x1b[0m"


def blue(msg: str) -> str:
    """Wrap an input string so that is is printed with blue coloring escape codes."""
    blue = "\033[0;34m"
    return f"{blue}{msg}{_reset}"


def red(msg: str) -> str:
    """Wrap an input string so that is is printed with red coloring escape codes."""
    red = "\x1b[31;20m"
    return f"{red}{msg}{_reset}"


def yellow(msg: str) -> str:
    """Wrap an input string so that is is printed with yellow coloring escape codes."""
    yellow = "\x1b[33;20m"
    return f"{yellow}{msg}{_reset}"


def bold_red(msg: str) -> str:
    """Wrap an input string so that is is printed with bold red coloring escape codes."""
    bold_red = "\x1b[31;1m"
    return f"{bold_red}{msg}{_reset}"


def confirm(msg: str, yes_is_default: bool = False, silent: bool = False) -> bool:
    """Get confirmation from a user regarding a message.

    If ``silent=True`` is passed, validation from user input is skipped an
    method automatically continues.

    Example:

        >>> confirm("Proceed?")
        Proceed? (y/N) # entered "", default N
        False

        >>> confirm("Proceed?")
        Proceed? (y/N) # entered "y"
        True

        >>> confirm("Proceed?", yes_is_default=True)
        Proceed? (Y/n) # entered "", default Y
        True

        >>> confirm("Proceed?", silent=True)
        True

    Args:
        msg: The prompt to get Y/N input from the user on.
        yes_is_default: Optional, if provided, the default (empty
            enter behaviour will be Y)
        silent: Whether or not to skip user input and just return
            true immediately.

    Returns:
        bool: ``True`` if user's response is yes, else ``False``.
    """
    if silent:
        return True

    yes, no = "y", "n"
    default, options = (yes, "(Y/n)") if yes_is_default else (no, "(y/N)")

    while True:
        response = input(f"{msg} {options} ").lower()
        if not response:
            response = default

        if response not in (yes, no):
            print(f"Incorrect response '{response}'")  # noqa: T201
        else:
            return response == yes


def single_choice_menu(
    choices: list[str], prompt: str, indicator: str = "=>", trim_suffix: Optional[str] = None
) -> str:
    """Prompt the user with a visual menu and return a single item they choose.

    Example:

        >>> single_choice_menu(["foo", "bar", "baz"], "Pick one")
        #  < spawns interactive terminal menu, selected foo >
        'foo'

    Args:
        choices: The list of options to choose from.
        prompt: The prompt to display above the choices in the menu.
        indicator: Indicator icon on left hand side of current selection.
        trim_suffix: Potential suffix to remove from the selected choice.
            Default is ``None``. Useful in cases where menuing choices are ordered/sorted
            and say for example, the top pick is appened with ``... (latest)`` but you're
            still only interested in the ``...``
    """
    selected, _ = pick(  # pyright: ignore
        choices,
        prompt,
        indicator=indicator,
    )
    selected = selected.removesuffix(trim_suffix) if trim_suffix else selected  # pyright: ignore
    return cast(str, selected)


def multi_choice_menu(choices: list[str], prompt: str, indicator: str = "=>") -> list[str]:
    """Prompt the user with a menu and return a list of (potentially multiple) items they choose.

    Args:
        choices: The list of options to choose from.
        prompt: The prompt to display above the choices in the menu.
        indicator: Indicator icon on left hand side of current selection.
    """
    selected: list[str] = pick(  # pyright: ignore
        choices,
        prompt,
        indicator=indicator,
        multiselect=True,
        min_selection_count=1,
    )
    selected = [tup[0] for tup in selected]
    return selected
