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
from configparser import ConfigParser
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import sendgrid
from sendgrid.helpers.mail import Content, Email, Mail
from enum import Enum, unique

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

if False:
    # will be caught by python 2.7 to be illegal syntax
    print_line('Sorry, this script requires a python3 runtime environment.', file=sys.stderr)
    os._exit(1)

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

# the following enum EFI_* name order and starting value must be identical to that found in our gateway .spin2 object
FolderId = Enum('FolderId', [
     'EFI_VAR',
     'EFI_TMP',
     'EFI_CONTROL',
     'EFI_STATUS',
     'EFI_LOG',
     'EFI_MAIL',
     'EFI_PROC'], start=100)

#for folderId in FolderId:
#    print(folderId, folderId.value)

# the following enum FM_* name order and starting value must be identical to that found in our gateway .spin2 object
FileMode = Enum('FileMode', [
     'FM_READONLY',
     'FM_WRITE',
     'FM_WRITE_CREATE'], start=200)

#for fileMode in FileMode:
#    print(fileMode, fileMode.value)

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
parser.add_argument("-c", '--config_dir', help='set directory where config.ini is located', default=sys.path[0])
parse_args = parser.parse_args()

opt_verbose = parse_args.verbose
opt_debug = parse_args.debug
opt_useTestFile = parse_args.test
config_dir = parse_args.config_dir

print_line(script_info, info=True)
if opt_verbose:
    print_line('Verbose enabled', info=True)
if opt_debug:
    print_line('Debug enabled', debug=True)
if opt_useTestFile:
    print_line('TEST: debug stream is test file', debug=True)

# -----------------------------------------------------------------------------
#  Config File parsing
# -----------------------------------------------------------------------------
config = ConfigParser(delimiters=('=', ), inline_comment_prefixes=('#'))
config.optionxform = str
try:
    with open(os.path.join(config_dir, 'config.ini')) as config_file:
        config.read_file(config_file)
except IOError:
    print_line('No configuration file "config.ini"', error=True, sd_notify=True)
    sys.exit(1)

# default domain when hostname -f doesn't return it
#  load any override from config file
default_domain = ''
fallback_domain = config['Daemon'].get('fallback_domain', default_domain).lower()

# default daemon use folder locations
default_folder_tmp = '/tmp/P2-RPi-ioT-gateway'
default_folder_var = '/var/P2-RPi-ioT-gateway'
default_folder_control = '/var/P2-RPi-ioT-gateway/control'
default_folder_status = '/var/P2-RPi-ioT-gateway/status'
default_folder_log = '/var/log/P2-RPi-ioT-gateway/log'
default_folder_mail = '/var/P2-RPi-ioT-gateway/mail'
default_folder_proc = '/var/P2-RPi-ioT-gateway/proc'

# load any folder overrides from config file
folder_tmp = config['Daemon'].get('folder_tmp', default_folder_tmp)
folder_var = config['Daemon'].get('folder_var', default_folder_var)
folder_control = config['Daemon'].get('folder_control', default_folder_control)
folder_status = config['Daemon'].get('folder_status', default_folder_status)
folder_log = config['Daemon'].get('folder_log', default_folder_log)
folder_mail = config['Daemon'].get('folder_mail', default_folder_mail)
folder_proc = config['Daemon'].get('folder_proc', default_folder_proc)

# and set up dictionary so we can get path indexed by enum value
folderSpecByFolderId = {}
folderSpecByFolderId[FolderId.EFI_TMP] = folder_tmp
folderSpecByFolderId[FolderId.EFI_VAR] = folder_var
folderSpecByFolderId[FolderId.EFI_CONTROL] = folder_control
folderSpecByFolderId[FolderId.EFI_STATUS] = folder_status
folderSpecByFolderId[FolderId.EFI_LOG] = folder_log
folderSpecByFolderId[FolderId.EFI_MAIL] = folder_mail
folderSpecByFolderId[FolderId.EFI_PROC] = folder_proc

