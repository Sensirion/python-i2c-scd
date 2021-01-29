Quick Start
===========

SensorBridge Example
--------------------

Following example code shows how to use this driver with a Sensirion SCD41
connected to the computer using a `Sensirion SEK-SensorBridge`_. The driver
for the SensorBridge can be installed with

.. sourcecode:: bash

    pip install sensirion-shdlc-sensorbridge


.. sourcecode:: python

    import time
    from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
    from sensirion_shdlc_sensorbridge import SensorBridgePort, \
        SensorBridgeShdlcDevice, SensorBridgeI2cProxy
    from sensirion_i2c_driver import I2cConnection
    from sensirion_i2c_scd import Scd4xI2cDevice

    # Connect to the SensorBridge with default settings:
    #  - baudrate:      460800
    #  - slave address: 0
    with ShdlcSerialPort(port='COM1', baudrate=460800) as port:
        bridge = SensorBridgeShdlcDevice(ShdlcConnection(port), slave_address=0)
        print("SensorBridge SN: {}".format(bridge.get_serial_number()))

        # Configure SensorBridge port 1 for SCD4x
        bridge.set_i2c_frequency(SensorBridgePort.ONE, frequency=100e3)
        bridge.set_supply_voltage(SensorBridgePort.ONE, voltage=3.3)
        bridge.switch_supply_on(SensorBridgePort.ONE)

        # Create SCD41 device
        i2c_transceiver = SensorBridgeI2cProxy(bridge, port=SensorBridgePort.ONE)
        scd41 = Scd4xI2cDevice(I2cConnection(i2c_transceiver))

        # start periodic measurement in high power mode
        scd41.start_periodic_measurement()

        # Measure every 5 seconds
        while True:
            time.sleep(5)
            co2, temperature, humidity = scd41.read_measurement()
            # use default formatting for printing output:
            print("{}, {}, {}".format(co2, temperature, humidity))
            # custom printing of attributes:
            print("{:d} ppm CO2, {:0.2f} °C ({} ticks), {:0.1f} %RH ({} ticks)".format(
                co2.co2,
                temperature.degrees_celsius, temperature.ticks,
                humidity.percent_rh, humidity.ticks))
        scd41.stop_periodic_measurement()


.. _Sensirion SEK-SensorBridge: https://www.sensirion.com/sensorbridge/
