#!/usr/bin/env python3
#
# Python PTT remote (TX) by barf <stuart@macintosh>
#

import os
import array
import time
import pickle
import zmq
# from IPython import embed

import ctypes
import struct, time
import numpy as np

BIND_ADDRESS = "*" # '*' or IP address to bind to
SERVER_PORT = 5555 # default = 5555

CONST_DLL_VJOY = "C:\\Program Files\\vJoy\\x64\\vJoyInterface.dll"

class vJoy(object):
    def __init__(self, reference = 1):
        self.handle = None
        self.dll = ctypes.CDLL( CONST_DLL_VJOY )
        self.reference = reference
        self.acquired = False
        
    def open(self):
        if self.dll.AcquireVJD( self.reference ):
            self.acquired = True
            return True
        return False
    def close(self):
        if self.dll.RelinquishVJD( self.reference ):
            self.acquired = False
            return True
        return False
    def generateJoystickPosition(self, 
        wThrottle = 0, wRudder = 0, wAileron = 0, 
        wAxisX = 0, wAxisY = 0, wAxisZ = 0,
        wAxisXRot = 0, wAxisYRot = 0, wAxisZRot = 0,
        wSlider = 0, wDial = 0, wWheel = 0,
        wAxisVX = 0, wAxisVY = 0, wAxisVZ = 0,
        wAxisVBRX = 0, wAxisVBRY = 0, wAxisVBRZ = 0,
        lButtons = 0, bHats = 0, bHatsEx1 = 0, bHatsEx2 = 0, bHatsEx3 = 0):
        """
        typedef struct _JOYSTICK_POSITION
        {
            BYTE    bDevice; // Index of device. 1-based
            LONG    wThrottle;
            LONG    wRudder;
            LONG    wAileron;
            LONG    wAxisX;
            LONG    wAxisY;
            LONG    wAxisZ;
            LONG    wAxisXRot;
            LONG    wAxisYRot;
            LONG    wAxisZRot;
            LONG    wSlider;
            LONG    wDial;
            LONG    wWheel;
            LONG    wAxisVX;
            LONG    wAxisVY;
            LONG    wAxisVZ;
            LONG    wAxisVBRX;
            LONG    wAxisVBRY;
            LONG    wAxisVBRZ;
            LONG    lButtons;   // 32 buttons: 0x00000001 means button1 is pressed, 0x80000000 -> button32 is pressed
            DWORD   bHats;      // Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
                        DWORD   bHatsEx1;   // 16-bit of continuous HAT switch
                        DWORD   bHatsEx2;   // 16-bit of continuous HAT switch
                        DWORD   bHatsEx3;   // 16-bit of continuous HAT switch
        } JOYSTICK_POSITION, *PJOYSTICK_POSITION;
        """
        joyPosFormat = "BlllllllllllllllllllIIII"
        pos = struct.pack( joyPosFormat, self.reference, wThrottle, wRudder,
                                   wAileron, wAxisX, wAxisY, wAxisZ, wAxisXRot, wAxisYRot,
                                   wAxisZRot, wSlider, wDial, wWheel, wAxisVX, wAxisVY, wAxisVZ,
                                   wAxisVBRX, wAxisVBRY, wAxisVBRZ, lButtons, bHats, bHatsEx1, bHatsEx2, bHatsEx3 )
        return pos
    def update(self, joystickPosition):
        if self.dll.UpdateVJD( self.reference, joystickPosition ):
            return True
        return False
    #Not working, send buttons one by one
    def sendButtons( self, bState ):
        joyPosition = self.generateJoystickPosition( lButtons = bState )
        return self.update( joyPosition )
    def setButton( self, index, state ):
        if self.dll.SetBtn( state, self.reference, index ):
            return True
        return False

# valueX, valueY between -1.0 and 1.0
# scale between 0 and 16000
def setJoy(valueX, valueY, scale):
    xPos = int(valueX*scale)
    yPos = int(valueY*scale)
    joystickPosition = vj.generateJoystickPosition(wAxisX = 16000+xPos, wAxisY = 16000+yPos)
    vj.update(joystickPosition)

def makeBitArray(bitSize, fill = 0):
    intSize = bitSize >> 5                   # number of 32 bit integers
    if (bitSize & 31):                      # if bitSize != (32 * n) add
        intSize += 1                        #    a record for stragglers
    if fill == 1:
        fill = 4294967295                                 # all bits set
    else:
        fill = 0                                      # all bits cleared

    bitArray = array.array('I')          # 'I' = unsigned 32-bit integer
    bitArray.extend((fill,) * intSize)

    return(bitArray)

# testBit() returns a nonzero result, 2**offset, if the bit at 'bit_num' is set to 1.
def testBit(array_name, bit_num):
    record = bit_num >> 5
    offset = bit_num & 31
    mask = 1 << offset
    return(array_name[record] & mask)

# setBit() returns an integer with the bit at 'bit_num' set to 1.
def setBit(array_name, bit_num):
    record = bit_num >> 5
    offset = bit_num & 31
    mask = 1 << offset
    array_name[record] |= mask
    return(array_name[record])

# clearBit() returns an integer with the bit at 'bit_num' cleared.
def clearBit(array_name, bit_num):
    record = bit_num >> 5
    offset = bit_num & 31
    mask = ~(1 << offset)
    array_name[record] &= mask
    return(array_name[record])

# toggleBit() returns an integer with the bit at 'bit_num' inverted, 0 -> 1 and 1 -> 0.
def toggleBit(array_name, bit_num):
    record = bit_num >> 5
    offset = bit_num & 31
    mask = 1 << offset
    array_name[record] ^= mask
    return(array_name[record])

if __name__ == '__main__':
    # TODO: (json?) config file
    context = zmq.Context()
    print("Starting server…")
    subscriber = context.socket(zmq.SUB)
    subscriber.bind("tcp://%s:%s" % (BIND_ADDRESS, SERVER_PORT))
    subscriber.setsockopt(zmq.SUBSCRIBE, b'')
    print("ZMQ server started")
    print("opening virtual joystick…")
    vj = vJoy()
    vj.open()
    print("virtual joystick connected")
    print('ready…')

    nbr = 0
    buttons = makeBitArray(32, 0)
    while True:
        msg = subscriber.recv()
        data = pickle.loads(msg)
        event = data[0:2]
        t_tx = data[2]
        t_delta = time.time() - t_tx
        # print('Event#%s:\t%s\tTime:\t%s\tt-delta:\t%s' % (nbr, event, t_tx, t_delta))
        nbr += 1
        ## process event
        # test()
        if event[0] == 10: # ptt pressed
            # print('PTT ON')
            button_idx = event[1]['button']
            setBit(buttons, button_idx)
            joystickPosition = vj.generateJoystickPosition(lButtons = buttons[0])
            vj.update(joystickPosition)
        if event[0] == 11: # ptt released
            # print('PTT OFF')
            button_idx = event[1]['button']
            clearBit(buttons, button_idx)
            joystickPosition = vj.generateJoystickPosition(lButtons = buttons[0])
            vj.update(joystickPosition)

    print("vj closing", flush=True)
    vj.close()
