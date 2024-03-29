#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _thread
from datetime import datetime
from math import e
from time import time, sleep, localtime, strftime
import os
import subprocess
import sys
import os.path
import json
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
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

if False:
    # will be caught by python 2.7 to be illegal syntax
    print_line('Sorry, this script requires a python3 runtime environment.', file=sys.stderr)
    os._exit(1)

# v0.0.1 - awaken email send
# v0.0.2 - add file handling

script_version  = "0.0.3"
script_name     = 'P2-RPi-ioT-gw-daemon.py'
script_info     = '{} v{}'.format(script_name, script_version)
project_name    = 'P2-RPi-IoT-gw'
project_url     = 'https://github.com/ironsheep/P2-RPi-IoT-gateway'

# -----------------------------------------------------------------------------
# the BELOW are identical to that found in our gateway .spin2 object
#   (!!!they must be kept in sync!!!)
# -----------------------------------------------------------------------------

# markers found within the data arriving from the P2 but likely will NOT be found in normal user data sent by the P2
parm_sep    = '^|^'
body_start  = 'email|Start'
body_end    = 'email|End'

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
     'FM_WRITE_CREATE',
     'FM_LISTEN'], start=200)

#for fileMode in FileMode:
#    print(fileMode, fileMode.value)

# -----------------------------------------------------------------------------
# the ABOVE are identical to that found in our gateway .spin2 object
# -----------------------------------------------------------------------------
#   Colorama constants:
#  Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#  Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#  Style: DIM, NORMAL, BRIGHT, RESET_ALL
#
# Logging function
def print_line(text, error=False, warning=False, info=False, verbose=False, debug=False, console=True):
    timestamp = strftime('%Y-%m-%d %H:%M:%S', localtime())
    if console:
        if error:
            print(Fore.RED + Style.BRIGHT + '[{}] '.format(timestamp) + Style.NORMAL + '{}'.format(text) + Style.RESET_ALL, file=sys.stderr)
        elif warning:
            print(Fore.YELLOW + Style.BRIGHT + '[{}] '.format(timestamp) + Style.NORMAL + '{}'.format(text) + Style.RESET_ALL)
        elif info or verbose:
            if verbose:
                # conditional verbose output...
                if opt_verbose:
                    print(Fore.GREEN + '[{}] '.format(timestamp) + Fore.YELLOW  + '- ' + '{}'.format(text) + Style.RESET_ALL)
            else:
                # info...
                print(Fore.MAGENTA + '[{}] '.format(timestamp) + Fore.WHITE  + '- ' + '{}'.format(text) + Style.RESET_ALL)
        elif debug:
            # conditional debug output...
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
    print_line('Verbose enabled', verbose=True)
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
default_folder_control = '/var/www/html/P2-RPi-ioT-gateway/control'
default_folder_status = '/var/P2-RPi-ioT-gateway/status'
default_folder_log = '/var/log/P2-RPi-ioT-gateway'
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
#  methods indentifying RPi host hardware/software
# -----------------------------------------------------------------------------

