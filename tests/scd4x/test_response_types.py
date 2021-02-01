# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_i2c_scd.scd4x.response_types import Scd4xCarbonDioxide, Scd4xTemperature, Scd4xHumidity, \
    Scd4xTemperatureOffset
import pytest


@pytest.mark.parametrize("value", [
    dict({'ticks': 50, 'co2': 50}),
    dict({'ticks': 834, 'co2': 834}),
])
def test_co2(value):
    """
    Test if the CO2() type works as expected for different values.
    """
    result = Scd4xCarbonDioxide(value.get('ticks'))
    assert type(result) is Scd4xCarbonDioxide
    assert type(result.ticks) is int
    assert result.ticks == value.get('ticks')
    assert type(result.co2) is int
    assert result.co2 == value.get('co2')


@pytest.mark.parametrize("value", [
    dict({'ticks': 0, 'degrees_celsius': -45., 'degrees_fahrenheit': -49.}),
    dict(
        {'ticks': 65536, 'degrees_celsius': 130., 'degrees_fahrenheit': 266.}),
])
def test_temperature(value):
    """
    Test if the Temperature() type works as expected for different values.
    """
    result = Scd4xTemperature(value.get('ticks'))
    assert type(result) is Scd4xTemperature
    assert type(result.ticks) is int
    assert result.ticks == value.get('ticks')
    assert type(result.degrees_celsius) is float
    assert result.degrees_celsius == value.get('degrees_celsius')
    assert type(result.degrees_fahrenheit) is float
    assert result.degrees_fahrenheit == value.get('degrees_fahrenheit')


@pytest.mark.parametrize("value", [
    dict({'ticks': 0, 'percent_rh': 0.}),
    dict({'ticks': 65536, 'percent_rh': 100.}),
])
def test_humidity(value):
    """
    Test if the Humidity() type works as expected for different values.
    """
    result = Scd4xHumidity(value.get('ticks'))
    assert type(result) is Scd4xHumidity
    assert type(result.ticks) is int
    assert result.ticks == value.get('ticks')
    assert type(result.percent_rh) is float
    assert result.percent_rh == value.get('percent_rh')


@pytest.mark.parametrize("value", [
    dict({'ticks': 0, 'degrees_celsius': 0, 'degrees_fahrenheit': 32.}),
    dict(
        {'ticks': 65536, 'degrees_celsius': 175., 'degrees_fahrenheit': 347.}),
])
def test_temperature_offset(value):
    """
    Test if the TemperatureOffset() type works as expected for different values.
    """
    result = Scd4xTemperatureOffset(value.get('ticks'))
    assert type(result) is Scd4xTemperatureOffset
    assert type(result.ticks) is int
    assert result.ticks == value.get('ticks')
    assert type(result.degrees_celsius) is float
    assert result.degrees_celsius == value.get('degrees_celsius')
    assert type(result.degrees_fahrenheit) is float
    assert result.degrees_fahrenheit == value.get('degrees_fahrenheit')
