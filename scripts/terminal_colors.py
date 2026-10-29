"""Pure ANSI/VT color decoding for terminal media renderers."""

from __future__ import annotations

import re
from typing import Any


ANSI_COLORS = {
    "black": "#000000",
    "red": "#cd0000",
    "green": "#00cd00",
    "brown": "#cdcd00",
    "blue": "#0000ee",
    "magenta": "#cd00cd",
    "cyan": "#00cdcd",
    "white": "#e5e5e5",
    "brightblack": "#7f7f7f",
    "brightred": "#ff0000",
    "brightgreen": "#00ff00",
    "brightyellow": "#ffff00",
    "brightblue": "#5c5cff",
    "brightmagenta": "#ff00ff",
    "brightcyan": "#00ffff",
    "brightwhite": "#ffffff",
    "default": "default",
}


def xterm_color(index: int) -> str:
    """Return a CSS color for one bounded xterm palette index."""
    if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index <= 255:
        raise ValueError(f"xterm color index must be between 0 and 255, got {index!r}")
    palette = [
        "#000000", "#800000", "#008000", "#808000", "#000080", "#800080", "#008080", "#c0c0c0",
        "#808080", "#ff0000", "#00ff00", "#ffff00", "#0000ff", "#ff00ff", "#00ffff", "#ffffff",
    ]
    if index < 16:
        return palette[index]
    if index < 232:
        value = index - 16
        levels = (0, 95, 135, 175, 215, 255)
        red, green, blue = levels[value // 36], levels[(value // 6) % 6], levels[value % 6]
        return f"#{red:02x}{green:02x}{blue:02x}"
    gray = 8 + 10 * (index - 232)
    return f"#{gray:02x}{gray:02x}{gray:02x}"


def color(value: Any, default: str) -> str:
    """Resolve pyte's ANSI names, RGB strings, or decimal xterm indices."""
    if value is None:
        return default
    if isinstance(value, int):
        return xterm_color(value)
    text = str(value).lower()
    # pyte stores RGB SGR values as six hexadecimal characters. Numeric RGB
    # strings must be recognized before decimal xterm palette indices.
    if re.fullmatch(r"[0-9a-f]{6}", text):
        return "#" + text
    if text in ANSI_COLORS:
        resolved = ANSI_COLORS[text]
        return default if resolved == "default" else resolved
    if text.startswith("#") and re.fullmatch(r"#[0-9a-f]{6}", text):
        return text
    if text.isdigit():
        return xterm_color(int(text))
    return default