# load any sendgrid use and details from config file
default_api_key = ''
default_from_addr = ''

use_sendgrid = config['EMAIL'].getboolean('use_sendgrid', False)
sendgrid_api_key = config['EMAIL'].get('sendgrid_api_key', default_api_key)
sendgrid_from_addr = config['EMAIL'].get('sendgrid_from_addr', default_from_addr)
print_line('CONFIG: use sendgrid={}'.format(use_sendgrid), debug=True)
print_line('CONFIG: sendgrid_api_key=[{}]'.format(sendgrid_api_key), debug=True)
print_line('CONFIG: sendgrid_from_addr=[{}]'.format(sendgrid_from_addr), debug=True)



# -----------------------------------------------------------------------------
#  methods indetifying RPi hardware host
# -----------------------------------------------------------------------------
rpi_model = '??'
rpi_model_raw = '??'
rpi_linux_release = '??'
rpi_linux_version = '??'
rpi_hostname = '??'
rpi_fqdn = '??'

def idenitfyRPiHost():
    global rpi_model
    global rpi_model_raw
    global rpi_linux_release
    global rpi_linux_version
    global rpi_hostname
    global rpi_fqdn
    rpi_model, rpi_model_raw = getDeviceModel()
    rpi_linux_release = getLinuxRelease()
    rpi_linux_version = getLinuxVersion()
    rpi_hostname, rpi_fqdn = getHostnames()

