# SPDX-FileCopyrightText: 2023 Bernhard Bablok
#
# SPDX-License-Identifier: MIT

"""
`arc`
================================================================================

Various common shapes for use with displayio - Arc shape!


* Author(s): Bernhard Bablok

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

import math
import displayio
from adafruit_display_shapes.polygon import Polygon

try:
    import vectorio

    HAVE_VECTORIO = True
except ImportError:
    HAVE_VECTORIO = False

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Shapes.git"


class Arc(displayio.Group):
    # pylint: disable=too-few-public-methods, invalid-name
    """An arc. Technically, an arc is a Group with one or two polygons.

    An arc is defined by a radius, an angle (in degrees) and a direction (also in
    degrees). The latter is the direction of the midpoint of the arc.

    The direction-parameter uses the layout of polar-coordinates, i.e. zero points
    to the right, 90 to the top, 180 to the left and 270 to the bottom.

    The Arc-class creates the arc as a polygon. The number of segments define
    how round the arc is. There is a memory-tradeoff if the segment-number is
    large.

    :param float radius: The (outer) radius of the arc.
    :param float angle: The angle of the arc in degrees.
    :param float direction: The direction of the middle-point of the arc in degrees (0)
    :param int segments: The number of segments of the arc.
    :param arc_width int: (Optional) The width of the arc. This creates an inner arc as well.
    :param int|None outline: The outline of the arc. Can be a hex value for a color or
                    ``None`` for no outline.
    :param int|None fill: The fill-color of the arc. Can be a hex value for a color or
                    ``None`` for no filling. Ignored if port does not support vectorio.
    """

    def __init__(
        # pylint: disable=too-many-arguments, too-many-locals
        self,
        radius: float,
        angle: float,
        direction: float,
        segments: int,
        *args,
        arc_width: Optional[int] = 1,
        outline: Optional[int] = None,
        fill: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        # shift direction by angle/2
        self._direction = direction - angle / 2
        self._radius = radius
        self._angle = angle
        self._segments = segments
        self._outline = outline
        self._fill = fill
        self._arc_width = arc_width
        self.palette = None
        self.vector_polygon = None
        self.outline_polygon = None

        self._init_arc()

    def _init_arc(self):
        # create outer points
        points = []
        for i in range(self._segments + 1):
            alpha = (i * self._angle / self._segments + self._direction) / 180 * math.pi
            x0 = int(self._radius * math.cos(alpha))
            y0 = -int(self._radius * math.sin(alpha))
            points.append((x0, y0))

        # create inner points
        if self._arc_width > 1:
            for i in range(self._segments, -1, -1):
                alpha = (
                    (i * self._angle / self._segments + self._direction) / 180 * math.pi
                )
                x0 = int((self._radius - self._arc_width) * math.cos(alpha))
                y0 = -int((self._radius - self._arc_width) * math.sin(alpha))
                points.append((x0, y0))

        # create polygon(s) and add to ourselves
        if self._arc_width > 1 and HAVE_VECTORIO and self._fill is not None:
            if self.palette is None:
                self.palette = displayio.Palette(1)
            self.palette[0] = self._fill
            if self.vector_polygon is None:
                self.vector_polygon = vectorio.Polygon(
                    pixel_shader=self.palette, points=points, x=0, y=0
                )
                self.append(self.vector_polygon)
            else:
                self.vector_polygon.points = points

        if self._outline is not None:
            if self.outline_polygon is None:
                self.outline_polygon = Polygon(
                    points, outline=self._outline, colors=1, close=self._arc_width > 1
                )
            else:
                self.remove(self.outline_polygon)
                self.outline_polygon = Polygon(
                    points, outline=self._outline, colors=1, close=self._arc_width > 1
                )
            self.append(self.outline_polygon)

    @property
    def direction(self):
        """Which direction the arc is pointing"""
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value
        self._direction = value - self.angle / 2
        self._init_arc()

    @property
    def radius(self):
        """Radius of the arc"""
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self._init_arc()

    @property
    def angle(self):
        """How wide the curve of the arc is in degrees"""
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self._init_arc()

    @property
    def segments(self):
        """Number of segments of the arc, more segments make smoother
        rounded parts but use more time and memory"""
        return self._segments

    @segments.setter
    def segments(self, value):
        self._segments = value
        self._init_arc()

    @property
    def outline(self):
        """The outline color. None for no outline"""
        return self._outline

    @outline.setter
    def outline(self, value):
        self._outline = value
        self._init_arc()

    @property
    def fill(self):
        """The fill color. None for no fill"""
        return self._fill

    @fill.setter
    def fill(self, value):
        self._fill = value
        self._init_arc()

    @property
    def arc_width(self):
        """The thickness of the arc in pixels"""
        return self._arc_width

    @arc_width.setter
    def arc_width(self, value):
        self._arc_width = value
        self._init_arc()
