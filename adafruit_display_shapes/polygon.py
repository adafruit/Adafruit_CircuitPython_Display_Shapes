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
    # pylint: disable=too-many-arguments,invalid-name
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
        if close:
            points.append(points[0])

        xs = []
        ys = []

        for point in points:
            xs.append(point[0])
            ys.append(point[1])

        x_offset = min(xs)
        y_offset = min(ys)

        # Find the largest and smallest X values to figure out width for bitmap
        width = max(xs) - min(xs) + 1
        height = max(ys) - min(ys) + 1

        self._palette = displayio.Palette(colors + 1)
        self._palette.make_transparent(0)
        self._bitmap = displayio.Bitmap(width, height, colors + 1)

        if outline is not None:
            # print("outline")
            self.outline = outline
            for index, _ in enumerate(points[:-1]):
                point_a = points[index]
                point_b = points[index + 1]
                self._line(
                    point_a[0] - x_offset,
                    point_a[1] - y_offset,
                    point_b[0] - x_offset,
                    point_b[1] - y_offset,
                    self._OUTLINE,
                )

        super().__init__(
            self._bitmap, pixel_shader=self._palette, x=x_offset, y=y_offset
        )

    # pylint: disable=invalid-name, too-many-locals, too-many-branches
    def _line(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: int,
    ) -> None:
        if x0 == x1:
            if y0 > y1:
                y0, y1 = y1, y0
            for _h in range(y0, y1 + 1):
                self._bitmap[x0, _h] = color
        elif y0 == y1:
            if x0 > x1:
                x0, x1 = x1, x0
            for _w in range(x0, x1 + 1):
                self._bitmap[_w, y0] = color
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
                    self._bitmap[y0, x] = color
                else:
                    self._bitmap[x, y0] = color
                err -= dy
                if err < 0:
                    y0 += ystep
                    err += dx

    # pylint: enable=invalid-name, too-many-locals, too-many-branches

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
