# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

# flake8: noqa

from __future__ import absolute_import, division, print_function

from struct import pack, unpack

from sensirion_i2c_driver import SensirionI2cCommand, CrcCalculator

from sensirion_i2c_scd.scd4x.response_types import Scd4xHumidity, Scd4xCarbonDioxide, Scd4xTemperature
from sensirion_i2c_scd.scd4x.data_types import Scd4xTemperatureOffsetDegC
from sensirion_i2c_scd.scd4x.response_types import Scd4xTemperatureOffset


class Scd4xI2cCmdBase(SensirionI2cCommand):
    """
    SCD4x I²C base command.
    """

    def __init__(self, command, tx_data, rx_length, read_delay, timeout,
                 post_processing_time=0.0):
        """
        Constructs a new SCD4x I²C command.

        :param int/None command:
            The command ID to be sent to the device. None means that no
            command will be sent, i.e. only ``tx_data`` (if not None) will
            be sent. No CRC is added to these bytes since the command ID
            usually already contains a CRC.
        :param bytes-like/list/None tx_data:
            Bytes to be extended with CRCs and then sent to the I²C device.
            None means that no write header will be sent at all (if ``command``
            is None too). An empty list means to send the write header (even if
            ``command`` is None), but without data following it.
        :param int/None rx_length:
            Number of bytes to be read from the I²C device, including CRC
            bytes. None means that no read header is sent at all. Zero means
            to send the read header, but without reading any data.
        :param float read_delay:
            Delay (in Seconds) to be inserted between the end of the write
            operation and the beginning of the read operation. This is needed
            if the device needs some time to prepare the RX data, e.g. if it
            has to perform a measurement. Set to 0.0 to indicate that no delay
            is needed, i.e. the device does not need any processing time.
        :param float timeout:
            Timeout (in Seconds) to be used in case of clock stretching. If the
            device stretches the clock longer than this value, the transceive
            operation will be aborted with a timeout error. Set to 0.0 to
            indicate that the device will not stretch the clock for this
            command.
        :param float post_processing_time:
            Maximum time in seconds the device needs for post processing of
            this command until it is ready to receive the next command. For
            example after a device reset command, the device might need some
            time until it is ready again. Usually this is 0.0s, i.e. no post
            processing is needed.
        """
        super(Scd4xI2cCmdBase, self).__init__(
            command=command,
            tx_data=tx_data,
            rx_length=rx_length,
            read_delay=read_delay,
            timeout=timeout,
            crc=CrcCalculator(8, 0x31, 0xFF, 0x00),
            command_bytes=2,
            post_processing_time=post_processing_time,
        )


