# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function

from sensirion_i2c_driver import I2cDevice
from sensirion_i2c_driver.errors import I2cNackError

from .commands import Scd4xI2cCmdGetSerialNumber, Scd4xI2cCmdStartPeriodicMeasurement, \
    Scd4xI2cCmdStartLowPowerPeriodicMeasurement, Scd4xI2cCmdReadMeasurement, Scd4xI2cCmdStopPeriodicMeasurement, \
    Scd4xI2cCmdGetTemperatureOffset, Scd4xI2cCmdSetTemperatureOffset, Scd4xI2cCmdGetSensorAltitude, \
    Scd4xI2cCmdSetSensorAltitude, Scd4xI2cCmdSetAmbientPressure, Scd4xI2cCmdPerformForcedRecalibration, \
    Scd4xI2cCmdGetAutomaticSelfCalibration, Scd4xI2cCmdSetAutomaticSelfCalibration, Scd4xI2cCmdGetDataReadyStatus, \
    Scd4xI2cCmdPersistSettings, Scd4xI2cCmdPerformSelfTest, Scd4xI2cCmdPerformFactoryReset, Scd4xI2cCmdReinit, \
    Scd4xI2cCmdMeasureSingleShot, Scd4xI2cCmdMeasureSingleShotRhtOnly, Scd4xI2cCmdPowerDown, Scd4xI2cCmdWakeUp
from .data_types import Scd4xPowerMode