#  object that provides access to information about the RPi on which we are running
class RPiHostInfo:

    def getDeviceModel(self):
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

    def getLinuxRelease(self):
        out = subprocess.Popen("/bin/cat /etc/apt/sources.list | /bin/egrep -v '#' | /usr/bin/awk '{ print $3 }' | /bin/grep . | /usr/bin/sort -u",
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        stdout, _ = out.communicate()
        linux_release = stdout.decode('utf-8').rstrip()
        print_line('rpi_linux_release=[{}]'.format(linux_release), debug=True)
        return linux_release


    def getLinuxVersion(self):
        out = subprocess.Popen("/bin/uname -r",
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        stdout, _ = out.communicate()
        linux_version = stdout.decode('utf-8').rstrip()
        print_line('rpi_linux_version=[{}]'.format(linux_version), debug=True)
        return linux_version


    def getHostnames(self):
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

#  object that provides access to gateway runtime confiration data
class RuntimeConfig:
    # Host RPi keys
    keyRPiModel = "Model"
    keyRPiMdlFull = "ModelFull"
    keyRPiRel = "OsRelease"
    keyRPiVer = "OsVersion"
    keyRPiName = "Hostname"
    keyRPiFqdn = "FQDN"

    # P2 Hardware/Application keys
    keyHwName = "hwName"
    keyObjVer = "objVer"

    # email keys
    keyEmailTo = "to"
    keyEmailFrom = "fm"
    keyEmailCC = "cc"
    keyEmailBCC = "bc"
    keyEmailSubj = "su"
    keyEmailBody = "bo"

    # sms keys
    keySmsPhone = "phone"
    keySmsMessage = "message"

    configRequiredEmailKeys = [ keyEmailTo, keyEmailSubj, keyEmailBody ]

    configOptionalEmailKeys =[ keyEmailFrom, keyEmailCC, keyEmailBCC ]

    #  searchable list of keys
    configKnownKeys = [ keyHwName, keyObjVer,
                        keyRPiModel, keyRPiMdlFull, keyRPiRel, keyRPiVer, keyRPiName, keyRPiFqdn,
                        keyEmailTo, keyEmailFrom, keyEmailCC, keyEmailBCC, keyEmailSubj, keyEmailBody,
                        keySmsPhone, keySmsMessage ]

    configDictionary = {}   # initially empty

    def haveNeededEmailKeys(self):
        # check if we have a minimum set of email specs to be able to send. Return T/F here T means we can send!
        global configDictionary
        global configRequiredEmailKeys
        foundMinimumKeysStatus = True
        for key in self.configRequiredEmailKeys:
            if key not in self.configDictionary.keys():
                foundMinimumKeysStatus = False

        print_line('CONFIG-Dict: have email keys=[{}]'.format(foundMinimumKeysStatus), debug=True)
        return foundMinimumKeysStatus

    def validateKey(self, name):
        # ensure a key we are trying to set/get is expect by this system
        #   generate warning if NOT
        if name not in self.configKnownKeys:
            print_line('CONFIG-Dict: Unexpected key=[{}]!!'.format(name), warning=True)

    def setConfigNamedVarValue(self, name, value):
        # set a config value for name
        global configDictionary
        self.validateKey(name)   # warn if key isn't a know key
        foundKey = False
        if name in self.configDictionary.keys():
            oldValue = self.configDictionary[name]
            foundKey = True
        self.configDictionary[name] = value
        if foundKey and oldValue != value:
            print_line('CONFIG-Dict: [{}]=[{}]->[{}]'.format(name, oldValue, value), debug=True)
        else:
            print_line('CONFIG-Dict: [{}]=[{}]'.format(name, value), debug=True)

    def getValueForConfigVar(self, name):
        # return a config value for name
        # print_line('CONFIG-Dict: get({})'.format(name), debug=True)
        self.validateKey(name)   # warn if key isn't a know key
        dictValue = ""
        if name in self.configDictionary.keys():
            dictValue = self.configDictionary[name]
            print_line('CONFIG-Dict: [{}]=[{}]'.format(name, dictValue), debug=True)
        else:
            print_line('CONFIG-Dict: [{}] NOT FOUND'.format(name, dictValue), warning=True)
        return dictValue

# -----------------------------------------------------------------------------
#  Maintain our list of file handles requested by the P2
# -----------------------------------------------------------------------------

#  Object used to track gateway files
class FileDetails:
    # (declare class variables here)

    # create a new instance with all details given!
    def __init__(self, fileName, fileMode, dirSpec):
        # (declare instance variables here)
        self.fileName = fileName + '.json'
        self.fileMode = fileMode
        self.dirSpec = dirSpec
        self.fileSpec = os.path.join(self.dirSpec, self.fileName)

# object tracking the gateway files providing access via handles
class FileHandleStore:
    # (declare class variables here)

    def __init__(self):
        # (declare instance variables here)
        self.dctLiveFiles = {}  # runtime hash of known files (not persisted)
        self.dctWatchedFiles = {}  # runtime hash of files being watched (not persisted)
        self.nNextFileId = 1  # initial collId value (1 - 99,999)

    def handleStringForFile(self, fileName, fileMode, dirSpec):
        # create and return a new fileIdKey for this new file and save file details with the key
        #  TODO: detect open-assoc of same file details (only 1 path/filename on file, please)
        fileIdKey = self.nextFileIdKey()
        desiredFileId = int(fileIdKey)
        self.dctLiveFiles[fileIdKey] = FileDetails(fileName, fileMode, dirSpec)
        return desiredFileId

    def handleForFSpec(self, possibleFSpec):
        # create and return a new fileIdKey for this new file and save file details with the key
        #  TODO: detect open-assoc of same file details (only 1 path/filename on file, please)
        desiredFileId = 0
        if len(self.dctLiveFiles.keys()) > 0:
            for fileIdKey in self.dctLiveFiles.keys():
                possibleFileDetails = self.dctLiveFiles[fileIdKey]
                if possibleFileDetails.fileSpec == possibleFSpec:
                    desiredFileId = int(fileIdKey)
                    break   # we have our answer, abort loop
        return desiredFileId

    def addWatchForHandle(self, possibleFileId):
        # record that we are now watching this file!
        fileIdKey = self.keyForFileId(possibleFileId)
        desiredFileDetails = self.dctLiveFiles[fileIdKey]
        self.dctWatchedFiles[fileIdKey] = desiredFileDetails

    def isWatchedFSpec(self, possibleFSpec):
        # return T/F where T means a watch of {possibleFSpec} is requested
        bChangeStatus = False
        if len(self.dctWatchedFiles.keys()) > 0:
            for fileIdKey in self.dctWatchedFiles.keys():
                possibleFileDetails = self.dctWatchedFiles[fileIdKey]
                if possibleFileDetails.fileSpec == possibleFSpec:
                    bChangeStatus = True
                    break   # we have our answer, abort loop
        return bChangeStatus

    def fpsecForHandle(self, possibleFileId):
        # return the fileSpec associated with the given collId
        fileIdKey = self.keyForFileId(possibleFileId)
        desiredFileDetails = self.dctLiveFiles[fileIdKey]
        return desiredFileDetails.fileSpec

    def nextFileIdKey(self):
      # return the next legal collId key [00001 -> 99999]
      fileIdKey = self.keyForFileId(self.nNextFileId)
      if fileIdKey in self.dctLiveFiles.keys():
        print_line('ERROR[Internal] FileHandleStore: attempted re-use of fileIdKey=[{}]'.format(fileIdKey),error=True)
      if(self.nNextFileId < 99999):  # limit to 1-99,999
        self.nNextFileId = self.nNextFileId + 1
      return fileIdKey

    def isValidHandle(self, possibleFileId):
        # return T/F where T means this key represents an actual file
        fileIdKey = self.keyForFileId(possibleFileId)
        validationStatus = True
        if not fileIdKey in self.dctLiveFiles.keys():
            validationStatus = False
        return validationStatus

    def keyForFileId(self, possibleFileId):
        # return file id as 5-char string
        desiredFileIdStr = '{:05d}'.format(int(possibleFileId))
        return desiredFileIdStr

# -----------------------------------------------------------------------------
#  methods for filesystem watching
# -----------------------------------------------------------------------------

# object that does the watching
class FileSystemWatcher:
    # (declare class variables here)

    def __init__(self, folderName):
        # (declare instance variables here)
        self.observer = Observer()
        self.DIRECTORY_TO_WATCH = folderName

    def run(self):
        print_line('Thread: FileSystemWatcher() started', verbose=True)
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        try:
            while True:
                sleep(5)
        except Exception as e:
            self.observer.stop()
            print_line('!!! FileSystemWatcher: Exception: {}'.format(e), error=True)

        self.observer.join()

# object that takes action based on file/dir changed notifications
class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        print_line('- FileSystemEventHandler: event=[{}]'.format(event), debug=True)
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print_line("Received FileCreate event - [{}]".format(event.src_path), debug=True)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print_line("Received FileModified event - [{}]".format(event.src_path), debug=True)
            reportFileChanged(event.src_path)


# -----------------------------------------------------------------------------
#  Circular queue for serial input lines & serial listener
# -----------------------------------------------------------------------------

# object which is a queue of text lines
#  these arrive at a rate different from our handling them rate
#  so we put them in a queue while they wait to be handled
class RxLineQueue:
    # (declare class variables here)

    def __init__(self):
        # (declare instance variables here)
        self.lineBuffer = deque()

    def pushLine(self, newLine):
        self.lineBuffer.append(newLine)
        # show debug every 100 lines more added
        if len(self.lineBuffer) % 100 == 0:
            print_line('- lines({})'.format(len(self.lineBuffer)),debug=True)

    def popLine(self):
        oldestLine = ''
        if len(self.lineBuffer) > 0:
            oldestLine = self.lineBuffer.popleft()
        return oldestLine


# -----------------------------------------------------------------------------
#  TASK: dedicated serial listener
# -----------------------------------------------------------------------------

def taskSerialListener(serPort):
    global queueRxLines
    print_line('Thread: taskSerialListener() started', verbose=True)
    # process lies from serial or from test file
    if opt_useTestFile == True:
        test_file=open("charlie_rpi_debug.out", "r")
        lines = test_file.readlines()
        for currLine in lines:
            queueRxLines.pushLine(currLine)
            #sleep(0.1)
    else:
        while True:
            received_data = serPort.readline()              #read serial port
            if len(received_data) > 0:
                print_line('TASK-RX rxD({})=({})'.format(len(received_data),received_data), debug=True)
                currLine = received_data.decode('utf-8', 'replace').rstrip()
                #print_line('TASK-RX line({}=[{}]'.format(len(currLine), currLine), debug=True)
                queueRxLines.pushLine(currLine)


# -----------------------------------------------------------------------------
#  Email Handler
# -----------------------------------------------------------------------------

newLine = '\n'

def createAndSendEmail(emailTo, emailFrom, emailSubj, emailTextLines):
    # send a email via the selected interface
    print_line('createAndSendEmail to=[{}], from=[{}], subj=[{}], body=[{}]'.format(emailTo, emailFrom, emailSubj, emailTextLines), debug=True)
    #
    # build message footer
    # =================================
    #
    #  --
    #  Sent From: {objName} {objVer}
    #        Via: {daemonName} {daemonVer}
    #       Host: {RPiName} - {osName}, {osVersion}
    # =================================
    footer = '\n\n--\n'
    objName = runtimeConfig.getValueForConfigVar(runtimeConfig.keyHwName)
    objVer = runtimeConfig.getValueForConfigVar(runtimeConfig.keyObjVer)
    footer += '  Sent From: {} v{}\n'.format(objName, objVer)
    footer += '        Via: {}\n'.format(script_info)
    footer += '       Host: {} - {}\n'.format(rpi_fqdn, rpi_model)
    footer += '    Running: Kernel v{} ({})\n'.format(rpi_linux_version, rpi_linux_release)
    # format the body text
    body = ''
    for line in emailTextLines:
        body += '{}\n'.format(line)
    # then append our footer
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
    tmpTo =  runtimeConfig.getValueForConfigVar(runtimeConfig.keyEmailTo)
    tmpFrom = runtimeConfig.getValueForConfigVar(runtimeConfig.keyEmailFrom)
    tmpSubject = runtimeConfig.getValueForConfigVar(runtimeConfig.keyEmailSubj)
    tmpBody = runtimeConfig.getValueForConfigVar(runtimeConfig.keyEmailBody)
    # TODO: wire up BCC, CC ensure that multiple, To, Cc, and Bcc work too!
    # print_line('sendEmailFromConfig to=[{}], from=[{}], subj=[{}], body=[{}]'.format(tmpTo, tmpFrom, tmpSubject, tmpBody), debug=True)
    createAndSendEmail(tmpTo, tmpFrom, tmpSubject, tmpBody)

# -----------------------------------------------------------------------------
#  Main loop
# -----------------------------------------------------------------------------
# commands from P2
cmdIdentifyHW  = "ident:"
cmdSendEmail = "email-send:"
cmdSendSMS = "sms-send:"
cmdFileAccess = "file-access:"
cmdFileWrite = "file-write:"
cmdFileRead = "file-read:"
cmdListFolder = "folder-list:"
cmdListKeys = "key-list:"
cmdTestSerial = "test:"

# serial test named parameters
keyTestReset = "reset"  # T/F where T means start count at zero
keyTestMsg = "msg"  # T/F where T means start count at zero

testSerialParmKeys = [ keyTestReset, keyTestMsg ]

# file-access named parameters
keyFileAccDir = "dir"
keyFileAccMode = "mode"
keyFileAccFName = "cname"
fileAccessParmKeys = [ keyFileAccDir, keyFileAccMode, keyFileAccFName ]

# file-write, read named parameters
keyFileFileID = "cid"
keyFileVarNm = "key"
keyFileVarVal = "val"
fileWriteParmKeys = [ keyFileFileID, keyFileVarNm, keyFileVarVal ]
fileReadParmKeys = [ keyFileFileID, keyFileVarNm ]

# folder list named parameters
folderListParmKeys = [ keyFileAccDir ]
keyListParmKeys = [ keyFileFileID ]


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
            print_line('  [{}]=[{}]'.format(name, value), debug=True)
            findingsDict[name] = value
        else:
            print_line('processNameValuePairs nameValueStr({})=({}) ! missing "=" !'.format(len(nameValueStr), nameValueStr), warning=True)
    return findingsDict

# global state parameter for building email
gatheringEmailBody = False
emailBodyTextAr = []
serTestTxCount = 0
serTestRxCount = 0
serTestErrCount = 0

def processIncomingRequest(newLine, serPort):
    global gatheringEmailBody
    global emailBodyTextAr
    global serTestTxCount
    global serTestRxCount
    global serTestErrCount

    print_line('Incoming line({})=[{}]'.format(len(newLine), newLine), debug=True)

    if newLine.startswith(body_end):
        gatheringEmailBody = False
        print_line('Incoming emailBodyTextAr({})=[{}]'.format(len(emailBodyTextAr), emailBodyTextAr), debug=True)
        runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyEmailBody, emailBodyTextAr)
        # Send the email if we know enough to do so...
        if runtimeConfig.haveNeededEmailKeys() == True:
            sendEmailFromConfig()
            sendValidationSuccess(serPort, "email", "", "")

    elif gatheringEmailBody == True:
        bodyLinesAr = newLine.split('\\n')
        print_line('bodyLinesAr({})=[{}]'.format(len(bodyLinesAr), bodyLinesAr), debug=True)
        emailBodyTextAr += bodyLinesAr

    elif newLine.startswith(body_start):
        gatheringEmailBody = True
        emailBodyTextAr = []

    elif newLine.startswith(cmdIdentifyHW):
        print_line('* HANDLE id P2 Hardware', verbose=True)
        nameValuePairs = getNameValuePairs(newLine, cmdIdentifyHW)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            # Record the hardware info for later use
            if len(findingsDict) > 0:
                p2ProcDict = {}
                for key in findingsDict:
                    runtimeConfig.setConfigNamedVarValue(key, findingsDict[key])
                    p2ProcDict[key] = findingsDict[key]
                # now write to our P2 Proc file as well
                p2Name = runtimeConfig.getValueForConfigVar(runtimeConfig.keyHwName).replace(' - ', '-').replace(' ', '-')
                procFspec = os.path.join(folder_proc, 'P2-{}.json'.format(p2Name))
                writeJsonFile(procFspec, p2ProcDict)
                sendValidationSuccess(serPort, "fident", "", "")
            else:
                print_line('processIncomingRequest nameValueStr({})=({}) ! missing hardware keys !'.format(len(newLine), newLine), warning=True)

    elif newLine.startswith(cmdTestSerial):
        print_line('* HANDLE id P2 Hardware', verbose=True)
        nameValuePairs = getNameValuePairs(newLine, cmdTestSerial)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            if len(findingsDict) > 0:
                # validate all keys exist
                bHaveAllKeys = True
                missingParmName = ''
                for requiredKey in testSerialParmKeys:
                    if requiredKey not in findingsDict.keys():
                        HaveAllKeys = False
                        missingParmName = requiredKey
                        break
                if not bHaveAllKeys:
                    errorTxt = 'missing folder-list named parameter [{}]'.format(missingParmName)
                    sendValidationError(serPort, "stest", errorTxt)
                else:
                    # validate reset and take action
                    shouldReset = findingsDict[keyTestReset]
                    if shouldReset.lower() != 'true' and shouldReset.lower() != 'false':
                        errorTxt = 'Invalid [{}] value [{}]'.format(missingParmName, shouldReset)
                        sendValidationError(serPort, "stest", errorTxt)
                    else:
                        if shouldReset.lower() == 'true':
                            serTestRxCount = 0
                            serTestTxCount = 0
                            serTestErrCount = 0
                        rxStr = findingsDict[keyTestMsg]
                        compRxStr = genNextRxString(serTestRxCount)
                        serTestRxCount += 1
                        print_line('TEST: rx=[{}] == [{}] ??'.format(rxStr, compRxStr), debug=True)
                        if rxStr != compRxStr:
                            serTestErrCount += 1
                        compTxStr = genNextTxString(serTestTxCount)
                        serTestTxCount += 1
                        checkMsg = '{}{}msg={}'.format(serTestErrCount, parm_sep, compTxStr)
                        sendValidationSuccess(serPort, "stest", "ct", checkMsg)

    elif newLine.startswith(cmdListFolder):
        print_line('* HANDLE list collections', verbose=True)
        nameValuePairs = getNameValuePairs(newLine, cmdListFolder)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            if len(findingsDict) > 0:
                # validate all keys exist
                bHaveAllKeys = True
                missingParmName = ''
                for requiredKey in folderListParmKeys:
                    if requiredKey not in findingsDict.keys():
                        HaveAllKeys = False
                        missingParmName = requiredKey
                        break
                if not bHaveAllKeys:
                    errorTxt = 'missing folder-list named parameter [{}]'.format(missingParmName)
                    sendValidationError(serPort, "folist", errorTxt)
                else:
                    # validate dirID is valid Enum number
                    dirID = int(findingsDict[keyFileAccDir])
                    if dirID not in FolderId._value2member_map_:    # in list of valid Enum numbers?
                        errorTxt = 'bad parm dir={} - unknown folder ID'.format(dirID)
                        sendValidationError(serPort, "folist", errorTxt)
                    else:
                        # good request now list all files in dir
                        dirSpec = folderSpecByFolderId[FolderId(dirID)]
                        filesAr = os.listdir(dirSpec)
                        print_line('processIncomingRequest filesAr({})=({})'.format(len(filesAr), filesAr), debug=True)
                        fileBaseNamesAr = []
                        fnameLst = ''
                        fnameCt = len(filesAr)
                        resultStr = ''
                        if fnameCt > 0:
                            # have 1 or more files
                            for filename in filesAr:
                                if '.json' in filename:
                                    fbasename = filename.replace('.json','')
                                    fileBaseNamesAr.append(fbasename)
                            fnameLst = ','.join(fileBaseNamesAr)
                            resultStr = '{}{}names={}'.format(fnameCt, parm_sep, fnameLst)
                        else:
                            # have NO files in dir
                            resultStr = '{}'.format(fnameCt)
                        sendValidationSuccess(serPort, "folist", "ct", resultStr)
        else:
            print_line('processIncomingRequest nameValueStr({})=({}) ! missing list files params !'.format(len(newLine), newLine), warning=True)

    elif newLine.startswith(cmdListKeys):
        print_line('* HANDLE list keys in collection', verbose=True)
        nameValuePairs = getNameValuePairs(newLine, cmdListKeys)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            if len(findingsDict) > 0:
                # validate all keys exist
                bHaveAllKeys = True
                missingParmName = ''
                for requiredKey in keyListParmKeys:
                    if requiredKey not in findingsDict.keys():
                        HaveAllKeys = False
                        missingParmName = requiredKey
                        break
                if not bHaveAllKeys:
                    errorTxt = 'missing keys-list named parameter [{}]'.format(missingParmName)
                    sendValidationError(serPort, "kylist", errorTxt)
                else:
                    # validate dirID is valid Enum number
                    fileIdStr = findingsDict[keyFileFileID]
                    if not fileHandles.isValidHandle(fileIdStr):
                        errorTxt = 'BAD file handle [{}]'.format(fileIdStr)
                        sendValidationError(serPort, "kylist", errorTxt)
                    else:
                        fspec = fileHandles.fpsecForHandle(fileIdStr)
                        # good request now list all keys in collection
                        filesize = os.path.getsize(fspec)
                        fileDict = {}   # start empty
                        keysAr = []
                        if filesize > 0:    # if we have existing content, preload it
                            with open(fspec, "r") as read_file:
                                fileDict = json.load(read_file)
                                keysAr = fileDict.keys()
                        print_line('processIncomingRequest keysAr({})=({})'.format(len(keysAr), keysAr), debug=True)
                        fileBaseNamesAr = []
                        keyNameLst = ''
                        keyCt = len(keysAr)
                        resultStr = ''
                        if keyCt > 0:
                            # have 1 or more files
                            keyNameLst = ','.join(keysAr)
                            resultStr = '{}{}names={}'.format(keyCt, parm_sep, keyNameLst)
                        else:
                            # have NO files in dir
                            resultStr = '{}'.format(keyCt)
                        sendValidationSuccess(serPort, "kylist", "ct", resultStr)
        else:
            print_line('processIncomingRequest nameValueStr({})=({}) ! missing list files params !'.format(len(newLine), newLine), warning=True)

    elif newLine.startswith(cmdSendEmail):
        print_line('* HANDLE send email', verbose=True)
        nameValuePairs = getNameValuePairs(newLine, cmdSendEmail)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            if len(findingsDict) > 0:
                for key in findingsDict:
                    runtimeConfig.setConfigNamedVarValue(key, findingsDict[key])
            else:
                print_line('processIncomingRequest nameValueStr({})=({}) ! missing email params !'.format(len(newLine), newLine), warning=True)

    elif newLine.startswith(cmdSendSMS):
        print_line('* HANDLE send SMS', verbose=True)
        nameValuePairs = getNameValuePairs(newLine, cmdSendSMS)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            if len(findingsDict) > 0:
                for key in findingsDict:
                    runtimeConfig.setConfigNamedVarValue(key, findingsDict[key])
            else:
                print_line('processIncomingRequest nameValueStr({})=({}) ! missing SMS params !'.format(len(newLine), newLine), warning=True)
            # TODO: now send the SMS

    elif newLine.startswith(cmdFileWrite):
        print_line('* HANDLE File WRITE', verbose=True)
        nameValuePairs = getNameValuePairs(newLine, cmdFileWrite)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            if len(findingsDict) > 0:
                # validate all keys exist
                bHaveAllKeys = True
                missingParmName = ''
                for requiredKey in fileWriteParmKeys:
                    if requiredKey not in findingsDict.keys():
                        HaveAllKeys = False
                        missingParmName = requiredKey
                        break
                if not bHaveAllKeys:
                    errorTxt = 'missing file-write named parameter [{}]'.format(missingParmName)
                    sendValidationError(serPort, "fwrite", errorTxt)
                else:
                    fileIdStr = findingsDict[keyFileFileID]
                    if not fileHandles.isValidHandle(fileIdStr):
                        errorTxt = 'BAD write file handle [{}]'.format(fileIdStr)
                        sendValidationError(serPort, "fwrite", errorTxt)
                    else:
                        fspec = fileHandles.fpsecForHandle(fileIdStr)
                        varKey = findingsDict[keyFileVarNm]
                        varValue = findingsDict[keyFileVarVal]
                        # load json file
                        filesize = os.path.getsize(fspec)
                        fileDict = {}   # start empty
                        if filesize > 0:    # if we have existing content, preload it
                            with open(fspec, "r") as read_file:
                                fileDict = json.load(read_file)
                        # replace key-value pair (or add it)
                        fileDict[varKey] = varValue
                        # write the file
                        writeJsonFile(fspec, fileDict)
                        # report our operation success to P2 (status only)
                        sendValidationSuccess(serPort, "fwrite", "", "")
            else:
                print_line('processIncomingRequest nameValueStr({})=({}) ! missing file-write params !'.format(len(newLine), newLine), warning=True)
            # TODO: now write the file

    elif newLine.startswith(cmdFileRead):
        print_line('* HANDLE File READ', verbose=True)
        nameValuePairs = getNameValuePairs(newLine, cmdFileRead)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            if len(findingsDict) > 0:
                # validate all keys exist
                bHaveAllKeys = True
                missingParmName = ''
                for requiredKey in fileReadParmKeys:
                    if requiredKey not in findingsDict.keys():
                        HaveAllKeys = False
                        missingParmName = requiredKey
                        break
                if not bHaveAllKeys:
                    errorTxt = 'missing file-read named parameter [{}]'.format(missingParmName)
                    sendValidationError(serPort, "fread", errorTxt)
                else:
                    fileIdStr = findingsDict[keyFileFileID]
                    if not fileHandles.isValidHandle(fileIdStr):
                        errorTxt = 'BAD file handle [{}]'.format(fileIdStr)
                        sendValidationError(serPort, "fread", errorTxt)
                    else:
                        fspec = fileHandles.fpsecForHandle(fileIdStr)
                        varKey = findingsDict[keyFileVarNm]
                        # load json file
                        with open(fspec, "r") as read_file:
                            fileDict = json.load(read_file)
                        if not varKey in fileDict.keys():
                            errorTxt = 'BAD Key - Key not found [{}]'.format(varKey)
                            sendValidationError(serPort, "fread", errorTxt)
                        else:
                            desiredValue = fileDict[varKey]
                            # report our operation success to P2 (and send value read from file)
                            sendValidationSuccess(serPort, "fread", "varVal", desiredValue)
            else:
                print_line('processIncomingRequest nameValueStr({})=({}) ! missing file-read params !'.format(len(newLine), newLine), warning=True)
            # TODO: now read from the file

    elif newLine.startswith(cmdFileAccess):
        print_line('* HANDLE File Open-equiv', verbose=True)
        bNeedFileWatch = False
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
                    sendValidationError(serPort, "faccess", errorTxt)
                else:
                    # validate dirID is valid Enum number
                    dirID = int(findingsDict[keyFileAccDir])
                    if dirID not in FolderId._value2member_map_:    # in list of valid Enum numbers?
                        errorTxt = 'bad parm dir={} - unknown folder ID'.format(dirID)
                        sendValidationError(serPort, "faccess", errorTxt)
                    else:
                        # validate modeId is valid Enum number
                        modeId = int(findingsDict[keyFileAccMode])
                        if modeId not in FileMode._value2member_map_:    # in list of valid Enum numbers?
                            errorTxt = 'bad parm mode={} - unknown file-mode ID'.format(modeId)
                            sendValidationError(serPort, "faccess", errorTxt)
                        else:
                            dirSpec = folderSpecByFolderId[FolderId(dirID)]
                            filename = findingsDict[keyFileAccFName]
                            filespec = os.path.join(dirSpec, filename + '.json')
                            bCanAccessStatus = True
                            # if file should exist ensure it does, report if not
                            if FileMode(modeId) == FileMode.FM_READONLY or FileMode(modeId) == FileMode.FM_WRITE:
                                # P2 wants to access read/write an existing file
                                # determine if filename exists in dir
                                if not os.path.exists(filespec):
                                    # if it doesn't exist report the error!
                                    print_line('ERROR file named=[{}] not found fspec=[{}]'.format(filename, filespec), debug=True)
                                    errorTxt = 'bad fname={} - file NOT found'.format(filename)
                                    sendValidationError(serPort, "faccess", errorTxt)
                                    bCanAccessStatus = False
                            elif FileMode(modeId) == FileMode.FM_WRITE_CREATE:
                                # P2 will write to file, so create empty if doesn't exist
                                if not os.path.exists(filespec):
                                    # let's create the file
                                    print_line('* create empty file [{}]'.format(filespec), verbose=True)
                                    open(filespec, 'a').close() # equiv to touch(1)
                            elif FileMode(modeId) == FileMode.FM_LISTEN:
                                # P2 wants to be notified of content changes to this file!
                                # first, warn if this is not in control DIR!
                                if FolderId(dirID) != FolderId.EFI_CONTROL:
                                    print_line('ERROR attempt to watch file named=[{}] not in /control/ folder. Folder=[{}]'.format(filename, FolderId(dirID)), error=True)
                                    errorTxt = 'bad fname={} not in /control/! folder={}'.format(filename, FolderId(dirID))
                                    sendValidationError(serPort, "faccess", errorTxt)
                                    bCanAccessStatus = False
                                else:
                                    # Register need to report changes!
                                    bNeedFileWatch = True
                            if bCanAccessStatus == True:
                                # return findings as response
                                newFileIdStr = fileHandles.handleStringForFile(filename, FileMode(modeId), dirSpec)
                                if bNeedFileWatch:
                                    # activate our file watching!
                                    fileHandles.addWatchForHandle(newFileIdStr)
                                sendValidationSuccess(serPort, "faccess", "collId", newFileIdStr)
            else:
                print_line('processIncomingRequest nameValueStr({})=[{}] ! missing FileAccess params !'.format(len(newLine), newLine), warning=True)
    else:
        print_line('ERROR: line({})=[{}] ! P2 LINE NOT Recognized !'.format(len(newLine), newLine), error=True)

def writeJsonFile(outFSpec, dataDict):
    # format the json data and write to file
    with open(outFSpec, "w") as write_file:
        json.dump(dataDict, write_file, indent = 4, sort_keys=True)
        # append a final newline
        write_file.write("\n")

def sendValidationError(serPort, cmdPrefixStr, errorMessage):
    # format and send an error message via outgoing serial
    successStatus = False
    responseStr = '{}:status={}{}msg={}\n'.format(cmdPrefixStr, successStatus, parm_sep, errorMessage)
    newOutLine = responseStr.encode('utf-8')
    print_line('sendValidationError line({})=[{}]'.format(len(newOutLine), newOutLine), error=True)
    serPort.write(newOutLine)

def sendValidationSuccess(serPort, cmdPrefixStr, returnKeyStr, returnValueStr):
    # format and send an error message via outgoing serial
    successStatus = True
    if(len(returnKeyStr) > 0):
        # if we have a key we're sending along an extra KV pair
        responseStr = '{}:status={}{}{}={}\n'.format(cmdPrefixStr, successStatus, parm_sep, returnKeyStr, returnValueStr)
    else:
        # no key so just send final status
        responseStr = '{}:status={}\n'.format(cmdPrefixStr, successStatus)
    newOutLine = responseStr.encode('utf-8')
    print_line('sendValidationSuccess line({})=({})'.format(len(newOutLine), newOutLine), verbose=True)
    serPort.write(newOutLine)

def sendVariableChanged(serPort, varName, varValue, collId):
        # format and send an error message via outgoing serial
    responseStr = 'ctrl:{}={}{}collId={}\n'.format(varName, varValue, parm_sep, collId)
    newOutLine = responseStr.encode('utf-8')
    print_line('sendVariableChanged line({})=[{}]'.format(len(newOutLine), newOutLine), verbose=True)
    serPort.write(newOutLine)
    sleep(0.2)  # pause 2/10ths of second

def genNextRxString(countValue):
    # format expected RX message for comparison use
    desiredFileIdStr = 'P2TestMsg#{:05d}'.format(int(countValue))
    return desiredFileIdStr

def genNextTxString(countValue):
    # generate expected TX message to send
    desiredFileIdStr = 'RPiTestMsg#{:05d}'.format(int(countValue))
    return desiredFileIdStr


def processInput(serPort):
    global queueRxLines
    while True:             # get Loop (if something, get another)
        # process an incoming line - creates our windows as needed
        currLine = queueRxLines.popLine()

        if len(currLine) > 0:
            processIncomingRequest(currLine, serPort)
        else:
            break

def genSomeOutput(serPort):
    newOutLine = b'Hello p2\n'
    print_line('genSomeOutput line({})=({})'.format(len(newOutLine), newOutLine), debug=True)
    serPort.write(newOutLine)

def mainLoop(serPort):
    print_line('Thread: MainLoop() running', verbose=True)
    while True:             # Event Loop
        processInput(serPort)
        # genSomeOutput(serPort)
        sleep(0.2)  # pause 2/10ths of second


# -----------------------------------------------------------------------------
#  Main loop
# -----------------------------------------------------------------------------

# and allocate our single runtime config store
runtimeConfig = RuntimeConfig()

# and allocate our single runtime config store
fileHandles = FileHandleStore()

# alocate our access to our Host Info
rpiHost = RPiHostInfo()

rpi_model, rpi_model_raw = rpiHost.getDeviceModel()
rpi_linux_release = rpiHost.getLinuxRelease()
rpi_linux_version = rpiHost.getLinuxVersion()
rpi_hostname, rpi_fqdn = rpiHost.getHostnames()

# Write our RPi proc file
dictHostInfo = {}
dictHostInfo['Model'] = rpi_model
dictHostInfo['ModelFull'] = rpi_model_raw
dictHostInfo['OsRelease'] = rpi_linux_release
dictHostInfo['OsVersion'] = rpi_linux_version
dictHostInfo['Hostname'] = rpi_hostname
dictHostInfo['FQDN'] = rpi_fqdn

procFspec = os.path.join(folder_proc, 'rpiHostInfo.json')
writeJsonFile(procFspec, dictHostInfo)

# record RPi into to runtimeConfig
runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyRPiModel, rpi_model)
runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyRPiMdlFull, rpi_model_raw)
runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyRPiRel, rpi_linux_release)
runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyRPiVer, rpi_linux_version)
runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyRPiName, rpi_hostname)
runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyRPiFqdn, rpi_fqdn)

