# Python Driver for Sensirion I²C Carbon Dioxide Sensor

<b>This driver repository is deprecated. The Python SCD4x driver has been moved to [https://github.com/Sensirion/python-i2c-scd4x](https://github.com/Sensirion/python-i2c-scd4x).</b>

This repository contains the Python driver to communicate with Sensirion
SCD4x CO2 sensors using the I²C interface.

[<center><img src="images/SCD4x.png" width="300px"></center>](https://sensirion.com/my-scd-ek)

Click [here](https://sensirion.com/my-scd-ek) to learn more about the SCD4x
sensor and the SCD41 Evaluation Kit Board.

Click [here](https://sensirion.com/products/product-categories/co2/)
to learn more about the Sensirion SCD4x sensor family.

## Supported Sensors

* SCD40
* SCD41
* SCD42

## Usage

See user manual at [https://sensirion.github.io/python-i2c-scd/](https://sensirion.github.io/python-i2c-scd/).

### Connecting the SCD41 Evaluation Kit Board

Your sensor has the four different connectors: VCC, GND, SDA and SCL. The
provided jumper wire cables have the following colors.

 *SCD4x*  | *Jumper Wire*
 :------: | :-----------:
   VCC    |      Red
   GND    |     Black
   SDA    |     Green
   SCL    |     Yellow

## Development

We develop and test this driver using our company internal tools (version
control, continuous integration, code review etc.) and automatically
synchronize the `master` branch with GitHub. But this doesn't mean that we
don't respond to issues or don't accept pull requests on GitHub. In fact,
you're very welcome to open issues or create pull requests :)

### Check coding style

The coding style can be checked with [`flake8`](http://flake8.pycqa.org/):

```bash
pip install -e .[test]  # Install requirements
flake8                  # Run style check
```

In addition, we check the formatting of files with
[`editorconfig-checker`](https://editorconfig-checker.github.io/):

```bash
pip install editorconfig-checker==2.0.3   # Install requirements
editorconfig-checker                      # Run check
```

### Run tests

Unit tests can be run with [`pytest`](https://pytest.org/):

```bash
pip install -e .[test]                             # Install requirements
pytest -m "not needs_device"                       # Run tests without hardware
pytest                                             # Run all tests
pytest -m "not (needs_device and not needs_scd4x)" # Run all tests for scd4x
```

The tests with the marker `needs_scd4x` have following requirements:

- An SCD4x device must be connected to a
  [SensorBridge](https://www.sensirion.com/sensorbridge/) on port 1.
- Pass the serial port where the SensorBridge is connected with
  `--serial-port`, e.g. `pytest --serial-port=COM7`
- The SensorBridge must have default settings (baudrate 460800, address 0)


### Build documentation

The documentation can be built with [Sphinx](http://www.sphinx-doc.org/):

```bash
python setup.py install                        # Install package
pip install -r docs/requirements.txt           # Install requirements
sphinx-versioning build docs docs/_build/html  # Build documentation
```

## License

See [LICENSE](LICENSE).
