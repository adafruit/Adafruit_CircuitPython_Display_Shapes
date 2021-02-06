# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`simpleroundrect`
================================================================================

A slightly modified version of Adafruit_CircuitPython_Display_Shapes that includes
an explicit call to palette.make_opaque() in the fill color setter function.

"""

import math
import displayio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Shapes.git"


class SimpleRoundRect(displayio.TileGrid):
    # pylint: disable=too-many-arguments
    """A round-corner rectangle with lower memory usage than RoundRect. All the corners
        have the same radius and no outline.

    :param x: The x-position of the top left corner.
    :param y: The y-position of the top left corner.
    :param width: The width of the rounded-corner rectangle.
    :param height: The height of the rounded-corner rectangle.
    :param radius: The radius of the rounded corner.
    :param fill: The color to fill the rounded-corner rectangle. Can be a hex value for a color or
                 ``None`` for transparent.
    """

    def __init__(self, x, y, width, height, radius=0, fill=0xFF0000):

        # the palette and shpae can only be stored after __init__
        palette = displayio.Palette(2)
        shape = displayio.Shape(
            width,
            height,
            # mirror_x is False due to a core displayio bug
            mirror_x=False,
            mirror_y=True,
        )
        super().__init__(shape, pixel_shader=palette, x=x, y=y)

        # configure the color and palette
        palette.make_transparent(0)
        palette[1] = fill

        # these them so fill can be adjusted later
        self._palette = palette
        self._shape = shape

        # clip a too large radius to the max allowed
        radius = min(radius, round(width / 2), round(height / 2))

        # calculate and apply the radius row by row
        rsqrd = radius ** 2
        for row_offset in range(0, radius):
            left_indent = radius - int(math.sqrt(rsqrd - (row_offset - radius) ** 2))
            right_indent = width - left_indent - 1

            shape.set_boundary(
                row_offset,
                left_indent,
                right_indent,
            )

        # store for read only access later
        self._radius = radius
        self._width = width
        self._height = height

    @property
    def fill(self):
        return self._palette[1]

    @fill.setter
    def fill(self, value):
        if value is None:
            self._palette.make_transparent(1)
        else:
            self._palette.make_opaque(1)
            self._palette[1] = value

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def radius(self):
        return self._radius