# let's ensure we have all needed directories

for dirSpec in folderSpecByFolderId.values():
    if not os.path.isdir(dirSpec):
        os.mkdir(dirSpec)
        if not os.path.isdir(dirSpec):
            print_line('WARNING: dir [{}] NOT found!'.format(dirSpec), warning=True)
            print_line('ERROR: Failed to create Dir [{}]!'.format(dirSpec), warning=True)
        else:
            print_line('Dir [{}] created!'.format(dirSpec), verbose=True)
    else:
        print_line('Dir [{}] - OK'.format(dirSpec), debug=True)


def reportFileChanged(fSpec):
    # If file is of interest, Load json file and send vars to P2
    collId = fileHandles.handleForFSpec(fSpec);
    if fileHandles.isWatchedFSpec(fSpec) == False:
         print_line('CHK File [{}] is NOT watched'.format(fSpec), debug=True)
    else:
        print_line('CHK File [{}] is watched'.format(fSpec), debug=True)
        # load json file
        filesize = os.path.getsize(fSpec)
        fileDict = {}   # start empty
        if filesize > 0:    # if we have existing content, preload it
            with open(fSpec, "r") as read_file:
                fileAr = json.load(read_file)
                fileDict = fileAr[0]    # PHP puts dict in array!?
                for varName in fileDict.keys():
                    varValue = fileDict[varName]
                    print_line('Control [{}] = [{}]'.format(varName, varValue), debug=True)
                    # send var to P2
                    sendVariableChanged(serialPort, varName, varValue, collId)


colorama_init()  # Initialize our color console system

# start our serial receive listener

# 1,440,000 = 150x 9600 baud  FAILS P2 Tx
#   864,000 =  90x 9600 baud  FAILS P2 Tx
#   720,000 =  75x 9600 baud  FAILS P2 Rx
#   672,000 =  70x 9600 baud  FAILS P2 Rx
#   624,000 =  65x 9600 baud  GOOD (Serial test proven)
#   499,200 =  52x 9600 baud
#   480,000 =  50x 9600 baud
#
baudRate = 624000
print_line('Baud rate: {:,} bits/sec'.format(baudRate), verbose=True)

serialPort = serial.Serial ("/dev/serial0", baudRate, timeout=1)    #Open port with baud rate & timeout

queueRxLines = RxLineQueue()

_thread.start_new_thread(taskSerialListener, ( serialPort, ))

# start our file-system watcher
dirWatcher = FileSystemWatcher(folder_control)
#dirWatcher.run()
_thread.start_new_thread(dirWatcher.run, ( ))

sleep(1)    # aloow threads to start...

# run our loop
try:
    mainLoop(serialPort)

finally:
    # normal shutdown
    print_line('Done', info=True)
