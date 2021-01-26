# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from enum import IntEnum


class Scd4xPowerMode(IntEnum):
    """
    An enum containing all available power mode settings for the
    co2 measurements.

    .. note: The power mode setting influences the measurement
             interval and thus the overall energy consumption of the sensor.
             Check the datasheet for further information.
    """
    HIGH = 1    #: High power mode measures every 5 seconds
    LOW = 2     #: Low power mode measures every 30 seconds


class Scd4xTemperatureOffsetDegC(object):
    """
    Represents a temperature offset in degree celsius.

    With the :py:attr:`ticks` you can access the raw data as sent to the
    device. For the converted values you can choose between
    :py:attr:`degrees_celsius` and :py:attr:`degrees_fahrenheit`.

    :param int degree_celsius:
        The temperature as degree celsius
    """
    def __init__(self, degree_celsius):
        """
        Creates an instance from the received raw data.
        """

        #: The converted temperature offset in °C.
        self.degrees_celsius = float(degree_celsius)

        #: The converted temperature offset in °F.
        self.degrees_fahrenheit = 32. + (self.degrees_celsius * 9. / 5.)

        #: The ticks (int) as received from the device.
        self.ticks = int(round(self.degrees_celsius * 65536. / 175.))

    def __str__(self):
        return '{:0.1f} °C'.format(self.degrees_celsius)
