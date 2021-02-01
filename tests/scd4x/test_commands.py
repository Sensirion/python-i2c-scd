# -*- coding: utf-8 -*-
# (c) Copyright 2020 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function

import pytest
import time

from sensirion_i2c_driver.errors import I2cNackError

from sensirion_i2c_scd.scd4x.data_types import Scd4xPowerMode
from sensirion_i2c_scd.scd4x.response_types import Scd4xTemperature, Scd4xHumidity, Scd4xCarbonDioxide, \
    Scd4xTemperatureOffset


@pytest.mark.needs_device
@pytest.mark.needs_scd4x
@pytest.mark.parametrize("power_mode", [
    Scd4xPowerMode.HIGH,
    Scd4xPowerMode.LOW,
])
def test_periodic_measurement(scd4x, power_mode):
    """
    Test periodic measurement in high and low power mode
    """
    scd4x.start_periodic_measurement(power_mode)
    while not scd4x.get_data_ready_status():
        # wait until data is ready to be read out
        time.sleep(1)
    co2, t, rh = scd4x.read_measurement()
    scd4x.stop_periodic_measurement()

    assert type(co2) is Scd4xCarbonDioxide
    assert type(co2.ticks) is int
    assert type(t) is Scd4xTemperature
    assert type(t.ticks) is int
    assert type(rh) is Scd4xHumidity
    assert type(rh.ticks) is int


@pytest.mark.needs_device
@pytest.mark.needs_scd4x
def test_get_temperature_offset(scd4x):
    """
    Test reading temperature offset
    """
    t_offset = scd4x.get_temperature_offset()
    assert type(t_offset) is Scd4xTemperatureOffset
    assert type(t_offset.ticks) is int
    assert type(t_offset.degrees_celsius) is float


@pytest.mark.needs_device
@pytest.mark.needs_scd4x
@pytest.mark.parametrize("expected_offset", [
    3.0,
    3.5,
    4.0
])
def test_set_temperature_offset(scd4x, expected_offset):
    """
    Test set temperature offset to different values
    """
    scd4x.set_temperature_offset(expected_offset)
    offset = scd4x.get_temperature_offset()

    assert round(offset.degrees_celsius, 1) == expected_offset


@pytest.mark.needs_device
@pytest.mark.needs_scd4x
def test_get_sensor_altitude(scd4x):
    """
    Test get sensor altitude in meters above sea level
    """
    altitude = scd4x.get_sensor_altitude()
    assert type(altitude) is int


@pytest.mark.needs_device
@pytest.mark.needs_scd4x
@pytest.mark.parametrize("expected_altitude", [
    200,
    500,
    700,
])
def test_set_sensor_altitude(scd4x, expected_altitude):
    """
    Test set sensor altitude in meters above sea level
    """
    original_altitude = scd4x.get_sensor_altitude()
    scd4x.set_sensor_altitude(expected_altitude)
    altitude = scd4x.get_sensor_altitude()
    assert altitude == expected_altitude
    scd4x.set_sensor_altitude(original_altitude)


@pytest.mark.needs_device
@pytest.mark.needs_scd4x
def test_get_automatic_self_calibration(scd4x):
    """
    Test get ASC value
    """
    asc = scd4x.get_automatic_self_calibration()
    assert type(asc) is bool


@pytest.mark.needs_device
@pytest.mark.needs_scd4x
@pytest.mark.parametrize("expected_asc", [
    False,
    True,
])
def test_set_automatic_self_calibration(scd4x, expected_asc):
    """
    Test get ASC value
    """
    scd4x.set_automatic_self_calibration(expected_asc)
    asc = scd4x.get_automatic_self_calibration()
    assert asc == expected_asc


@pytest.mark.needs_device
@pytest.mark.needs_scd4x
def test_measure_single_shot(scd4x):
    """
    Test measure co2, relative humidity and temperature as single shot measurement from idle mode
    """
    scd4x.measure_single_shot()
    co2, t, rh = scd4x.read_measurement()
    assert type(co2) is Scd4xCarbonDioxide
    assert type(t) is Scd4xTemperature
    assert type(rh) is Scd4xHumidity


@pytest.mark.needs_device
@pytest.mark.needs_scd4x
def test_measure_single_shot_rht_only(scd4x):
    """
    Test measure relative humidity and temperature as single shot measurement from idle mode
    """
    scd4x.measure_single_shot_rht_only()
    co2, t, rh = scd4x.read_measurement()
    assert type(co2) is Scd4xCarbonDioxide
    assert type(t) is Scd4xTemperature
    assert type(rh) is Scd4xHumidity


@pytest.mark.needs_device
@pytest.mark.needs_scd4x
def test_sleep_mode(scd4x):
    """
    Test power down and wake up commands
    """
    scd4x.power_down()
    try:
        scd4x.get_data_ready_status()
    except I2cNackError:
        assert True
    else:
        assert False, "SCD4x should respond with NACK when in sleep mode"
    scd4x.wake_up()
    try:
        scd4x.get_data_ready_status()
    except I2cNackError:
        assert False, "SCD4x should respond after wake up"
    else:
        assert True