def getDeviceModel():
    out = subprocess.Popen("/bin/cat /proc/device-tree/model | /bin/sed -e 's/\\x0//g'",
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, _ = out.communicate()
    model_raw = stdout.decode('utf-8')
    # now reduce string length (just more compact, same info)
    model = model_raw.replace('Raspberry ', 'R').replace(
        'i Model ', 'i 1 Model').replace('Rev ', 'r').replace(' Plus ', '+ ')

    print_line('rpi_model_raw=[{}]'.format(model_raw), debug=True)
    print_line('rpi_model=[{}]'.format(model), debug=True)
    return model, model_raw

def getLinuxRelease():
    out = subprocess.Popen("/bin/cat /etc/apt/sources.list | /bin/egrep -v '#' | /usr/bin/awk '{ print $3 }' | /bin/grep . | /usr/bin/sort -u",
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, _ = out.communicate()
    linux_release = stdout.decode('utf-8').rstrip()
    print_line('rpi_linux_release=[{}]'.format(linux_release), debug=True)
    return linux_release


def getLinuxVersion():
    out = subprocess.Popen("/bin/uname -r",
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, _ = out.communicate()
    linux_version = stdout.decode('utf-8').rstrip()
    print_line('rpi_linux_version=[{}]'.format(linux_version), debug=True)
    return linux_version


def getHostnames():
    out = subprocess.Popen("/bin/hostname -f",
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, _ = out.communicate()
    fqdn_raw = stdout.decode('utf-8').rstrip()
    print_line('fqdn_raw=[{}]'.format(fqdn_raw), debug=True)
    lcl_hostname = fqdn_raw
    if '.' in fqdn_raw:
        # have good fqdn
        nameParts = fqdn_raw.split('.')
        lcl_fqdn = fqdn_raw
        tmpHostname = nameParts[0]
    else:
        # missing domain, if we have a fallback apply it
        if len(fallback_domain) > 0:
            lcl_fqdn = '{}.{}'.format(fqdn_raw, fallback_domain)
        else:
            lcl_fqdn = lcl_hostname

    print_line('rpi_fqdn=[{}]'.format(lcl_fqdn), debug=True)
    print_line('rpi_hostname=[{}]'.format(lcl_hostname), debug=True)
    return lcl_hostname, lcl_fqdn

# -----------------------------------------------------------------------------
#  Maintain Runtime Configuration values
# -----------------------------------------------------------------------------
keyHwName = "hwName"
keyObjVer = "objVer"
#
keyEmailTo = "to"
keyEmailFrom = "fm"
keyEmailCC = "cc"
keyEmailBCC = "bc"
keyEmailSubj = "su"
keyEmailBody = "bo"
#
keySmsPhone = "phone"
keySmsMessage = "message"

configRequiredEmailKeys = [ keyEmailTo, keyEmailSubj, keyEmailBody ]

configOptionalEmailKeys =[ keyEmailFrom, keyEmailCC, keyEmailBCC ]

#  searchable list of keys
configKnownKeys = [ keyHwName, keyObjVer,
                   keyEmailTo, keyEmailFrom, keyEmailCC, keyEmailBCC, keyEmailSubj, keyEmailBody,
                   keySmsPhone, keySmsMessage ]

configDictionary = {}   # initially empty

def haveNeededEmailKeys():
    # check if we have a minimum set of email specs to be able to send. Return T/F here T means we can send!
    global configDictionary
    global configRequiredEmailKeys
    foundMinimumKeysStatus = True
    for key in configRequiredEmailKeys:
        if key not in configDictionary.keys():
            foundMinimumKeysStatus = False

    print_line('CONFIG-Dict: have email keys=[{}]'.format(foundMinimumKeysStatus), debug=True)
    return foundMinimumKeysStatus

def validateKey(name):
    # ensure a key we are trying to set/get is expect by this system
    #   generate warning if NOT
    if name not in configKnownKeys:
        print_line('CONFIG-Dict: Unexpected key=[{}]!!'.format(name), warning=True)

def setConfigNamedVarValue(name, value):
    # set a config value for name
    global configDictionary
    validateKey(name)   # warn if key isn't a know key
    foundKey = False
    if name in configDictionary.keys():
        oldValue = configDictionary[name]
        foundKey = True
    configDictionary[name] = value
    if foundKey and oldValue != value:
        print_line('CONFIG-Dict: [{}]=[{}]->[{}]'.format(name, oldValue, value), debug=True)
    else:
        print_line('CONFIG-Dict: [{}]=[{}]'.format(name, value), debug=True)

def getValueForConfigVar(name):
    # return a config value for name
    # print_line('CONFIG-Dict: get({})'.format(name), debug=True)
    validateKey(name)   # warn if key isn't a know key
    dictValue = ""
    if name in configDictionary.keys():
        dictValue = configDictionary[name]
        print_line('CONFIG-Dict: [{}]=[{}]'.format(name, dictValue), debug=True)
    else:
        print_line('CONFIG-Dict: [{}] NOT FOUND'.format(name, dictValue), warning=True)
    return dictValue

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

def taskProcessInput(ser):
    print_line('Thread: taskProcessInput() started', verbose=True)
    # process lies from serial or from test file
    if opt_useTestFile == True:
        test_file=open("charlie_rpi_debug.out", "r")
        lines = test_file.readlines()
        for currLine in lines:
            pushLine(currLine)
            #sleep(0.1)
    else:
        while True:
            received_data = ser.readline()              #read serial port
            currLine = received_data.decode('utf-8').rstrip()
            if len(currLine) > 0:
                print_line('TASK-RX({})'.format(currLine), debug=True)
                pushLine(currLine)


# -----------------------------------------------------------------------------
#  Email Handler
# -----------------------------------------------------------------------------

newLine = '\n'

def crateAndSendEmail(emailTo, emailFrom, emailSubj, emailTextLines):
    # send a email via the selected interface
    print_line('crateAndSendEmail to=[{}], from=[{}], subj=[{}], body=[{}]'.format(emailTo, emailFrom, emailSubj, emailTextLines), debug=True)
    #
    # build message footer
    # =================================
    #
    #  --
    #  Sent From: {objName} {objVer}
    #        Via: {daemonName} {daemonVer}
    #       Host: RPIName - os name, version
    # =================================
    footer = '\n\n--\n'
    objName = getValueForConfigVar(keyHwName)
    objVer = getValueForConfigVar(keyObjVer)
    footer += '  Sent From: {} v{}\n'.format(objName, objVer)
    footer += '        Via: {}\n'.format(script_info)
    # rpi_model_raw=[Raspberry Pi 3 Model B Plus Rev 1.3]
    # rpi_model=[RPi 3 Model B+ r1.3]
    # rpi_linux_release=[bullseye]
    # rpi_linux_version=[5.10.63-v7+]
    # fqdn_raw=[pip2iotgw]
    # rpi_fqdn=[pip2iotgw.home]
    # rpi_hostname=[pip2iotgw]
    footer += '       Host: {} - {}\n'.format(rpi_fqdn, rpi_model)
    footer += '    Running: Kernel v{} ({})\n'.format(rpi_linux_version, rpi_linux_release)

    body = ''
    for line in emailTextLines:
        body += '{}\n'.format(line)

    emailBody = body + footer

    if use_sendgrid:
        #
        # compose our email and send via our SendGrid account
        #  # ,
        sgCli = sendgrid.SendGridAPIClient(sendgrid_api_key)
        newEmail = Mail(from_email = sendgrid_from_addr,
                    to_emails = emailTo,
                    subject = emailSubj,
                    plain_text_content = emailBody)
        response = sgCli.client.mail.send.post(request_body=newEmail.get())

        #  included for debugging purposes
        print_line('SG status_code [{}]'.format(response.status_code), debug=True)
        print_line('SG body [{}]'.format(response.body), debug=True)
        print_line('SG headers [{}]'.format(response.headers), debug=True)
    else:
        #
        # compose our email and send using sendmail directly
        #
        msg = MIMEText(emailBody)  # failed attempt to xlate...
        if len(emailFrom) > 0:
            msg["From"] = emailFrom
        msg["To"] = emailTo
        msg["Subject"] = emailSubj
        mailProcess = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        # Both Python 2.X and 3.X
        mailProcess.communicate(msg.as_bytes() if sys.version_info >= (3,0) else msg.as_string())


def sendEmailFromConfig():
    # gather email details then create and send a email via the selected interface
    tmpTo =  getValueForConfigVar(keyEmailTo)
    tmpFrom = getValueForConfigVar(keyEmailFrom)
    tmpSubject = getValueForConfigVar(keyEmailSubj)
    tmpBody = getValueForConfigVar(keyEmailBody)
    # TODO: wire up BCC, CC ensure that multiple, To, Cc, and Bcc work too!
    # print_line('sendEmailFromConfig to=[{}], from=[{}], subj=[{}], body=[{}]'.format(tmpTo, tmpFrom, tmpSubject, tmpBody), debug=True)
    crateAndSendEmail(tmpTo, tmpFrom, tmpSubject, tmpBody)

# -----------------------------------------------------------------------------
#  Main loop
# -----------------------------------------------------------------------------
cmdIdentifyHW  = "ident:"
cmdSendEmail = "email-send:"
cmdSendSMS = "sms-send:"
cmdFileAccess = "file-access:"
cmdFileWrite = "file-write:"
cmdFileRead = "file-read:"

# file-access named parameters
keyFileAccDir = "dir"
keyFileAccMode = "mode"
keyFileAccFName = "fname"
fileAccessParmKeys = [ keyFileAccDir, keyFileAccMode, keyFileAccFName]



def getNameValuePairs(strRequest, cmdStr):
    # isolate name-value pairs found within {strRequest} (after removing prefix {cmdStr})
    rmdr = strRequest.replace(cmdStr,'')
    nameValuePairs = rmdr.split(parm_sep)
    print_line('getNameValuePairs nameValuePairs({})=({})'.format(len(nameValuePairs), nameValuePairs), debug=True)
    return nameValuePairs

def processNameValuePairs(nameValuePairsAr):
    # parse the name value pairs - return of dictionary of findings
    findingsDict = {}
    for nameValueStr in nameValuePairsAr:
        if '=' in nameValueStr:
            name,value = nameValueStr.split('=', 1)
            print_line('  [{}]=[{}]'.format(name, value), verbose=True)
            findingsDict[name] = value
        else:
            print_line('processNameValuePairs nameValueStr({})=({}) ! missing "=" !'.format(len(nameValueStr), nameValueStr), warning=True)
    return findingsDict

# global state parameter for building email
gatheringEmailBody = False
emailBodyTextAr = []

def processIncomingRequest(newLine, Ser):
    global gatheringEmailBody
    global emailBodyTextAr

    print_line('Incoming line({})=({})'.format(len(newLine), newLine), debug=True)

    if newLine.startswith(body_end):
        gatheringEmailBody = False
        print_line('Incoming emailBodyTextAr({})=[{}]'.format(len(emailBodyTextAr), emailBodyTextAr), verbose=True)
        setConfigNamedVarValue(keyEmailBody, emailBodyTextAr)
        # Send the email if we know enough to do so...
        if haveNeededEmailKeys() == True:
            sendEmailFromConfig()

    if gatheringEmailBody == True:
        bodyLinesAr = newLine.split('\\n')
        print_line('bodyLinesAr({})=[{}]'.format(len(bodyLinesAr), bodyLinesAr), verbose=True)
        emailBodyTextAr += bodyLinesAr

    if newLine.startswith(body_start):
        gatheringEmailBody = True
        emailBodyTextAr = []

    if newLine.startswith(cmdIdentifyHW):
        print_line('* HANDLE id P2 Hardware', info=True)
        nameValuePairs = getNameValuePairs(newLine, cmdIdentifyHW)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            # Record the hardware info for later use
            if len(findingsDict) > 0:
                for key in findingsDict:
                    setConfigNamedVarValue(key, findingsDict[key])
            else:
                print_line('processIncomingRequest nameValueStr({})=({}) ! missing hardware keys !'.format(len(newLine), newLine), warning=True)

    if newLine.startswith(cmdSendEmail):
        print_line('* HANDLE send email', info=True)
        nameValuePairs = getNameValuePairs(newLine, cmdSendEmail)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            if len(findingsDict) > 0:
                for key in findingsDict:
                    setConfigNamedVarValue(key, findingsDict[key])
            else:
                print_line('processIncomingRequest nameValueStr({})=({}) ! missing email params !'.format(len(newLine), newLine), warning=True)

    if newLine.startswith(cmdSendSMS):
        print_line('* HANDLE send SMS', info=True)
        nameValuePairs = getNameValuePairs(newLine, cmdSendSMS)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            if len(findingsDict) > 0:
                for key in findingsDict:
                    setConfigNamedVarValue(key, findingsDict[key])
            else:
                print_line('processIncomingRequest nameValueStr({})=({}) ! missing SMS params !'.format(len(newLine), newLine), warning=True)
            # TODO: now send the SMS

    if newLine.startswith(cmdFileAccess):
        print_line('* HANDLE send FIle Open-equiv', info=True)
        nameValuePairs = getNameValuePairs(newLine, cmdFileAccess)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            if len(findingsDict) > 0:
                # validate all keys exist
                bHaveAllKeys = True
                missingParmName = ''
                for requiredKey in fileAccessParmKeys:
                    if requiredKey not in findingsDict.keys():
                        HaveAllKeys = False
                        missingParmName = requiredKey
                        break
                if not bHaveAllKeys:
                    errorTxt = 'missing named parameter [{}]'.format(missingParmName)
                    sendValidationError(Ser, errorTxt)
                else:
                    # validate dir spec is valid
                    dirID = int(findingsDict[keyFileAccDir])
                    if dirID not in FolderId._value2member_map_:
                        errorTxt = 'bad parm dir={} - unknown folder ID'.format(dirID)
                        sendValidationError(Ser, "faccess", errorTxt)
                    else:
                        # validate dirId is valid
                        modeId = int(findingsDict[keyFileAccMode])
                        if modeId not in FileMode._value2member_map_:
                            errorTxt = 'bad parm mode={} - unknown file-mode ID'.format(modeId)
                            sendValidationError(Ser, "faccess", errorTxt)
                        else:
                            dirSpec = folderSpecByFolderId[FolderId(dirID)]
                            filename = findingsDict[keyFileAccFName]
                            filespec = os.path.join(dirSpec, filename + '.json')
                            bCanAccessStatus = True
                            # if file should exist ensure it does, report if not
                            if FileMode(modeId) == FileMode.FM_READONLY or FileMode(modeId) == FileMode.FM_WRITE:
                                # determine if filename exists in dir
                                if not os.path.exists(filespec):
                                    errorTxt = 'bad fname={} - file NOT found'.format(filename)
                                    sendValidationError(Ser, "faccess", errorTxt)
                                    bCanAccessStatus = False
                            if FileMode(modeId) == FileMode.FM_WRITE_CREATE:
                                if not os.path.exists(filespec):
                                    # let's create the file
                                    print_line('* create empty file [{}]'.format(filespec), verbose=True)
                                    open(filespec, 'a').close() # equiv to touch(1)
                            if bCanAccessStatus == True:
                                # return findings as response
                                sendValidationSuccess(Ser, "faccess", 9999)  # nonsense until we put code here
            else:
                print_line('processIncomingRequest nameValueStr({})=({}) ! missing FileAccess params !'.format(len(newLine), newLine), warning=True)

def sendValidationError(Ser, cmdPrefixStr, errorMessage):
    # format and send an error message via outgoing serial
    successStatus = False
    responseStr = '{}:status={},msg={}\n'.format(cmdPrefixStr, successStatus, errorMessage)
    newOutLine = responseStr.encode('utf-8')
    print_line('sendValidationError line({})=({})'.format(len(newOutLine), newOutLine), debug=True)
    Ser.write(newOutLine)

def sendValidationSuccess(Ser, cmdPrefixStr, returnValue):
    # format and send an error message via outgoing serial
    successStatus = True
    responseStr = '{}:status={},fileid={}\n'.format(cmdPrefixStr, successStatus, returnValue)
    newOutLine = responseStr.encode('utf-8')
    print_line('sendValidationSuccess line({})=({})'.format(len(newOutLine), newOutLine), debug=True)
    Ser.write(newOutLine)

def processInput(Ser):
    while True:             # get Loop (if something, get another)
        # process an incoming line - creates our windows as needed
        currLine = popLine()

        if len(currLine) > 0:
            processIncomingRequest(currLine, Ser)
        else:
            break

def genSomeOutput(Ser):
    newOutLine = b'Hello p2\n'
    print_line('genSomeOutput line({})=({})'.format(len(newOutLine), newOutLine), debug=True)
    ser.write(newOutLine)

def mainLoop(ser):
    while True:             # Event Loop
        processInput(ser)
        # genSomeOutput(ser)
        sleep(0.2)  # pause 2/10ths of second


# -----------------------------------------------------------------------------
#  Main loop
# -----------------------------------------------------------------------------

# start our input task
ser = serial.Serial ("/dev/serial0", 1000000, timeout=1)    #Open port with baud rate & timeout

_thread.start_new_thread(taskProcessInput, ( ser, ))

idenitfyRPiHost()

# run our loop
try:
    mainLoop(ser)

finally:
    # normal shutdown
    print_line('Done', info=True)



# ser = serial.Serial ("/dev/serial0", 1000000, timeout=1)    #Open port with baud rate & timeout
# while True:
#     received_data = ser.read()              #read serial port
#     sleep(0.03)
#     data_left = ser.inWaiting()             #check for remaining byte
#     received_data += ser.read(data_left)
#     print (received_data)                   #print received data
#     print_line('TEST-LOOP line({})=[{}]'.format(len(received_data), received_data), debug=True)
#     ser.write(received_data)                #transmit data serially
