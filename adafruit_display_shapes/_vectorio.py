# SPDX-FileCopyrightText: 2026 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Helpers for drawing display shapes with :py:mod:`vectorio`."""

import displayio

try:
    from vectorio import Rectangle as _Rectangle
except ImportError:
    _Rectangle = None

# vectorio.Rectangle grew corner radius, outline width and outline color index after display
# shapes first shipped. Firmware without them can only draw square, unfilled shapes from a
# bitmap, so the shapes fall back to building one.
HAS_VECTORIO = _Rectangle is not None and hasattr(_Rectangle, "radius")


def get_color(palette, index):
    """Return the color at ``index``, or ``None`` when that entry is transparent."""
    if palette.is_transparent(index):
        return None
    return palette[index]


def set_color(palette, index, color):
    """Set the entry at ``index`` to ``color``, or make it transparent when color is None."""
    if color is None:
        palette[index] = 0
        palette.make_transparent(index)
    else:
        palette[index] = color
        palette.make_opaque(index)
