# CVSSC
Voltage Controlled to OSC d&amp;b Soundscape controller

## What for ?
This is a "no computer" interface to control d&b Soundscape sound objects.

## How ?
It converts CV inputs (analog control voltage) to OSC messages, tailored for d&b DS100 En-Scene audio spatializer.
Build in Eurorack standard (IEC 60297 aka DIN 41494, cf https://sdiy.info/wiki/Eurorack), it includes :
* 6x CV inputs with Gain and Offset pots to scale from -12v/+12v range
* XY pad to control one object directly from the module
* Display for actual memory/scene or XY pad object ID
* Rotary encoder with push to select memory/scene or XY pad object ID
* Previous, Next, Recall scenes buttons

Gain will change the amplitude of the sound object displacement, Offset its center position (or static manual position).

## Hardware design
The module is based on Arduino Yun device. https://blog.arduino.cc/category/arduino/yun/
This device is a mix between and Arduino that has integrated ADCs for CV inputs, GPIO for display, buttons, encoders etc. and an embended Linux system to manage Ethernet, WIFI and advance Python programming for OSC management and integrated web server for monitoring and setup.
The module is build as a "shield" for the Yun, with the connectors and HUI.

## Software design
The Arduino code manages ADC and all the hardware of the module.
The Python code manages data mappings to OSC and configuration from a web browser.
