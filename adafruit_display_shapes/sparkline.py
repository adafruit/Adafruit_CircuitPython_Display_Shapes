# SPDX-FileCopyrightText: 2020 Kevin Matocha
#
# SPDX-License-Identifier: MIT

# class of sparklines in CircuitPython

# See the bottom for a code example using the `sparkline` Class.

# # File: display_shapes_sparkline.py
# A sparkline is a scrolling line graph, where any values added to sparkline using `
# add_value` are plotted.
#
# The `sparkline` class creates an element suitable for adding to the display using
# `display.show(mySparkline)`
# or adding to a `displayio.Group` to be displayed.
#
# When creating the sparkline, identify the number of `max_items` that will be
# included in the graph. When additional elements are added to the sparkline and
# the number of items has exceeded max_items, any excess values are removed from
# the left of the graph, and new values are added to the right.
"""
`sparkline`
================================================================================

Various common shapes for use with displayio - Sparkline!


* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

# pylint: disable=too-many-instance-attributes

try:
    from typing import Optional, List
except ImportError:
    pass
import displayio
from adafruit_display_shapes.polygon import Polygon


class _CyclicBuffer:
    def __init__(self, size: int) -> None:
        self._buffer = [None] * size
        self._start = 0  # between 0 and size-1
        self._end = 0  # between 0 and 2*size-1

    def push(self, value: float) -> None:
        """Pushes value at the end of the buffer.

        :param float value: value to be pushed

        """

        if self.len() == len(self._buffer):
            raise RuntimeError("Trying to push to full buffer")
        self._buffer[self._end % len(self._buffer)] = value
        self._end += 1

    def pop(self) -> float:
        """Pop value from the start of the buffer and returns it."""

        if self.len() == 0:
            raise RuntimeError("Trying to pop from empty buffer")
        result = self._buffer[self._start]
        self._start += 1
        if self._start == len(self._buffer):
            self._start -= len(self._buffer)
            self._end -= len(self._buffer)
        return result

    def len(self) -> int:
        """Returns count of valid data in the buffer."""

        return self._end - self._start

    def clear(self) -> None:
        """Marks all data as invalid."""

        self._start = 0
        self._end = 0

    def values(self) -> List[float]:
        """Returns valid data from the buffer."""

        if self.len() == 0:
            return []
        start = self._start
        end = self._end % len(self._buffer)
        if start < end:
            return self._buffer[start:end]
        return self._buffer[start:] + self._buffer[:end]


class Sparkline(displayio.TileGrid):
    # pylint: disable=too-many-arguments
    """A sparkline graph.

    :param int width: Width of the sparkline graph in pixels
    :param int height: Height of the sparkline graph in pixels
    :param int max_items: Maximum number of values housed in the sparkline
    :param bool dyn_xpitch: (Optional) Dynamically change xpitch (True)
    :param int|None y_min: Lower range for the y-axis.  Set to None for autorange.
    :param int|None y_max: Upper range for the y-axis.  Set to None for autorange.
    :param int x: X-position on the screen, in pixels
    :param int y: Y-position on the screen, in pixels
    :param int color: Line color, the default value is 0xFFFFFF (WHITE)

    Note: If dyn_xpitch is True (default), the sparkline will allways span
    the complete width. Otherwise, the sparkline will grow when you
    add values. Once the line has reached the full width, the sparkline
    will scroll to the left.
    """

    _LINE_COLOR = 1

    def __init__(
        self,
        width: int,
        height: int,
        max_items: int,
        dyn_xpitch: Optional[bool] = True,  # True = dynamic pitch size
        y_min: Optional[int] = None,  # None = autoscaling
        y_max: Optional[int] = None,  # None = autoscaling
        x: int = 0,
        y: int = 0,
        color: int = 0xFFFFFF,  # line color, default is WHITE
    ) -> None:
        # define class instance variables
        self._max_items = max_items  # maximum number of items in the list
        self._buffer = _CyclicBuffer(self._max_items)
        self.dyn_xpitch = dyn_xpitch
        if not dyn_xpitch:
            self._xpitch = (width - 1) / (self._max_items - 1)
        self.y_min = y_min  # minimum of y-axis (None: autoscale)
        self.y_max = y_max  # maximum of y-axis (None: autoscale)
        self.y_bottom = y_min
        # y_bottom: The actual minimum value of the vertical scale, will be
        # updated if autorange
        self.y_top = y_max
        # y_top: The actual minimum value of the vertical scale, will be
        # updated if autorange
        self._points = []  # _points: all points of sparkline
        colors = 2
        self._palette = displayio.Palette(colors + 1)
        self._palette.make_transparent(0)
        self._palette[self._LINE_COLOR] = color
        self._bitmap = displayio.Bitmap(width, height, colors + 1)

        super().__init__(self._bitmap, pixel_shader=self._palette, x=x, y=y)

    def clear_values(self) -> None:
        """Clears _buffer and removes all lines in the group"""
        self._bitmap.fill(0)
        self._buffer.clear()

    def add_value(self, value: float, update: bool = True) -> None:
        """Add a value to the sparkline.

        :param float value: The value to be added to the sparkline
        :param bool update: trigger recreation of primitives

        Note: when adding multiple values it is more efficient to call
        this method with parameter 'update=False' and then to manually
        call the update()-method
        """

        if value is not None:
            if (
                self._buffer.len() >= self._max_items
            ):  # if list is full, remove the first item
                first = self._buffer.pop()
                # check if boundaries have to be updated
                if self.y_min is None and first == self.y_bottom:
                    self.y_bottom = min(self._buffer.values())
                if self.y_max is None and first == self.y_top:
                    self.y_top = max(self._buffer.values())
            self._buffer.push(value)

            if self.y_min is None:
                self.y_bottom = (
                    value if not self.y_bottom else min(value, self.y_bottom)
                )
            if self.y_max is None:
                self.y_top = value if not self.y_top else max(value, self.y_top)

            if update:
                self.update()

    # pylint: disable=no-else-return
    @staticmethod
    def _xintercept(
        x_1: float,
        y_1: float,
        x_2: float,
        y_2: float,
        horizontal_y: float,
    ) -> Optional[
        int
    ]:  # finds intercept of the line and a horizontal line at horizontalY
        slope = (y_2 - y_1) / (x_2 - x_1)
        b = y_1 - slope * x_1

        if slope == 0 and y_1 != horizontal_y:  # does not intercept horizontalY
            return None
        else:
            xint = (
                horizontal_y - b
            ) / slope  # calculate the x-intercept at position y=horizontalY
            return int(xint)

    def _add_point(
        self,
        x: int,
        value: float,
    ) -> None:
        # Guard for y_top and y_bottom being the same
        if self.y_top == self.y_bottom:
            y = int(0.5 * self.height)
        else:
            y = int(
                (self.height - 1) * (self.y_top - value) / (self.y_top - self.y_bottom)
            )
        self._points.append((x, y))

    def _draw(self) -> None:
        self._bitmap.fill(0)
        Polygon.draw(self._bitmap, self._points, self._LINE_COLOR, close=False)

    # pylint: disable= too-many-branches, too-many-nested-blocks, too-many-locals, too-many-statements

    def update(self) -> None:
        """Update the drawing of the sparkline."""

        # bail out early if we only have a single point
        n_points = self._buffer.len()
        if n_points < 2:
            return

        if self.dyn_xpitch:
            # this is a float, only make int when plotting the line
            xpitch = (self.width - 1) / (n_points - 1)
        else:
            xpitch = self._xpitch

        self._points = []  # remove all points

        for count, value in enumerate(self._buffer.values()):
            if count == 0:
                self._add_point(0, value)
            else:
                x = int(xpitch * count)
                last_x = int(xpitch * (count - 1))

                if (self.y_bottom <= last_value <= self.y_top) and (
                    self.y_bottom <= value <= self.y_top
                ):  # both points are in range, plot the line
                    self._add_point(x, value)

                else:  # at least one point is out of range, clip one or both ends the line
                    if ((last_value > self.y_top) and (value > self.y_top)) or (
                        (last_value < self.y_bottom) and (value < self.y_bottom)
                    ):
                        # both points are on the same side out of range: don't draw anything
                        pass
                    else:
                        xint_bottom = self._xintercept(
                            last_x, last_value, x, value, self.y_bottom
                        )  # get possible new x intercept points
                        xint_top = self._xintercept(
                            last_x, last_value, x, value, self.y_top
                        )  # on the top and bottom of range
                        if (xint_bottom is None) or (
                            xint_top is None
                        ):  # out of range doublecheck
                            pass
                        else:
                            # Initialize the adjusted values as the baseline
                            adj_x = x
                            adj_value = value

                            if value > last_value:  # slope is positive
                                if xint_top <= x:  # top is clipped
                                    adj_x = xint_top
                                    adj_value = self.y_top  # y
                            else:  # slope is negative
                                if xint_bottom <= x:  # bottom is clipped
                                    adj_x = xint_bottom
                                    adj_value = self.y_bottom  # y

                            self._add_point(adj_x, adj_value)

            last_value = value  # store value for the next iteration

        self._draw()

    def values(self) -> List[float]:
        """Returns the values displayed on the sparkline."""

        return self._buffer.values()

    @property
    def width(self) -> int:
        """
        :return: the width of the graph in pixels
        """
        return self._bitmap.width

    @property
    def height(self) -> int:
        """
        :return: the height of the graph in pixels
        """
        return self._bitmap.height
