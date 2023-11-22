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
        direction = direction - angle / 2
        # create outer points
        points = []
        for i in range(segments + 1):
            alpha = (i * angle / segments + direction) / 180 * math.pi
            x0 = int(radius * math.cos(alpha))
            y0 = -int(radius * math.sin(alpha))
            points.append((x0, y0))

        # create inner points
        if arc_width > 1:
            for i in range(segments, -1, -1):
                alpha = (i * angle / segments + direction) / 180 * math.pi
                x0 = int((radius - arc_width) * math.cos(alpha))
                y0 = -int((radius - arc_width) * math.sin(alpha))
                points.append((x0, y0))

        # create polygon(s) and add to ourselves
        if arc_width > 1 and HAVE_VECTORIO and fill is not None:
            palette = displayio.Palette(1)
            palette[0] = fill
            self.append(vectorio.Polygon(pixel_shader=palette, points=points, x=0, y=0))
        if outline is not None:
            self.append(Polygon(points, outline=outline, colors=1, close=arc_width > 1))