class Scd4xI2cDevice(I2cDevice):
    """
    SCD4x I²C device class to allow executing I²C commands.
    """

    def __init__(self, connection, slave_address=0x62):
        """
        Constructs a new SCD4X I²C device.

        :param ~sensirion_i2c_driver.connection.I2cConnection connection:
            The I²C connection to use for communication.
        :param byte slave_address:
            The I²C slave address, defaults to 0x62.
        """
        super(Scd4xI2cDevice, self).__init__(connection, slave_address)

    def read_serial_number(self):
        """
        Read the serial number from the device.

        :return: The serial number.
        :rtype: int
        """
        return self.execute(Scd4xI2cCmdGetSerialNumber())

    def start_periodic_measurement(self, power_mode=Scd4xPowerMode.HIGH):
        """
        Start periodic measurement with given power mode

        :param ~sensirion_i2c_scd.scd4x.data_types.Scd4xPowerMode power_mode:
            The power mode (HIGH or LOW) to use for periodic measurements.
            High power mode measures every 5 seconds, while low power mode
            measures every 30 seconds. Default: High power mode

        .. note:: Only available in idle mode.
        """
        if power_mode == Scd4xPowerMode.HIGH:
            result = self.execute(Scd4xI2cCmdStartPeriodicMeasurement())
        elif power_mode == Scd4xPowerMode.LOW:
            result = self.execute(Scd4xI2cCmdStartLowPowerPeriodicMeasurement())
        else:
            raise ValueError('Unknown argument for power_mode')
        return result

    def read_measurement(self):
        """
        Read measurement during periodic measurement mode. Returns Co2, temperature and relative humidity
        as tuple

        :return:
            - co2 (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xCarbonDioxid`) -
              CO₂ response object
            - temperature (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xTemperature`) -
              Temperature response object.
            - humidity (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xHumidity`) -
              Humidity response object
        :rtype: tuple
        """
        return self.execute(Scd4xI2cCmdReadMeasurement())

    def stop_periodic_measurement(self):
        """
        Stop periodic measurement.

        .. note:: this command is only available in periodic measurement mode
        """
        return self.execute(Scd4xI2cCmdStopPeriodicMeasurement())

    def get_temperature_offset(self):
        """
        Get Temperature Offset I²C Command

        The temperature offset represents the difference between the measured
        temperature by the SCD4x and the actual ambient temperature. Per default,
        the temperature offset is set to 4°C.

        :return:
            - temperature (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xTemperatureOffset`) -
              temperature offset response object

        .. note:: Only available in idle mode.
        """
        return self.execute(Scd4xI2cCmdGetTemperatureOffset())

    def set_temperature_offset(self, t_offset):
        """
        Setting the temperature offset of the SCD4x
        inside the customer device correctly allows the user to leverage the RH and T
        output signal. Note that the temperature offset can depend on various factors
        such as the SCD4x measurement mode, self-heating of close components, the
        ambient temperature and air flow. Thus, the SCD4x temperature offset should
        be determined inside the customer device under its typical operation and in
        thermal equilibrium.

        .. note:: Only availabe in idle mode

        :param: (float) t_offset
                The temperature offset in degree Celsius
        """
        return self.execute(Scd4xI2cCmdSetTemperatureOffset(t_offset))

    def get_sensor_altitude(self):
        """
        Get Sensor Altitude I²C Command

        Get configured sensor altitude in meters above sea level. Per default, the
        sensor altitude is set to 0 meter above sea-level.

        .. note:: Only available in idle mode.
        """
        return self.execute(Scd4xI2cCmdGetSensorAltitude())

    def set_sensor_altitude(self, sensor_altitude):
        """
        Set Sensor Altitude I²C Command

        Set sensor altitude in meters above sea level. Note that setting a sensor
        altitude to the sensor overrides any pressure compensation based on a
        previously set ambient pressure.

        :param: (int) sensor_altitude: The altitude in meters above sea level

        .. note:: Only available in idle mode.
        """
        return self.execute(Scd4xI2cCmdSetSensorAltitude(sensor_altitude))

    def set_ambient_pressure(self, ambient_pressure):
        """
        Set Ambient Pressure I²C Command

        The set_ambient_pressure command can be sent during periodic measurements
        to enable continuous pressure compensation. Note that setting an ambient
        pressure to the sensor overrides any pressure compensation based on a
        previously set sensor altitude.

        :param int ambient_pressure:
            Ambient pressure in hPa. Convert value to Pa by: value * 100.

        .. note:: Available during measurements.
        """
        return self.execute(Scd4xI2cCmdSetAmbientPressure(ambient_pressure))

    def perform_forced_recalibration(self, target_co2_concentration):
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

        :param int target_co2_concentration:
            Target CO₂ concentration in ppm.

        :return: FRC correction value in CO₂ ppm or 0xFFFF if the command
                 failed.
        :rtype: int
        """
        return self.execute(Scd4xI2cCmdPerformForcedRecalibration(target_co2_concentration))

    def get_automatic_self_calibration(self):
        """
        Get Automatic Self Calibration I²C Command

        :return: True if ASC is enabled, False if ASC is disabled
        :rtype: int
        """
        ret = self.execute(Scd4xI2cCmdGetAutomaticSelfCalibration())
        return ret == 1

    def set_automatic_self_calibration(self, asc_enabled):
        """
        Set Automatic Self Calibration I²C Command

        :param int asc_enabled:
            True to enable ASC, False to disable ASC
        """
        if asc_enabled:
            value = 1
        else:
            value = 0
        return self.execute(Scd4xI2cCmdSetAutomaticSelfCalibration(value))

    def get_data_ready_status(self):
        """
        Get Data Ready Status I²C Command

        Check whether new measurement data is available for read-out.

        :return: True if data ready, else False
        :rtype: bool
        """
        ret = self.execute(Scd4xI2cCmdGetDataReadyStatus())
        return (ret & 0x07FF) > 0

    def persist_settings(self):
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
        return self.execute(Scd4xI2cCmdPersistSettings())

    def perform_self_test(self):
        """
        Perform Self Test I²C Command

        The perform_self_test feature can be used as an end-of-line test to confirm
        sensor functionality.

        :return: 0 means no malfunction detected
        :rtype: int
        """
        return self.execute(Scd4xI2cCmdPerformSelfTest())

    def perform_factory_reset(self):
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
        return self.execute(Scd4xI2cCmdPerformFactoryReset())

    def reinit(self):
        """
        Reinit I²C Command

        The reinit command reinitializes the sensor by reloading user settings from
        EEPROM. Before sending the reinit command, the stop measurement command
        must be issued. If reinit command does not trigger the desired
        re-initialization, a power-cycle should be applied to the SCD4x.

        .. note:: Only available in idle mode.
        """
        return self.execute(Scd4xI2cCmdReinit())

    def measure_single_shot(self):
        """
        Measure Single Shot I²C Command

        On-demand measurement of CO₂ concentration, relative humidity and
        temperature. The sensor output is read with the read_measurement command.

        .. note:: Only available in idle mode.
        """
        return self.execute(Scd4xI2cCmdMeasureSingleShot())

    def measure_single_shot_rht_only(self):
        """
        Measure Single Shot Rht Only I²C Command

        On-demand measurement of relative humidity and temperature only.
        The sensor output is read with the read_measurement command.

        .. note:: Only available in idle mode.
        """
        return self.execute(Scd4xI2cCmdMeasureSingleShotRhtOnly())

    def power_down(self):
        """
        Power Down I²C Command

        Put the sensor from idle to sleep mode to reduce current consumption.

        .. note:: Only available in idle mode.
        """
        return self.execute(Scd4xI2cCmdPowerDown())

    def wake_up(self):
        """
        Wake Up I²C Command

        Wake up sensor from sleep mode to idle mode.

        .. note:: Only available in sleep mode.
        """
        try:
            self.execute(Scd4xI2cCmdWakeUp())
        except I2cNackError:
            # This command might result in a I2C NACK if the SCD4x
            # can't wake up fast enough to respond on time
            pass
