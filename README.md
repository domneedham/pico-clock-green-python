# MicroPython Pico-Clock-Green example

Python port of the C code for the Waveshare [Pico-Clock-Green](https://www.waveshare.com/wiki/Pico-Clock-Green) product.

The code will be appended to support the Pico W and MQTT, so you can control it from smart home platforms such as Home Assistant.

> **Status**: The next big change will to be include the uasyncio library to (hopefully) improve performance.

> **Status**: So far, the code in this repo covers much of the basics, but the
> core functionality of the clock (alarms) remains to be
> implemented.

> **Status**: This code is changing a lot at present, as all the necessary features
> are added. Please expect change, and please expect classes and APIs to change.

## Instructions (Linux/Mac)

- Flash MicroPython onto the Pico.
  https://null-byte.wonderhowto.com/how-to/use-upip-load-micropython-libraries-onto-microcontroller-over-wi-fi-0237888/
- Install `ampy` from AdaFruit.
- Execute the `run` bash script to upload Python files and execute
  main.py

## Instructions (Windows)

If not running on Linux, use your usual method for uploading code to the Pico.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of updates.

## New Features

See [Features.md](FEATURES.md) for a list of features supported/to be added.
