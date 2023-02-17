#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2023 Sensirion AG, Switzerland

import time
import argparse
from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
from sensirion_shdlc_sensorbridge import SensorBridgePort, \
    SensorBridgeShdlcDevice, SensorBridgeI2cProxy
from sensirion_i2c_driver import I2cConnection
from sensirion_i2c_scd import Scd4xI2cDevice

parser = argparse.ArgumentParser()
parser.add_argument('--serial-port', '-p', default='COM1')
args = parser.parse_args()

# Connect to the SensorBridge with default settings:
#  - baudrate:      460800
#  - slave address: 0
with ShdlcSerialPort(port=args.serial_port, baudrate=460800) as port:
    bridge = SensorBridgeShdlcDevice(ShdlcConnection(port), slave_address=0)
    print("SensorBridge SN: {}".format(bridge.get_serial_number()))

    # Configure SensorBridge port 1 for SCD4x
    bridge.set_i2c_frequency(SensorBridgePort.ONE, frequency=100e3)
    bridge.set_supply_voltage(SensorBridgePort.ONE, voltage=3.3)
    bridge.switch_supply_on(SensorBridgePort.ONE)

    # Create SCD4x device
    i2c_transceiver = SensorBridgeI2cProxy(bridge, port=SensorBridgePort.ONE)
    scd4x = Scd4xI2cDevice(I2cConnection(i2c_transceiver))

    # Make sure measurement is stopped, else we can't read serial number or
    # start a new measurement
    scd4x.stop_periodic_measurement()

    print("scd4x Serial Number: {}".format(scd4x.read_serial_number()))

    # start periodic measurement in high power mode
    scd4x.start_periodic_measurement()

    # Measure every 5 seconds for 5 minute
    for _ in range(60):
        time.sleep(5)
        co2, temperature, humidity = scd4x.read_measurement()
        # use default formatting for printing output:
        print("{}, {}, {}".format(co2, temperature, humidity))
        # custom printing of attributes:
        print("{:d} ppm CO2, {:0.2f} °C ({} ticks), {:0.1f} %RH ({} ticks)".format(
            co2.co2,
            temperature.degrees_celsius, temperature.ticks,
            humidity.percent_rh, humidity.ticks))
    scd4x.stop_periodic_measurement()
