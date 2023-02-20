#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2023 Sensirion AG, Switzerland

import time
import argparse
from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection
from sensirion_i2c_scd import Scd4xI2cDevice

parser = argparse.ArgumentParser()
parser.add_argument('--i2c-port', '-p', default='/dev/i2c-1')
args = parser.parse_args()

# Connect to the I²C 1 port
with LinuxI2cTransceiver(args.i2c_port) as i2c_transceiver:
    # Create SCD4x device
    scd4x = Scd4xI2cDevice(I2cConnection(i2c_transceiver))

    # Make sure measurement is stopped, else we can't read serial number or
    # start a new measurement
    scd4x.stop_periodic_measurement()

    print("scd4x Serial Number: {}".format(scd4x.read_serial_number()))

    scd4x.start_periodic_measurement()

    # Measure every 5 seconds for 5 minute
    for _ in range(60):
        time.sleep(5)
        co2, temperature, humidity = scd4x.read_measurement()
        # use default formatting for printing output:
        print("{}, {}, {}".format(co2, temperature, humidity))
