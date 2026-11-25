# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`roundrect`
================================================================================

A slightly modified version of Adafruit_CircuitPython_Display_Shapes that includes
an explicit call to palette.make_opaque() in the fill color setter function.

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
    # No vectorio shape styles on this firmware, so the shape is drawn into a bitmap.
    from displayio import TileGrid as _Rectangle

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Shapes.git"

# A bitmap needs one entry that means "nothing here", so its fill moves to entry 2. vectorio
# shapes draw the fill and the outline with two entries and no background.
_FILL = 0 if HAS_VECTORIO else 2
_OUTLINE = 1


class RoundRect(_Rectangle):
    """A round-corner rectangle.

    The rectangle is drawn with :py:mod:`vectorio` when the firmware has it, which needs no
    bitmap and draws the corners on the GPU where the display has one. Older firmware builds
    a bitmap instead.

    :param int x: The x-position of the top left corner.
    :param int y: The y-position of the top left corner.
    :param int width: The width of the rounded-corner rectangle.
    :param int height: The height of the rounded-corner rectangle.
    :param int r: The radius of the rounded corner.
    :param int|None fill: The color to fill the rounded-corner rectangle. Can be a hex value
                    for a color or ``None`` for transparent.
    :param int|None outline: The outline of the rounded-corner rectangle. Can be a hex value
                    for a color or ``None`` for no outline.
    :param int stroke: Used for the outline. Will not change the outer bound size set by ``width``
                    and ``height``.

    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        r: int,
        *,
        fill: Optional[int] = None,
        outline: Optional[int] = None,
        stroke: int = 1,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Rectangle dimensions must be larger than 0.")
        if r > width / 2 or r > height / 2:
            raise ValueError("Radius cannot exceed half of the smaller side (width or height).")

        self._palette = displayio.Palette(2 if HAS_VECTORIO else 3)
        self._palette.make_transparent(0)
        self._palette.make_transparent(_FILL)
        self._palette.make_transparent(_OUTLINE)

        if HAS_VECTORIO:
            # vectorio clamps the radius to half of the shortest side itself, and draws the
            # corner and the outline inside the rectangle's bounds.
            super().__init__(
                pixel_shader=self._palette,
                width=width,
                height=height,
                x=x,
                y=y,
                radius=r,
                # vectorio allows at most half the shortest side; the bitmap path filled
                # the shape with the outline color when the stroke was wider than that.
                outline_width=min(stroke, min(width, height) // 2),
                outline_color_index=_OUTLINE if outline is not None else None,
            )
        else:
            self._r = r
            self._bitmap = displayio.Bitmap(width, height, 3)
            for i in range(0, width):  # draw the center chunk
                for j in range(r, height - r):  # draw the center chunk
                    self._bitmap[i, j] = _FILL
            self._helper(
                r,
                r,
                r,
                color=_FILL,
                fill=True,
                x_offset=width - 2 * r - 1,
                y_offset=height - 2 * r - 1,
            )

            if outline is not None:
                # draw flat sides
                for w in range(r, width - r):
                    for line in range(stroke):
                        self._bitmap[w, line] = _OUTLINE
                        self._bitmap[w, height - line - 1] = _OUTLINE
                for _h in range(r, height - r):
                    for line in range(stroke):
                        self._bitmap[line, _h] = _OUTLINE
                        self._bitmap[width - line - 1, _h] = _OUTLINE
                # draw round corners
                self._helper(
                    r,
                    r,
                    r,
                    color=_OUTLINE,
                    stroke=stroke,
                    x_offset=width - 2 * r - 1,
                    y_offset=height - 2 * r - 1,
                )
            super().__init__(self._bitmap, pixel_shader=self._palette, x=x, y=y)

        self.fill = fill
        self.outline = outline

    def _helper(
        self,
        x0: int,
        y0: int,
        r: int,
        *,
        color: int,
        x_offset: int = 0,
        y_offset: int = 0,
        stroke: int = 1,
        corner_flags: int = 0xF,
        fill: bool = False,
    ) -> None:
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r

        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            if corner_flags & 0x8:
                if fill:
                    for w in range(x0 - y, x0 + y + x_offset):
                        self._bitmap[w, y0 + x + y_offset] = color
                    for w in range(x0 - x, x0 + x + x_offset):
                        self._bitmap[w, y0 + y + y_offset] = color
                else:
                    for line in range(stroke):
                        self._bitmap[x0 - y + line, y0 + x + y_offset] = color
                        self._bitmap[x0 - x, y0 + y + y_offset - line] = color
            if corner_flags & 0x1:
                if fill:
                    for w in range(x0 - y, x0 + y + x_offset):
                        self._bitmap[w, y0 - x] = color
                    for w in range(x0 - x, x0 + x + x_offset):
                        self._bitmap[w, y0 - y] = color
                else:
                    for line in range(stroke):
                        self._bitmap[x0 - y + line, y0 - x] = color
                        self._bitmap[x0 - x, y0 - y + line] = color
            if corner_flags & 0x4:
                for line in range(stroke):
                    self._bitmap[x0 + x + x_offset, y0 + y + y_offset - line] = color
                    self._bitmap[x0 + y + x_offset - line, y0 + x + y_offset] = color
            if corner_flags & 0x2:
                for line in range(stroke):
                    self._bitmap[x0 + x + x_offset, y0 - y + line] = color
                    self._bitmap[x0 + y + x_offset - line, y0 - x] = color

    @property
    def fill(self) -> Optional[int]:
        """The fill of the rounded-corner rectangle. Can be a hex value for a color or ``None`` for
        transparent."""
        return get_color(self._palette, _FILL)

    @fill.setter
    def fill(self, color: Optional[int]) -> None:
        set_color(self._palette, _FILL, color)

    @property
    def outline(self) -> Optional[int]:
        """The outline of the rounded-corner rectangle. Can be a hex value for a color or ``None``
        for no outline."""
        return get_color(self._palette, _OUTLINE)

    @outline.setter
    def outline(self, color: Optional[int]) -> None:
        set_color(self._palette, _OUTLINE, color)

    if not HAS_VECTORIO:
        # A vectorio shape can be resized and re-rounded, so it answers these itself. A bitmap
        # can't be, so they stay read only there.

        @property
        def width(self) -> int:
            """
            :return: the width of the rounded rectangle in pixels
            """
            return self._bitmap.width

        @property
        def height(self) -> int:
            """
            :return: the height of the rounded rectangle in pixels
            """
            return self._bitmap.height

        @property
        def radius(self) -> int:
            """
            :return: the radius of the rounded corners in pixels
            """
            return self._r
