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
from adafruit_display_shapes.line import Line


class Sparkline(displayio.Group):
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
        self.width = width  # in pixels
        self.height = height  # in pixels
        self.color = color  #
        self._max_items = max_items  # maximum number of items in the list
        self._spark_list = []  # list containing the values
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
        self._redraw = True  # _redraw: redraw primitives
        self._last = []  # _last: last point of sparkline

        super().__init__(x=x, y=y)  # self is a group of lines

    def clear_values(self) -> None:
        """Removes all values from the _spark_list list and removes all lines in the group"""

        for _ in range(len(self)):  # remove all items from the current group
            self.pop()
        self._spark_list = []  # empty the list
        self._redraw = True

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
                len(self._spark_list) >= self._max_items
            ):  # if list is full, remove the first item
                first = self._spark_list.pop(0)
                # check if boundaries have to be updated
                if self.y_min is None and first == self.y_bottom:
                    self.y_bottom = min(self._spark_list)
                if self.y_max is None and first == self.y_top:
                    self.y_top = max(self._spark_list)
                self._redraw = True
            self._spark_list.append(value)

            if self.y_min is None:
                self._redraw = self._redraw or value < self.y_bottom
                self.y_bottom = (
                    value if not self.y_bottom else min(value, self.y_bottom)
                )
            if self.y_max is None:
                self._redraw = self._redraw or value > self.y_top
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

    def _plotline(
        self,
        x_1: int,
        last_value: float,
        x_2: int,
        value: float,
    ) -> None:

        # Guard for y_top and y_bottom being the same
        if self.y_top == self.y_bottom:
            y_2 = int(0.5 * self.height)
            y_1 = int(0.5 * self.height)
        else:
            y_2 = int(self.height * (self.y_top - value) / (self.y_top - self.y_bottom))
            y_1 = int(
                self.height * (self.y_top - last_value) / (self.y_top - self.y_bottom)
            )
        self.append(Line(x_1, y_1, x_2, y_2, self.color))  # plot the line
        self._last = [x_2, value]

    # pylint: disable= too-many-branches, too-many-nested-blocks, too-many-locals, too-many-statements

    def update(self) -> None:
        """Update the drawing of the sparkline."""

        # bail out early if we only have a single point
        n_points = len(self._spark_list)
        if n_points < 2:
            self._last = [0, self._spark_list[0]]
            return

        if self.dyn_xpitch:
            # this is a float, only make int when plotting the line
            xpitch = (self.width - 1) / (n_points - 1)
            self._redraw = True
        else:
            xpitch = self._xpitch

        # only add new segment if redrawing is not necessary
        if not self._redraw:
            # end of last line (last point, read as "x(-1)")
            x_m1 = self._last[0]
            y_m1 = self._last[1]
            # end of new line (new point, read as "x(0)")
            x_0 = int(x_m1 + xpitch)
            y_0 = self._spark_list[-1]
            self._plotline(x_m1, y_m1, x_0, y_0)
            return

        self._redraw = False  # reset, since we now redraw everything
        for _ in range(len(self)):  # remove all items from the current group
            self.pop()

        for count, value in enumerate(self._spark_list):
            if count == 0:
                pass  # don't draw anything for a first point
            else:
                x_2 = int(xpitch * count)
                x_1 = int(xpitch * (count - 1))

                if (self.y_bottom <= last_value <= self.y_top) and (
                    self.y_bottom <= value <= self.y_top
                ):  # both points are in range, plot the line
                    self._plotline(x_1, last_value, x_2, value)

                else:  # at least one point is out of range, clip one or both ends the line
                    if ((last_value > self.y_top) and (value > self.y_top)) or (
                        (last_value < self.y_bottom) and (value < self.y_bottom)
                    ):
                        # both points are on the same side out of range: don't draw anything
                        pass
                    else:
                        xint_bottom = self._xintercept(
                            x_1, last_value, x_2, value, self.y_bottom
                        )  # get possible new x intercept points
                        xint_top = self._xintercept(
                            x_1, last_value, x_2, value, self.y_top
                        )  # on the top and bottom of range
                        if (xint_bottom is None) or (
                            xint_top is None
                        ):  # out of range doublecheck
                            pass
                        else:
                            # Initialize the adjusted values as the baseline
                            adj_x_1 = x_1
                            adj_last_value = last_value
                            adj_x_2 = x_2
                            adj_value = value

                            if value > last_value:  # slope is positive
                                if xint_bottom >= x_1:  # bottom is clipped
                                    adj_x_1 = xint_bottom
                                    adj_last_value = self.y_bottom  # y_1
                                if xint_top <= x_2:  # top is clipped
                                    adj_x_2 = xint_top
                                    adj_value = self.y_top  # y_2
                            else:  # slope is negative
                                if xint_top >= x_1:  # top is clipped
                                    adj_x_1 = xint_top
                                    adj_last_value = self.y_top  # y_1
                                if xint_bottom <= x_2:  # bottom is clipped
                                    adj_x_2 = xint_bottom
                                    adj_value = self.y_bottom  # y_2

                            self._plotline(
                                adj_x_1,
                                adj_last_value,
                                adj_x_2,
                                adj_value,
                            )

            last_value = value  # store value for the next iteration

    def values(self) -> List[float]:
        """Returns the values displayed on the sparkline."""

        return self._spark_list
