# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`rect`
================================================================================

Various common shapes for use with displayio - Rectangle shape!


* Author(s): Limor Fried

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

try:
    from typing import Optional
except ImportError:
    pass

import displayio

from adafruit_display_shapes._vectorio import HAS_VECTORIO, get_color, set_color

if HAS_VECTORIO:
    from vectorio import Rectangle as _Rectangle
else:
    # No vectorio shape styles on this firmware, so the rectangle is drawn into a bitmap.
    from displayio import TileGrid as _Rectangle

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Shapes.git"

# Both implementations take the fill from palette entry 0 and the outline from entry 1.
_FILL = 0
_OUTLINE = 1


class Rect(_Rectangle):
    """A rectangle.

    The rectangle is drawn with :py:mod:`vectorio` when the firmware has it, which needs no
    bitmap and redraws only what changed. Older firmware builds a bitmap instead.

    :param int x: The x-position of the top left corner.
    :param int y: The y-position of the top left corner.
    :param int width: The width of the rectangle.
    :param int height: The height of the rectangle.
    :param int|None fill: The color to fill the rectangle. Can be a hex value for a color or
                    ``None`` for transparent.
    :param int|None outline: The outline of the rectangle. Can be a hex value for a color or
                    ``None`` for no outline.
    :param int stroke: Used for the outline. Will not change the outer bound size set by ``width``
                    and ``height``.

    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        *,
        fill: Optional[int] = None,
        outline: Optional[int] = None,
        stroke: int = 1,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Rectangle dimensions must be larger than 0.")

        self._palette = displayio.Palette(2)
        self._palette.make_transparent(_FILL)
        self._palette.make_transparent(_OUTLINE)

        if HAS_VECTORIO:
            # vectorio draws the fill and the outline itself, and takes the outline width and
            # both colors from the palette.
            super().__init__(
                pixel_shader=self._palette,
                width=width,
                height=height,
                x=x,
                y=y,
                # vectorio allows at most half the shortest side; the bitmap path filled
                # the shape with the outline color when the stroke was wider than that.
                outline_width=min(stroke, min(width, height) // 2),
                outline_color_index=_OUTLINE if outline is not None else None,
            )
        else:
            self._bitmap = displayio.Bitmap(width, height, 2)
            if outline is not None:
                for w in range(width):
                    for line in range(stroke):
                        self._bitmap[w, line] = _OUTLINE
                        self._bitmap[w, height - 1 - line] = _OUTLINE
                for h in range(height):
                    for line in range(stroke):
                        self._bitmap[line, h] = _OUTLINE
                        self._bitmap[width - 1 - line, h] = _OUTLINE
            super().__init__(self._bitmap, pixel_shader=self._palette, x=x, y=y)

        self.fill = fill
        self.outline = outline

    @property
    def fill(self) -> Optional[int]:
        """The fill of the rectangle. Can be a hex value for a color or ``None`` for
        transparent."""
        return get_color(self._palette, _FILL)

    @fill.setter
    def fill(self, color: Optional[int]) -> None:
        set_color(self._palette, _FILL, color)

    @property
    def outline(self) -> Optional[int]:
        """The outline of the rectangle. Can be a hex value for a color or ``None``
        for no outline."""
        return get_color(self._palette, _OUTLINE)

    @outline.setter
    def outline(self, color: Optional[int]) -> None:
        set_color(self._palette, _OUTLINE, color)

    if not HAS_VECTORIO:
        # A vectorio shape can be resized, so it answers width and height itself. A bitmap
        # can't be, so these stay read only there.

        @property
        def width(self) -> int:
            """
            :return: the width of the rectangle in pixels
            """
            return self._bitmap.width

        @property
        def height(self) -> int:
            """
            :return: the height of the rectangle in pixels
            """
            return self._bitmap.height
