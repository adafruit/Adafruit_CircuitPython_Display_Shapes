# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`polygon`
================================================================================

Various common shapes for use with displayio - Polygon shape!


* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

try:
    from typing import Optional, List, Tuple
except ImportError:
    pass

import displayio

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Shapes.git"


class Polygon(displayio.TileGrid):
    """A polygon.

    :param list points: A list of (x, y) tuples of the points
    :param int|None outline: The outline of the polygon. Can be a hex value for a color or
                    ``None`` for no outline.
    :param bool close: (Optional) Wether to connect first and last point. (True)
    :param int colors: (Optional) Number of colors to use. Most polygons would use two, one for
                    outline and one for fill. If you're not filling your polygon, set this to 1
                    for smaller memory footprint. (2)
    """

    _OUTLINE = 1
    _FILL = 2

    def __init__(
        self,
        points: List[Tuple[int, int]],
        *,
        outline: Optional[int] = None,
        close: Optional[bool] = True,
        colors: Optional[int] = 2,
    ) -> None:
        (xs, ys) = zip(*points)

        x_offset = min(xs)
        y_offset = min(ys)

        # Find the largest and smallest X values to figure out width for bitmap
        width = max(xs) - min(xs) + 1
        height = max(ys) - min(ys) + 1

        self._palette = displayio.Palette(colors + 1)
        self._palette.make_transparent(0)
        self._bitmap = displayio.Bitmap(width, height, colors + 1)

        shifted = [(x - x_offset, y - y_offset) for (x, y) in points]

        if outline is not None:
            self.outline = outline
            self.draw(self._bitmap, shifted, self._OUTLINE, close)

        super().__init__(
            self._bitmap, pixel_shader=self._palette, x=x_offset, y=y_offset
        )

    @staticmethod
    def draw(
        bitmap: displayio.Bitmap,
        points: List[Tuple[int, int]],
        color_id: int,
        close: Optional[bool] = True,
    ) -> None:
        """Draw a polygon conecting points on provided bitmap with provided color_id

        :param displayio.Bitmap bitmap: bitmap to draw on
        :param list points: A list of (x, y) tuples of the points
        :param int color_id: Color to draw with
        :param bool close: (Optional) Wether to connect first and last point. (True)
        """

        if close:
            points.append(points[0])

        for index in range(len(points) - 1):
            Polygon._line_on(bitmap, points[index], points[index + 1], color_id)

    def _line(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: int,
    ) -> None:
        self._line_on(self._bitmap, (x0, y0), (x1, y1), color)

    @staticmethod
    def _line_on(
        bitmap: displayio.Bitmap,
        p0: Tuple[int, int],
        p1: Tuple[int, int],
        color: int,
    ) -> None:
        (x0, y0) = p0
        (x1, y1) = p1
        if x0 == x1:
            if y0 > y1:
                y0, y1 = y1, y0
            for _h in range(y0, y1 + 1):
                bitmap[x0, _h] = color
        elif y0 == y1:
            if x0 > x1:
                x0, x1 = x1, x0
            for _w in range(x0, x1 + 1):
                bitmap[_w, y0] = color
        else:
            steep = abs(y1 - y0) > abs(x1 - x0)
            if steep:
                x0, y0 = y0, x0
                x1, y1 = y1, x1

            if x0 > x1:
                x0, x1 = x1, x0
                y0, y1 = y1, y0

            dx = x1 - x0
            dy = abs(y1 - y0)

            err = dx / 2

            if y0 < y1:
                ystep = 1
            else:
                ystep = -1

            for x in range(x0, x1 + 1):
                if steep:
                    bitmap[y0, x] = color
                else:
                    bitmap[x, y0] = color
                err -= dy
                if err < 0:
                    y0 += ystep
                    err += dx

    @property
    def outline(self) -> Optional[int]:
        """The outline of the polygon. Can be a hex value for a color or
        ``None`` for no outline."""
        return self._palette[self._OUTLINE]

    @outline.setter
    def outline(self, color: Optional[int]) -> None:
        if color is None:
            self._palette[self._OUTLINE] = 0
            self._palette.make_transparent(self._OUTLINE)
        else:
            self._palette[self._OUTLINE] = color
            self._palette.make_opaque(self._OUTLINE)
