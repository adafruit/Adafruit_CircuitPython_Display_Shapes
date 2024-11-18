# SPDX-FileCopyrightText: 2024 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`filled_polygon`
================================================================================

Various common shapes for use with displayio - Polygon that supports
both fill and outline


* Author(s): Bernhard Bablok, Tim Cocks

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
from adafruit_display_shapes.polygon import Polygon

try:
    import vectorio

    HAVE_VECTORIO = True
except ImportError:
    HAVE_VECTORIO = False

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Shapes.git"


class FilledPolygon(displayio.Group):
    # pylint: disable=too-few-public-methods, invalid-name
    """A filled polygon. Technically, an FilledPolygon is a Group with one or two polygons.

    :param list points: A list of (x, y) tuples of the points
    :param int|None outline: The outline of the arc. Can be a hex value for a color or
                    ``None`` for no outline.
    :param int|None fill: The fill-color of the arc. Can be a hex value for a color or
                    ``None`` for no filling. Ignored if port does not support vectorio.
    :param bool close: (Optional) Wether to connect first and last point. (True)
    :param int stroke: Thickness of the outline.

    """

    def __init__(
        self,
        points: List[Tuple[int, int]],
        *,
        outline: Optional[int] = None,
        fill: Optional[int] = None,
        close: Optional[bool] = True,
        stroke: int = 1,
    ) -> None:
        super().__init__()
        self._points = points
        self._outline = outline
        self._fill = fill
        self.close = close
        self.stroke = stroke

        self.palette = None
        self.vector_polygon = None
        self.outline_polygon = None

        self._init_polygon()

    def _init_polygon(self):
        # create polygon(s) and add to ourselves
        if HAVE_VECTORIO and self._fill is not None:
            if self.palette is None:
                self.palette = displayio.Palette(1)
            self.palette[0] = self._fill
            if self.vector_polygon is None:
                self.vector_polygon = vectorio.Polygon(
                    pixel_shader=self.palette, points=self.points, x=0, y=0
                )
                self.append(self.vector_polygon)
            else:
                self.vector_polygon.points = self.points

        if self._outline is not None:
            if self.outline_polygon is None:
                self.outline_polygon = Polygon(
                    self.points,
                    outline=self._outline,
                    colors=1,
                    close=self.close,
                    stroke=self.stroke,
                )
            else:
                self.remove(self.outline_polygon)
                self.outline_polygon = Polygon(
                    self.points,
                    outline=self._outline,
                    colors=1,
                    close=self.close,
                    stroke=self.stroke,
                )
            self.append(self.outline_polygon)

    @property
    def points(self):
        """The points that make up the polygon"""
        return self._points

    @points.setter
    def points(self, points):
        self._points = points
        self._init_polygon()

    @property
    def outline(self):
        """The outline color. None for no outline"""
        return self._outline

    @outline.setter
    def outline(self, value):
        self._outline = value
        self._init_polygon()

    @property
    def fill(self):
        """The fill color. None for no fill"""
        return self._fill

    @fill.setter
    def fill(self, value):
        self._fill = value
        self._init_polygon()
