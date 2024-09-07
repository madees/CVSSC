/** Chataigne Module for Greenut (c) Mathieu Delquignies, 09/2021
===============================================================================
This file is a Chataigne Custom Module to remote control Greenut hardware.
More about Greenut hardware : https://

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.
3. The name of the author may not be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
===============================================================================
*/

/**	===============================================================================
*	Chataigne module common functions
*	
*	See https://bkuperberg.gitbook.io/chataigne-docs/scripting/scripting-reference#common-functions
*	===============================================================================
*/

/**
 * This function is called automatically by Chataigne when you add the module in your Noisette.
 * Used for GUI initialisation, OSC Rx callbacks.
 */
function init() 
{
	// Register OSC received messages to their callback functions
	// See https://bkuperberg.gitbook.io/chataigne-docs/scripting/scripting-reference/module-scripts#module-specific-methods-the-local-object
	local.register("/pong", "rxPong");
	local.register("/CAN/*", "rxCAN");
	local.register("/DIN/*", "rxDIN");
	local.register("/encoder", "rxEncoder");
	local.register("/button", "rxButton");
	local.register("/freqIn","rxFreq");

	// GUI setup
	setReadonly();
	collapseContainers();
}

/**
 * This function is called automatically by Chataigne when a module value changes
 * @param {value} value 
 */
function moduleValueChanged(value)
{
	if (value.is(local.values.clickToPingGreenut))
	{
		// ping button : send ping
		local.values.isThereAnybodyOutThere.set(false);
		txPing();
	}
	
	// Those module values are just little helpers for string/int/string conversion in GUI
	if (value.is(local.values.hui.stringToSceneMajorminorIndex))
	{
		// convert the Scene index string to maj/min index integers values and set them
		scene=local.values.hui.stringToSceneMajorminorIndex.get();
		index=scene.split('.');
		local.values.hui.majorIndexInteger.set(parseInt(index[0]));
		local.values.hui.minorIndexInteger.set(parseInt(index[1]));
	}
	if (value.is(local.values.hui.majorIndexInteger)||value.is(local.values.hui.minorIndexInteger))
	{
		// convert Scene maj/min integers back to string
		minorI=local.values.hui.minorIndexInteger.get();
		majorI=local.values.hui.majorIndexInteger.get();
		local.values.hui.stringToDisplay.set(majorI+"."+minorI);
	}
	if (value.is(local.values.hui.displayBrightness))
	{
		// change display brightness
		displayBrightness(local.values.hui.displayBrightness.get());
	}
}
function oscEvent(address, args)
{
}

/**	===============================================================================
	Commands to send OSC messages to Greenut
	===============================================================================
*/

/**
 * Ping Greenut
 */
function txPing()
{
	local.send("/ping");
}

/**
 * get all DIN states
 */
function getDIN()
{
	local.send("/getDIN");
}

/**
 * Ping Greenut
 */
function intEnable()
{
	local.send("/intEnable");
}

/**
 * Ping Greenut
 */
function intDisable()
{
	local.send("/intDisable");
}

/**
 * Set digital out state
 * @param {integer} channel (0-7)
 * @param {boolean} state
 */
function txDOut(channel,state)
{
	local.send("/DOut/"+channel,state);
}

/**
 * Set RGB LED color
 * @param {color} (R, G, B, Alpha) (Alpha not used)
 */
function txLED(color)
{
	local.send("/LEDColor", color);
}

/**
 * Send text to quad alphanumeric display
 * @param {string} 4 characters
 */
function txPrint(text)
{
	local.send("/print", text);
}

/**
 * Send a scrolling text to quad alphanumeric display
 * @param {string}
 */
function txMessage(text)
{
	local.send("/message", text);
}

/**
 * Send brightness setting to quad alphanumeric display
 * @param {float}
 */
function displayBrightness(value)
{
	local.send("/brightness", value);
}

/**
 * Send blink rate to quad alphanumeric display
 * @param {float}
 */
function displayBlinkRate(value)
{
	local.send("/blink", value);
}

/**
 * Set analog out voltage
 * @param {integer} channel (1-4)
 * @param {float} voltage
 */
function txAOut(channel,voltage)
{
	local.send("/AOut/"+(channel-1),voltage);
}


/**	===============================================================================
	OSC rx parsers (from registered callback, others from OSCevent function)
	===============================================================================
*/

/**
 * OSC Receive a CAN channel value
 * @param {string} address 
 * @param {array} args 
 */
function rxCAN(address, args)
{
	channel=parseInt(address.substring(address.length-1, address.length));
	if (channel==0)
		{
		local.values.cvInputs_volts_.cvIn1.set(args[0]);
		}
	else if(channel==1)
		{
		local.values.cvInputs_volts_.cvIn2.set(args[0]);
		}
	else if(channel==2)
		{
		local.values.cvInputs_volts_.cvIn3.set(args[0]);
		}
	else if(channel==3)
		{
		local.values.cvInputs_volts_.cvIn4.set(args[0]);
		}
	else if(channel==4)
		{
		local.values.cvInputs_volts_.cvIn5.set(args[0]);
		}
	else if(channel==5)
		{
		local.values.cvInputs_volts_.cvIn6.set(args[0]);
		}
	else if(channel==6)
		{
		local.values.cvInputs_volts_.cvIn7.set(args[0]);
		}
	else if(channel==7)
		{
		local.values.cvInputs_volts_.cvIn8.set(args[0]);
		}
}

/**
 * OSC Receive a DIN channel state change
 * @param {string} address 
 * @param {array} args 
 */
function rxDIN(address, args)
{
	channel=parseInt(address.substring(address.length-1, address.length));
	if (channel==0)
		{
		local.values.triggersInputs.din1.set(args[0]);  
		}
	else if(channel==1)
		{
		local.values.triggersInputs.din2.set(args[0]);
		}
	else if(channel==2)
		{
		local.values.triggersInputs.din3.set(args[0]);
		}
	else if(channel==3)
		{
		local.values.triggersInputs.din4.set(args[0]);
		}
	else if(channel==4)
		{
		local.values.triggersInputs.din5.set(args[0]);
		}
	else if(channel==5)
		{
		local.values.triggersInputs.din6.set(args[0]);
		}
	else if(channel==6)
		{
		local.values.triggersInputs.din7.set(args[0]);
		}
	else if(channel==7)
		{
		local.values.triggersInputs.din8.set(args[0]);
		}
}

/**
 * OSC Receive an answer to ping
 */
function rxPong()
{
	local.values.isThereAnybodyOutThere.set(true);
}

/**
 * OSC Receive encoder changes
 */
function rxEncoder(address, args)
{
	local.values.hui.encoder.set(args[0]);
}

/**
 * OSC Receive encoder push button changes
 */
function rxButton(address, args)
{
	local.values.hui.push.set(args[0]);
}

/**
 * OSC Receive Frequency Input changes
 */
function rxFreq(address, args)
{
	local.values.frequencyInput.set(args[0]);
}

/**	===============================================================================
	Little helper functions
	===============================================================================
*/

/**
 * Set up some GUI fields as read only
 */
function setReadonly() 
{
	//local.parameters.oscInput.localPort.setAttribute("readonly", true);
	//local.parameters.oscOutputs.oscOutput.remotePort.setAttribute("readonly", true);
	
}
/**
 * Collapse not so useful GUI containers
 */
function collapseContainers() 
{
	local.parameters.oscInput.setCollapsed(true);
	local.parameters.oscOutputs.setCollapsed(true);
	local.scripts.setCollapsed(true);
	local.templates.setCollapsed(true);
	local.commandTester.setCollapsed(true);
}
