# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_i2c_scd.scd4x.data_types import Scd4xTemperatureOffsetDegC
import pytest


@pytest.mark.parametrize("value", [
    dict({'ticks': 0, 'degrees_celsius': 0, 'degrees_fahrenheit': 32.}),
    dict(
        {'ticks': 65536, 'degrees_celsius': 175., 'degrees_fahrenheit': 347.}),
])
def test_temperature_offset_degc(value):
    """
    Test if the TemperatureOffset() type works as expected for different values.
    """
    result = Scd4xTemperatureOffsetDegC(value.get('degrees_celsius'))
    assert type(result) is Scd4xTemperatureOffsetDegC
    assert type(result.ticks) is int
    assert result.ticks == value.get('ticks')
    assert type(result.degrees_celsius) is float
    assert result.degrees_celsius == value.get('degrees_celsius')
    assert type(result.degrees_fahrenheit) is float
    assert result.degrees_fahrenheit == value.get('degrees_fahrenheit')
