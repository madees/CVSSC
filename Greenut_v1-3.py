print("*** Greenut OSC Bridge ***")
print("v1.3 Mathieu Delquignies 22/10/2021")

# Import needed modules from osc4py3
# more infos :
# https://pypi.org/project/osc4py3/ 
from osc4py3.as_allthreads import *
from osc4py3 import oscmethod as osm
from osc4py3 import oscbuildparse

# Import needed modules from Pi-Plates
# more infos :
# https://pi-plates.com/daqc2-users-guide/
import piplates.DAQC2plate as DAQC2

#Import needed modules from Adafruit
import board
from adafruit_seesaw import seesaw, neopixel, rotaryio, digitalio
from adafruit_ht16k33.segments import Seg14x4
 
# Import utilities from modules
from time import sleep
from sys import argv
import socket
import RPi.GPIO as GPIO
import datetime

print(str(datetime.datetime.now()), "All libs import OK.")
#####################
# Constants & Globals
#
displayText = ""

# CANs values buffer
prevCAN = [0,0,0,0,0,0,0,0,0]

# FREQ input buffer
prevFreq = 0

# DIN int flags
DINInterrupt = 0
DINByte = 0

# Network parameters
# Rx host
rxPort=50052
localIP=socket.gethostbyname(socket.gethostname())
# Tx host
txPort=50051
# Command line argument may be recipient IP, without arg it will be Local
if(len(argv)==2):
    ipAddress=argv[1]
else:
    ipAddress=localIP

#####################
# Callback functions
#

# Reply to ping
def ping():
    msg = oscbuildparse.OSCMessage("/pong", None, [])
    osc_send(msg, "OSCTx")
    print(str(datetime.datetime.now()), "Received a ping, answering pong.")
    

# Set DOUT
def OSCDOut(address, args):
    # convert output number in address String to Integer range (0-7)
    pinOut=int(address[len(address)-1])%8
    # set or clear corresponding DAQC2 plate output
    if (args==1):
        DAQC2.setDOUTbit(0, pinOut)
    else:
        DAQC2.clrDOUTbit(0, pinOut)
    

# Set RGB Led color
def OSCLEDColor(red, green, blue, alpha):
    pixel.fill((int(red*255), int(green*255), int(blue*255)))
    print("Color led: R"+red+ " G"+ green," B"+ blue)
    
    
# Print text
def OSCPrint(args):
    displayText=str(args)
    display.print("   " + displayText)
    

# Print text  (speed 0.25, no loop)
def OSCMessage(args):
    display.marquee(str(args)+displayText, 0.25, False)
    

# get all Din values
def getDAQC2DIN():
    global DINInterrupt
    global DINByte
    # get DIN digital inputs values
    DINByte=DAQC2.getDINall(0)
    DINInterrupt=255
    
    
# DAQC2 Din Interrupt
def DAQC2Interrupt():
    global DINInterrupt
    global DINByte
    # get DIN digital inputs values
    DINByte=DAQC2.getDINall(0)
    # should debounce button before clearing interrupt ?! (software deboucining slow down OSC send rate, including CANs)
    DINInterrupt=DAQC2.getINTflags(0)
    
    
#
def intEnable():
    DAQC2.intEnable(0)
    print(str(datetime.datetime.now()), "DIN interrupts enabled.")
    

def intDisable():
    DAQC2.intDisable(0)
    print(str(datetime.datetime.now()), "DIN interrupts disabled.")
    

def OSCbrightness(args):
    display.brightness = args
    
    
def OSCblink(args):
    display.blink_rate = args
    
    
def OSCAOut(address, args):
    # convert output number in address String to Integer range (0-3)
    channel=int(address[len(address)-1])%4
    # set corresponding DAQC2 plate DA output voltage
    DAQC2.setDAC(0,channel,args)
    print(str(datetime.datetime.now()),"AOut #",channel," ",args)
    
    

#####################
#Functions

def testBit(int_type, offset):
    mask = 1 << offset
    return(bool(int_type & mask))

# Set Pi-PlatesRGB Led (for script only)
def PiPlateLED(args):
    # args is color as string: ‘off’, 'red’, ‘green’, ‘yellow’, ‘blue’, ‘magenta’, ‘cyan’, ‘white’
    DAQC2.setLED(0, args)
    
#####################
# Main
PiPlateLED("off")

# Board interrupt config for DIN triggers
# GPIO 22 is used as external interrupt from DAQC2. Enable input on this pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# set interrupt callback
# ? strange behaviour of bouncetime>1, see sleep() in interrupt callback alternative ? worth check with GPIO module update
# put this in main loop instead of callback (following Jerry's instructions form Pi-plates)
# GPIO.add_event_detect(22, GPIO.FALLING, callback=DAQC2Interrupt, bouncetime=1)
# enable interrupt also on DAQC2 #0-7 Digital Inputs for both edges
for i in range(8):DAQC2.enableDINint(0, i, "b")
# reset interrupt flag, pin GPIO.22 should be high
DINInterrupt=DAQC2.getINTflags(0)
if (DAQC2.GPIO.input(22)==1): print(str(datetime.datetime.now()), "External interrupts OK.")

