from __future__ import annotations

import re
import unittest

from scripts.terminal_colors import color, xterm_color


class TerminalColorTests(unittest.TestCase):
    def test_six_digit_rgb_precedes_decimal_palette_index(self) -> None:
        self.assertEqual(color("008000", "#e6edf3"), "#008000")
        self.assertEqual(color("808080", "#e6edf3"), "#808080")
        self.assertEqual(color("000000", "#e6edf3"), "#000000")
        self.assertEqual(color("ffff00", "#e6edf3"), "#ffff00")

    def test_named_and_default_colors(self) -> None:
        self.assertEqual(color("green", "#e6edf3"), "#00cd00")
        self.assertEqual(color("default", "#e6edf3"), "#e6edf3")
        self.assertEqual(color(None, "#123456"), "#123456")

    def test_all_xterm_palette_outputs_are_valid_css_colors(self) -> None:
        for index in range(256):
            with self.subTest(index=index):
                self.assertRegex(xterm_color(index), re.compile(r"^#[0-9a-f]{6}$"))

    def test_palette_boundaries_and_short_decimal_indices(self) -> None:
        self.assertEqual(color("0", "#e6edf3"), "#000000")
        self.assertEqual(color("255", "#e6edf3"), "#eeeeee")
        self.assertEqual(xterm_color(16), "#000000")
        self.assertEqual(xterm_color(232), "#080808")
        self.assertEqual(xterm_color(255), "#eeeeee")

    def test_out_of_range_palette_indices_are_rejected(self) -> None:
        for value in (-1, 256, 9999, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    xterm_color(value)
        for value in ("256", "9999"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    color(value, "#e6edf3")


if __name__ == "__main__":
    unittest.main()
