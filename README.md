# CVSSC
Voltage Controlled to OSC d&amp;b Soundscape controller

3/2021 : project stopped with this Yun idea, move to Raspberry Pi and DAQC2 HAT, see https://github.com/madees/DAQC2-Chataigne-Module
1/2024 : third step, now the active project is https://github.com/madees/asynth2osc
As Arduino Yun is discountinued, I've aborted this solution. Instead, I did it with a RPI HAT, and this RPI is using Chataigne embended to map OSC to DS100.

## What for ?
This is a "no computer" or "daw less" interface to control d&b Soundscape En-Scene sound objects from Eurorack analog modular synth modules. https://www.dbsoundscape.com/global/en/system-profile/en-scene/

This community module is NOT OFFICIALLY supported by d&b audiotechnik. It is publicly available to enable interested users to experiment, extend and create their own adaptations. There is no guarantee for compatibility inbetween versions or for the implemented functionality to be reliable for professional. Use what is provided here at your own risk!

## How ?
It converts CV inputs (analog control voltage) to OSC messages, tailored for d&b DS100 En-Scene audio spatializer.
Build in Eurorack standard (IEC 60297 aka DIN 41494, cf https://sdiy.info/wiki/Eurorack), it includes :
* 6x CV inputs with Gain and Offset pots to scale from -12v/+12v range
* XY pad to control one object directly from the module
* Display for actual memory/scene or XY pad object ID
* Rotary encoder with push to select memory/scene or XY pad object ID
* Previous, Next, Recall scenes buttons
* Integrated web interface to setup the OSC mappings and configurations

CV input Gain pot will change the amplitude of the sound object displacement, Offset pot its center position (or static manual position).

## Hardware design
The module is based on Arduino Yun device. https://store.arduino.cc/arduino-yun
This device is a mix between and Arduino that has integrated ADCs for CV inputs, GPIO for display, buttons, encoders etc. and an embended Linux system on Atheros processor to manage Ethernet, WIFI and advance Python programming for OSC management and integrated web server for monitoring and setup.

The module is build as a "shield" for the Yun, a PCB with all the connectors and components, connected to Yun pins header. 

On the analog part, 6 analog front ends to amplify and offset any CV signal for -12v to +12v to the ADC optimal range.

On its digital part, it includes the HUI components (rotary encoder with push button, three buttons with interrupts, one I2C display (4xdigits) and one I2C xY touch pad.

The ICSP port is still available for extension (example as coms with a Raspberry Pi or a more complex display).
Two I2C spare ports are provided in Grove standard https://wiki.seeedstudio.com/Grove_System/ for external sensors, actuators etc.

The power supply is as specified in Eurorack dual rail 12v DC, additional 5v regulation is done on the module (3.3v on the Yun itslef).

The circuit for PCB board has been designed with KiCad. https://kicad.org/

## BOM
* 1x Arduino Yun
* 1x 5 Pins 360 Degree Rotary Encoder w Push Button Switch https://www.adafruit.com/product/377
* 1x Adafruit 0.56" 4-Digit 7-Segment Display w/I2C Backpack - Green https://www.adafruit.com/product/880
* 1x TRILL XY Pad https://shop.bela.io/collections/trill/products/trill-square
* 1x CVSSC PCB board
* 1x aluminium Eurorack ?U front panel
* ...
* ICs R C connectors etc. to be continued form KiCAD BOM

## Software design
The Arduino code manages ADC and all the hardware of the module.
The Python code manages data mappings to OSC and configuration from a web browser.
