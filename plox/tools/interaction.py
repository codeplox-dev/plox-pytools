"""Methods for user input/interaction/etc.

.. code-block:: python

    from plox.tools import interaction
"""

from typing import Optional, cast

from pick import pick

RESET = "\x1b[0m"


def blue(msg: str) -> str:
    """Wrap an input string so that is is printed with blue coloring escape codes."""
    blue = "\033[0;34m"
    return f"{blue}{msg}{RESET}"


def red(msg: str) -> str:
    """Wrap an input string so that is is printed with red coloring escape codes."""
    red = "\x1b[31;20m"
    return f"{red}{msg}{RESET}"


def yellow(msg: str) -> str:
    """Wrap an input string so that is is printed with yellow coloring escape codes."""
    yellow = "\x1b[33;20m"
    return f"{yellow}{msg}{RESET}"


def bold_red(msg: str) -> str:
    """Wrap an input string so that is is printed with bold red coloring escape codes."""
    bold_red = "\x1b[31;1m"
    return f"{bold_red}{msg}{RESET}"


def confirm(msg: str, yes_is_default: bool = False, silent: bool = False) -> bool:
    """Get confirmation from a user regarding a message.

    If ``silent=True`` is passed, validation from user input is skipped an
    method automatically continues.

    Args:
        msg (str): The prompt to get Y/N input from the user on.
        yes_is_default (bool): Optional, if provided, the default (empty
            enter behaviour will be Y)
        silent (bool): Whether or not to skip user input and just return
            true immediately.

    Returns:
        bool: True if user's response is yes, else False.
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

    Args:
        choices (list[str]): The list of options to choose from.
        prompt (str): The prompt to display above the choices in the menu.
        indicator (str): Indicator icon on left hand side of current selection.
        trim_suffix (Optional[str]): Potential suffix to remove from the selected choice.
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
        choices (list[str]): The list of options to choose from.
        prompt (str): The prompt to display above the choices in the menu.
        indicator (str): Indicator icon on left hand side of current selection.
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