# Start the OSC system.
osc_startup()
print(str(datetime.datetime.now()), "OSC system started.")

# Make server channels to receive and send packets with LOCAL IP
osc_udp_server("127.0.0.1", rxPort, "OSCRx")
print(str(datetime.datetime.now()), "Local OSC server up and running on port "+str(rxPort)+" @"+localIP)
osc_udp_client(ipAddress, txPort, "OSCTx")
print(str(datetime.datetime.now()), "OSC client up and running on port "+str(txPort)+" @"+ipAddress)

# Associate Python functions with received message address patterns (default argument scheme OSCARG_DATAUNPACK)
osc_method("/ping", ping)
osc_method("/DOut/*", OSCDOut, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
osc_method("/LEDColor", OSCLEDColor)
osc_method("/print", OSCPrint)
osc_method("/message", OSCMessage)
osc_method("/getDIN", getDAQC2DIN)
osc_method("/intEnable",intEnable)
osc_method("/intDisable",intDisable)
osc_method("/brightness",OSCbrightness)
osc_method("/blink",OSCblink)
osc_method("/AOut/*", OSCAOut, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
print(str(datetime.datetime.now()), "OSC Rx parser up")

# Setup HUI on I2C bus with rotary encoder, RGB pixel and quad alphanumeric display
i2c = board.I2C()
seesaw = seesaw.Seesaw(i2c, 0x36)

encoder = rotaryio.IncrementalEncoder(seesaw)
last_position = -1

seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw, 24)
button_held = False

pixel = neopixel.NeoPixel(seesaw, 6, 1)

display = Seg14x4(i2c)
display.brightness = 0 # lowest as default, from 0 to 1 in 1/16 step

print(str(datetime.datetime.now()), "HUI setup OK")

print(str(datetime.datetime.now()), "Start event loop. Press Ctrl+c to stop.")
PiPlateLED("green")

#####################################################################################
# Start event loop
activityLED=0
try:
    finished = False
    while not finished:
        # Process HUI rotary encoder to OSC
        # negate the position to make clockwise rotation positive
        position = -encoder.position
        
        # Don't know why sometimes encoder send this false value ? filter it out
        if position == 2147483648:
            print(str(datetime.datetime.now()),"Encoder erronous value ?")
            position = last_position

        if position != last_position:
            last_position = position
            #print(str(datetime.datetime.now()),"Encoder ",position)
            msg = oscbuildparse.OSCMessage("/encoder/", None, [position])
            osc_send(msg, "OSCTx")
        
        # Process HUI push button to OSC
        if not button.value and not button_held:
            button_held = True
            msg = oscbuildparse.OSCMessage("/button/", None, [1])
            osc_send(msg, "OSCTx")
           
        if button.value and button_held:
            button_held = False
            msg = oscbuildparse.OSCMessage("/button/", None, [0])
            osc_send(msg, "OSCTx")
                    
        # Process DIN to OSC
        # Check for DIN interrupts manually (RPI interrupt callback is de-activated)
        if (DAQC2.GPIO.input(22)==0): DAQC2Interrupt()
        if (DINInterrupt):
            if (DINInterrupt>255):
                print(str(datetime.datetime.now()), "Interrupt error ! "+str(DINInterrupt))
            else:
                for i in range(8):
                    if (testBit(DINInterrupt,i)): 
                        msg = oscbuildparse.OSCMessage("/DIN/"+str(i), None, [int(testBit(DINByte,i)==True)])
                        osc_send(msg, "OSCTx")
            DINInterrupt=0
        
        # Process CANs to OSC
        # Get all 8 channels
        CAN=DAQC2.getADCall(0)
        for i in range(8):
            if prevCAN[i]!=CAN[i]:
                msg = oscbuildparse.OSCMessage("/CAN/"+str(i), None, [CAN[i]])
                osc_send(msg, "OSCTx")
                #print("CAN",i)
                prevCAN[i]=CAN[i]
        
        # Process Freq In to OSC
        #freq=DAQC2.getFREQ(0)
        #if prevFreq!=freq:
        #    msg = oscbuildparse.OSCMessage("/freqIn", None, [freq])
        #    osc_send(msg, "OSCTx")
        #    prevFreq=freq
        #    print(str(datetime.datetime.now()),"freqIn ",freq)
        
        # Process OSC inputs
        osc_process()
        
        #Slow down to <50Hz
        #sleep(0.02)
        
        #Blink led
        if(activityLED<10):
            activityLED +=1
        else:
            activityLED =0
            PiPlateLED("green")
        if(activityLED==1):PiPlateLED("off")   
        
# Properly close the system.
except KeyboardInterrupt:
    print(str(datetime.datetime.now()), "OSCDAQC2Plate.py stopped by operator.")
    
osc_terminate()
print(str(datetime.datetime.now()), "OSC system stopped.")
PiPlateLED("red")
GPIO.cleanup()
print(str(datetime.datetime.now()), "GPIO interrupts cleaned.")