class Scd4xI2cCmdStartPeriodicMeasurement(Scd4xI2cCmdBase):
    """
    Start Periodic Measurement I²C Command

    start periodic measurement, signal update interval is 5 seconds.

    .. note:: This command is only available in idle mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdStartPeriodicMeasurement, self).__init__(
            command=0x21B1,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Scd4xI2cCmdReadMeasurement(Scd4xI2cCmdBase):
    """
    Read Measurement I²C Command

    read sensor output. The measurement data can only be read out once per
    signal update interval as the buffer is emptied upon read-out. If no data
    is available in the buffer, the sensor returns a NACK. To avoid a NACK
    response the get_data_ready_status can be issued to check data status. The
    I2C master can abort the read transfer with a NACK followed by a STOP
    condition after any data byte if the user is not interested in subsequent
    data.

    .. note:: This command is only available in measurement mode. The firmware
              updates the measurement values depending on the measurement mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdReadMeasurement, self).__init__(
            command=0xEC05,
            tx_data=None,
            rx_length=9,
            read_delay=0.001,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return:
            - co2 (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xCarbonDioxid`) -
              CO₂ response object
            - temperature (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xTemperature`) -
              Temperature response object.
            - humidity (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xHumidity`) -
              Humidity response object
        :rtype: tuple
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Scd4xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        co2 = int(unpack(">H", checked_data[0:2])[0])  # uint16
        temperature = int(unpack(">H", checked_data[2:4])[0])  # uint16
        humidity = int(unpack(">H", checked_data[4:6])[0])  # uint16
        return Scd4xCarbonDioxide(co2), Scd4xTemperature(temperature), Scd4xHumidity(humidity)


class Scd4xI2cCmdStopPeriodicMeasurement(Scd4xI2cCmdBase):
    """
    Stop Periodic Measurement I²C Command

    Stop periodic measurement and return to idle mode for sensor configuration
    or to safe energy.

    .. note:: This command is only available in measurement mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdStopPeriodicMeasurement, self).__init__(
            command=0x3F86,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.5,
        )


class Scd4xI2cCmdGetTemperatureOffset(Scd4xI2cCmdBase):
    """
    Get Temperature Offset I²C Command

    The temperature offset represents the difference between the measured
    temperature by the SCD4x and the actual ambient temperature. Per default,
    the temperature offset is set to 4°C.

    .. note:: Only available in idle mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdGetTemperatureOffset, self).__init__(
            command=0x2318,
            tx_data=None,
            rx_length=3,
            read_delay=0.001,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return:
            - temperature offset (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xTemperatureOffset`) -
              TemperatureOffset response object.
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Scd4xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        t_offset = int(unpack(">H", checked_data[0:2])[0])  # uint16
        return Scd4xTemperatureOffset(t_offset)


class Scd4xI2cCmdSetTemperatureOffset(Scd4xI2cCmdBase):
    """
    Set Temperature Offset I²C Command

    Setting the temperature offset of the SCD4x inside the customer device
    correctly allows the user to leverage the RH and T output signal. Note that
    the temperature offset can depend on various factors such as the SCD4x
    measurement mode, self-heating of close components, the ambient temperature
    and air flow. Thus, the SCD4x temperature offset should be determined
    inside the customer device under its typical operation and in thermal
    equilibrium.

    .. note:: Only available in idle mode.
    """

    def __init__(self, t_offset):
        """
        Constructor.

        :param int t_offset:
            Temperature offset in degree celsius
        """
        super(Scd4xI2cCmdSetTemperatureOffset, self).__init__(
            command=0x241D,
            tx_data=b"".join([pack(">H", Scd4xTemperatureOffsetDegC(t_offset).ticks)]),
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Scd4xI2cCmdGetSensorAltitude(Scd4xI2cCmdBase):
    """
    Get Sensor Altitude I²C Command

    Get configured sensor altitude in meters above sea level. Per default, the
    sensor altitude is set to 0 meter above sea-level.

    .. note:: Only available in idle mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdGetSensorAltitude, self).__init__(
            command=0x2322,
            tx_data=None,
            rx_length=3,
            read_delay=0.001,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return: Sensor altitude in meters.
        :rtype: int
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Scd4xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        sensor_altitude = int(unpack(">H", checked_data[0:2])[0])  # uint16
        return sensor_altitude


class Scd4xI2cCmdSetSensorAltitude(Scd4xI2cCmdBase):
    """
    Set Sensor Altitude I²C Command

    Set sensor altitude in meters above sea level. Note that setting a sensor
    altitude to the sensor overrides any pressure compensation based on a
    previously set ambient pressure.

    .. note:: Only available in idle mode.
    """

    def __init__(self, sensor_altitude):
        """
        Constructor.

        :param int sensor_altitude:
            Sensor altitude in meters.
        """
        super(Scd4xI2cCmdSetSensorAltitude, self).__init__(
            command=0x2427,
            tx_data=b"".join([pack(">H", sensor_altitude)]),
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Scd4xI2cCmdSetAmbientPressure(Scd4xI2cCmdBase):
    """
    Set Ambient Pressure I²C Command

    The set_ambient_pressure command can be sent during periodic measurements
    to enable continuous pressure compensation. Note that setting an ambient
    pressure to the sensor overrides any pressure compensation based on a
    previously set sensor altitude.

    .. note:: Available during measurements.
    """

    def __init__(self, ambient_pressure):
        """
        Constructor.

        :param int ambient_pressure:
            Ambient pressure in hPa. Convert value to Pa by: value * 100.
        """
        super(Scd4xI2cCmdSetAmbientPressure, self).__init__(
            command=0xE000,
            tx_data=b"".join([pack(">H", ambient_pressure)]),
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Scd4xI2cCmdPerformForcedRecalibration(Scd4xI2cCmdBase):
    """
    Perform Forced Recalibration I²C Command

    To successfully conduct an accurate forced recalibration, the following
    steps need to be carried out:

    1. Operate the SCD4x in a periodic measurement mode for > 3 minutes in an
       environment with homogenous and constant CO₂ concentration.
    2. Stop periodic measurement. Wait 500 ms.
    3. Subsequently issue the perform_forced_recalibration command and
       optionally read out the baseline correction. A return value of 0xffff
       indicates that the forced recalibration failed.
    """

    def __init__(self, target_co2_concentration):
        """
        Constructor.

        :param int target_co2_concentration:
            Target CO₂ concentration in ppm.
        """
        super(Scd4xI2cCmdPerformForcedRecalibration, self).__init__(
            command=0x362F,
            tx_data=b"".join([pack(">H", target_co2_concentration)]),
            rx_length=3,
            read_delay=0.4,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return: FRC correction value in CO₂ ppm or 0xFFFF if the command
                 failed.
        :rtype: int
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Scd4xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        frc_correction = int(unpack(">H", checked_data[0:2])[0])  # uint16
        if frc_correction != 0xFFFF:
            return frc_correction - 0x8000
        return frc_correction


class Scd4xI2cCmdGetAutomaticSelfCalibration(Scd4xI2cCmdBase):
    """
    Get Automatic Self Calibration I²C Command

    By default, the ASC is enabled.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdGetAutomaticSelfCalibration, self).__init__(
            command=0x2313,
            tx_data=None,
            rx_length=3,
            read_delay=0.001,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return: 1 if ASC is enabled, 0 if ASC is disabled
        :rtype: int
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Scd4xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        asc_enabled = int(unpack(">H", checked_data[0:2])[0])  # uint16
        return asc_enabled


class Scd4xI2cCmdSetAutomaticSelfCalibration(Scd4xI2cCmdBase):
    """
    Set Automatic Self Calibration I²C Command

    By default, the ASC is enabled.
    """

    def __init__(self, asc_enabled):
        """
        Constructor.

        :param int asc_enabled:
            1 to enable ASC, 0 to disable ASC
        """
        super(Scd4xI2cCmdSetAutomaticSelfCalibration, self).__init__(
            command=0x2416,
            tx_data=b"".join([pack(">H", asc_enabled)]),
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Scd4xI2cCmdStartLowPowerPeriodicMeasurement(Scd4xI2cCmdBase):
    """
    Start Low Power Periodic Measurement I²C Command

    Start low power periodic measurement, signal update interval is 30 seconds.

    .. note:: This command is only available in idle mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdStartLowPowerPeriodicMeasurement, self).__init__(
            command=0x21AC,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.0,
        )


class Scd4xI2cCmdGetDataReadyStatus(Scd4xI2cCmdBase):
    """
    Get Data Ready Status I²C Command

    Check whether new measurement data is available for read-out.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdGetDataReadyStatus, self).__init__(
            command=0xE4B8,
            tx_data=None,
            rx_length=3,
            read_delay=0.001,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return: If last 11 bits are 0 data not ready, else data ready
        :rtype: int
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Scd4xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        data_ready = int(unpack(">H", checked_data[0:2])[0])  # uint16
        return data_ready


class Scd4xI2cCmdPersistSettings(Scd4xI2cCmdBase):
    """
    Persist Settings I²C Command

    Configuration settings such as the temperature offset, sensor altitude and
    the ASC enabled/disabled parameter are by default stored in the volatile
    memory (RAM) only and will be lost after a power-cycle. This command stores
    the current configuration in the EEPROM of the SCD4x, making them
    persistent across power-cycling.

    .. note:: To avoid unnecessary wear of the EEPROM, this command should only
              be sent when persistence is required and if actual changes to the
              configuration have been made (The EEPROM is guaranteed to endure
              at least 2000 write cycles before failure). Note that field
              calibration history (i.e. FRC and ASC) is automatically stored in
              a separate EEPROM dimensioned for specified sensor lifetime.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdPersistSettings, self).__init__(
            command=0x3615,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.8,
        )


class Scd4xI2cCmdGetSerialNumber(Scd4xI2cCmdBase):
    """
    Get Serial Number I²C Command

    Reading out the serial number can be used to identify the chip and to
    verify the presence of the sensor. The get serial number command returns 3
    words. Together, the 3 words constitute a unique serial number with a
    length of 48 bits (big endian format).
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdGetSerialNumber, self).__init__(
            command=0x3682,
            tx_data=None,
            rx_length=9,
            read_delay=0.001,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return:
            - serial_number (int) - 48 bit serial number
        :rtype: tuple
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Scd4xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        serial_0 = int(unpack(">H", checked_data[0:2])[0])  # uint16
        serial_1 = int(unpack(">H", checked_data[2:4])[0])  # uint16
        serial_2 = int(unpack(">H", checked_data[4:6])[0])  # uint16
        return serial_0 << 32 | serial_1 << 16 | serial_2


class Scd4xI2cCmdPerformSelfTest(Scd4xI2cCmdBase):
    """
    Perform Self Test I²C Command

    The perform_self_test feature can be used as an end-of-line test to confirm
    sensor functionality.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdPerformSelfTest, self).__init__(
            command=0x3639,
            tx_data=None,
            rx_length=3,
            read_delay=5.5,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return: 0 means no malfunction detected
        :rtype: int
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Scd4xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        sensor_status = int(unpack(">H", checked_data[0:2])[0])  # uint16
        return sensor_status


class Scd4xI2cCmdPerformFactoryReset(Scd4xI2cCmdBase):
    """
    Perform Factory Reset I²C Command

    Initiates the reset of all configurations stored in the EEPROM and erases
    the FRC and ASC algorithm history.

    .. note:: To avoid unnecessary wear of the EEPROM, this command should only
              be sent when actual changes to the configuration have been made
              which should be reverted (The EEPROM is guaranteed to endure at
              least 2000 write cycles before failure). Note that field
              calibration history (i.e. FRC and ASC) is automatically stored in
              a separate EEPROM dimensioned for specified sensor lifetime.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdPerformFactoryReset, self).__init__(
            command=0x3632,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.8,
        )


class Scd4xI2cCmdReinit(Scd4xI2cCmdBase):
    """
    Reinit I²C Command

    The reinit command reinitializes the sensor by reloading user settings from
    EEPROM. Before sending the reinit command, the stop measurement command
    must be issued. If reinit command does not trigger the desired
    re-initialization, a power-cycle should be applied to the SCD4x.

    .. note:: Only available in idle mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdReinit, self).__init__(
            command=0x3646,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.02,
        )


class Scd4xI2cCmdMeasureSingleShot(Scd4xI2cCmdBase):
    """
    Measure Single Shot I²C Command

    On-demand measurement of CO₂ concentration, relative humidity and
    temperature. The sensor output is read with the read_measurement command.

    .. note:: Only available in idle mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdMeasureSingleShot, self).__init__(
            command=0x219D,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=1.35,
        )


class Scd4xI2cCmdMeasureSingleShotRhtOnly(Scd4xI2cCmdBase):
    """
    Measure Single Shot Rht Only I²C Command

    On-demand measurement of relative humidity and temperature only.

    .. note:: Only available in idle mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdMeasureSingleShotRhtOnly, self).__init__(
            command=0x2196,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.05,
        )


class Scd4xI2cCmdPowerDown(Scd4xI2cCmdBase):
    """
    Power Down I²C Command

    Put the sensor from idle to sleep mode to reduce current consumption.

    .. note:: Only available in idle mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdPowerDown, self).__init__(
            command=0x36E0,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.001,
        )


class Scd4xI2cCmdWakeUp(Scd4xI2cCmdBase):
    """
    Wake Up I²C Command

    Wake up sensor from sleep mode to idle mode.

    .. note:: Only available in sleep mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd4xI2cCmdWakeUp, self).__init__(
            command=0x36F6,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0,
            post_processing_time=0.02,
        )
