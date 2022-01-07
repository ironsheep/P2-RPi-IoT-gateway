#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _thread
from datetime import datetime
from time import time, sleep, localtime, strftime
import os
import subprocess
import sys
import os.path
import argparse
from collections import deque
from unidecode import unidecode
from colorama import init as colorama_init
from colorama import Fore, Back, Style
import serial
from time import sleep

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

script_version  = "0.0.1"
script_name     = 'P2-RPi-ioT-gw-daemon.py'
script_info     = '{} v{}'.format(script_name, script_version)
project_name    = 'P2-RPi-IoT-gw'
project_url     = 'https://github.com/ironsheep/P2-RPi-IoT-gateway'

# -------------------------------
# the following are identical to that found in our gateway .spin2 object
#   (!!!they must be kept in sync!!!)
parm_sep    = '^|^'     # chars that will not be found in user data
body_start  = 'emailStart'
body_end    = 'emailEnd'
# -------------------------------

if False:
    # will be caught by python 2.7 to be illegal syntax
    print_line('Sorry, this script requires a python3 runtime environment.', file=sys.stderr)
    os._exit(1)

# Logging function
def print_line(text, error=False, warning=False, info=False, verbose=False, debug=False, console=True):
    timestamp = strftime('%Y-%m-%d %H:%M:%S', localtime())
    if console:
        if error:
            print(Fore.RED + Style.BRIGHT + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL, file=sys.stderr)
        elif warning:
            print(Fore.YELLOW + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL)
        elif info or verbose:
            if opt_verbose:
                # verbose...
                print(Fore.GREEN + '[{}] '.format(timestamp) + Fore.YELLOW  + '- ' + '{}'.format(text) + Style.RESET_ALL)
            else:
                # info...
                print(Fore.MAGENTA + '[{}] '.format(timestamp) + Fore.YELLOW  + '- ' + '{}'.format(text) + Style.RESET_ALL)
        elif debug:
            if opt_debug:
                print(Fore.CYAN + '[{}] '.format(timestamp) + '- (DBG): ' + '{}'.format(text) + Style.RESET_ALL)
        else:
            print(Fore.GREEN + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL)

# -----------------------------------------------------------------------------
#  Script Argument parsing
# -----------------------------------------------------------------------------

# Argparse
opt_debug = False
opt_verbose = False
opt_useTestFile = False

# Argparse
parser = argparse.ArgumentParser(description=project_name, epilog='For further details see: ' + project_url)
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-d", "--debug", help="show debug output", action="store_true")
parser.add_argument("-t", "--test", help="run from canned test file", action="store_true")
parse_args = parser.parse_args()

opt_debug = parse_args.debug
opt_verbose = parse_args.verbose
opt_useTestFile = parse_args.test

print_line(script_info, info=True)
if opt_verbose:
    print_line('Verbose enabled', info=True)
if opt_debug:
    print_line('Debug enabled', debug=True)
if opt_useTestFile:
    print_line('TEST: debug stream is test file', debug=True)

# -----------------------------------------------------------------------------
#  Circular queue for serial input lines & serial listener
# -----------------------------------------------------------------------------

lineBuffer = deque()

def pushLine(newLine):
    lineBuffer.append(newLine)
    # show debug every 100 lines more added
    if len(lineBuffer) % 100 == 0:
        print_line('- lines({})'.format(len(lineBuffer)),debug=True)

def popLine():
    global lineBuffer
    oldestLine = ''
    if len(lineBuffer) > 0:
        oldestLine = lineBuffer.popleft()
    return oldestLine


# -----------------------------------------------------------------------------
#  TASK: dedicated serial listener
# -----------------------------------------------------------------------------

def taskProcessInput():
    print_line('Thread: taskProcessInput() started', verbose=True)
    # process lies from serial or from test file
    if opt_useTestFile == True:
        test_file=open("charlie_rpi_debug.out", "r")
        lines = test_file.readlines()
        for currLine in lines:
            pushLine(currLine)
            #sleep(0.1)
    else:
        ser = serial.Serial ("/dev/serial0", 2000000, timeout=1)    #Open port with baud rate & timeout
        while True:
            received_data = ser.readline()              #read serial port
            currLine = received_data.decode('utf-8').rstrip()
            if len(currLine) > 0:
                print_line('TASK-RX({})'.format(currLine), debug=True)
                pushLine(currLine)



# -----------------------------------------------------------------------------
#  Main loop
# -----------------------------------------------------------------------------

def opJustLogIt(cmdString):
    print_line('opJustLogIt({})'.format(cmdString), debug=True)

def processDebugLine(newLine):
    opJustLogIt(newLine)

def mainLoop():
    while True:             # Event Loop
        # process an incoming line - creates our windows as needed
        currLine = popLine()

        if len(currLine) > 0:
            print_line('DO-LINE({})'.format(currLine), debug=True)
            processDebugLine(currLine)



# -----------------------------------------------------------------------------
#  Main loop
# -----------------------------------------------------------------------------

# start our input task
_thread.start_new_thread(taskProcessInput, ( ))

# run our loop
try:
    mainLoop()

finally:
    # normal shutdown
    print_line('Done', info=True)
