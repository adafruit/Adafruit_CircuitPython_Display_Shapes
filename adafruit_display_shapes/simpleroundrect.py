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
    def __init__(self, x, y, width, height, radius=0, fill=0xFF0000):

        # the palette and shpae can only be stored after __init__
        palette = displayio.Palette(2)
        shape = displayio.Shape(
            width,
            height,
            # mirror_x and mirror_y are False until a core displayio bug is fixed
            mirror_x=False,
            mirror_y=False,
        )
        super().__init__(shape, pixel_shader=palette, x=x, y=y)

        # configure the color and palette
        palette.make_transparent(0)
        palette[1] = fill

        # these them so fill can be adjusted later
        self._palette = palette
        self._shape = shape

        # clip a too large radius to the max allowed
        radius = min(radius, width // 2, height // 2)

        # calculate and apply the radius row by row
        rsqrd = radius ** 2
        for row_offset in range(0, radius):
            left_indent = radius - round(math.sqrt(rsqrd - (row_offset - radius) ** 2))
            right_indent = width - left_indent - 1

            shape.set_boundary(row_offset, left_indent, right_indent)
            shape.set_boundary(height - row_offset - 1, left_indent, right_indent)

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
            self._palette.make_transparent(0)
        else:
            self._palette.make_opaque(0)
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
