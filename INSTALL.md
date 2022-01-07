# P2 RPi ioT Gateway - RPi Setup / P2 Project Setup

Enable an RPi to serve as an ioT gateway for our P2 Hardware - while dedicating only 2 pins for serial communication

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE) 

---

**--------- This project currently UNDER DEVELOPMENT!  it is NOT yet ready for use! ---------**

---

## Contents

Found on this Page:

- [Installation](https://github.com/ironsheep/P2-RPi-ioT-gateway/blob/main/INSTALL.md#installation) - Install this project and supporting libraries on an RPi
- [Configuration](https://github.com/ironsheep/P2-RPi-ioT-gateway/blob/main/INSTALL.md#configuration) - Initial configuration of gateway
- [Wiring](https://github.com/ironsheep/P2-RPi-ioT-gateway/blob/main/INSTALL.md#wiring-our-serial-connection) - Wire the serial connection between the P2 Development board and our RPi
- [Execution](https://github.com/ironsheep/P2-RPi-ioT-gateway/blob/main/INSTALL.md#execution) - Test the deamon configuration. Does it all run?
- [Configure Daemon run Style]() - Configure this project to start at every boot 
- [Update install to latest]() - Project updated? Update this RPis installation to get latest features 

Additional pages:

- [Top README](https://github.com/ironsheep/P2-RPi-ioT-gateway)
- [Configure Email Service](SETUP-EMAIL.md)
- Configure Twitter Service - *TBA*
- Configure SMS Service- *TBA*
- Configure Apache/PHP Service- *TBA*

---

## Installation

On a modern Linux system just a few steps are needed to get the daemon working.
The following example shows the installation under Debian/Raspbian below the `/opt` directory:

First install extra packages the script needs (select one of the two following commands)

### Packages for Ubuntu, Raspberry pi OS, and the like

```shell
sudo apt-get install git python3 python3-pip python3-tzlocal python3-sdnotify python3-colorama python3-unidecode python3-paho-mqtt
```

### Now finish with the script install

Now that the extra packages are installed let's install our script and any remaining supporting python modules.

```shell
sudo git clone https://github.com/ironsheep/P2-RPi-ioT-gateway.git /opt/P2-RPi-ioT-gateway

cd /opt/P2-RPi-ioT-gateway
sudo pip3 install -r requirements.txt
```

**WARNING:** If you choose to install these files in a location other than `/opt/P2-RPi-ioT-gateway`, you will need to modify some of the control files which are used when setting up to run this script automatically. The following files:

- **p2-rpi-iot-gateway** - Sys V init script
- **p2-rpi-iot-gateway.service** - Systemd Daemon / Service description file

... need to have any mention of `/opt/P2-RPi-ioT-gateway` changed to your install location **before you can run this script as a service.**


## Configuration

To match personal needs, all operational details can be configured by modifying entries within the file [`config.ini`](config.ini.dist).
The file needs to be created first: (*in the following: if you don't have vim installed you might try nano*)

```shell
sudo cp /opt/P2-RPi-ioT-gateway/config.{ini.dist,ini}
sudo vim /opt/P2-RPi-ioT-gateway/config.ini
```

You will likely want to locate and configure the following (at a minimum) in your config.ini:

```shell
fallback_domain = {if you have older RPis that dont report their fqdn correctly}
# ...
hostname = {your-mqtt-broker}
# ...
discovery_prefix = {if you use something other than 'homeassistant'}
# ...
base_topic = {your home-assistant base topic}

# ...
username = {your mqtt username if your setup requires one}
password = {your mqtt password if your setup requires one}

```

Now that your config.ini is setup let's test!

## Wiring our Serial Connection

The **P2-RPi-ioT-gw-daemon.py** script is built to use the main serial I/O channel at the RPi GPIO Interface.  These are GPIO pins 14 & 15. 

**NOTE:** FYI a good reference is: [pinout diagram for RPi GPIO Pins](https://pinout.xyz/)

**RPi Wiring for Daemon use:**

| RPi Hdr Pin# | RPi GPIO Name| RPi Purpose | P2 Purpose | P2 Pin # |
| --- | --- | --- | --- | --- |
| 6 | GND | Signal ground| Signal ground | GND near Tx/Rx Pins|
| 8 | GPIO 14 | Uart Tx | Serial Rx (from RPi) | 25
| 10 | GPIO 15 | Uart Rx | Serial Tx (to RPi) | 24

Pick two pins on your P2 dev board to be used for RPi serial communications. The demo files provided by this project define these two pins as 24, 25. Feel free to choose different pins. Just remember to adjust the constants in your code to use your pin choices.
 
## Execution

### Initial Test

A first test run is as easy as:

```shell
python3 /opt/P2-RPi-ioT-gateway/P2-RPi-ioT-gw-daemon.py
```

**NOTE:** *it is a good idea to execute this script by hand this way each time you modify the config.ini.  By running after each modification the script can tell you through error messages if it had any problems with any values in the config.ini file, or any missing values. etc.*``

Using the command line argument `--config`, a directory where to read the config.ini file from can be specified, e.g.

```shell
python3 /opt/P2-RPi-ioT-gateway/P2-RPi-ioT-gw-daemon.py --config /opt/P2-RPi-ioT-gateway
```

### Preparing to run full time

In order to have your HA system know if your RPi is online/offline and when it last reported-in then you must set up this script to run as a system service.

**NOTE:** Daemon mode must be enabled in the configuration file (default).

But first, we need to grant access to some hardware for the user account under which the sevice will run.

### Set up daemon account to allow access to serial I/O

By default this script is run as user:group  **daemon:daemon**.  As this script requires access to the serial uart you'll want to add access to it for the daemon user as follows (note: serial access is controlled by the 'dialout' group/permission):

```shell
# list current groups
groups daemon
$ daemon : daemon

# add video if not present
sudo usermod daemon -a -G dialout

# list current groups
groups daemon
$ daemon : daemon dialout
#                 ^^^^^^^ now it is present
```
   
### (all RPi3 models) enable /dev/serial0

```shell
# edit /boot/config.txt
sudo vi /boot/config.txt
```
	
in **/boot/config.txt** add the following lines and reboot your RPi.  /dev/serial0 should now appear.
   
```shell
# fix our serial clock freq so we can do 2Mb/s
# ref: https://github.com/ironsheep/RPi-P2D2-Support
init_uart_clock=32000000
	
# and condition which uart is present
enable_uart=1

```
   
***TBD** add instructions to run sudo raspi-config to disable console but enable serial port!

### Choose Run Style

You can choose to run this script as a `systemd service` or as a `Sys V init script`. If you are on a newer OS than `Jessie` or if as a system admin you are just more comfortable with Sys V init scripts then you can use the latter style.

Let's look at how to set up each of these forms:

#### Run as Systemd Daemon / Service (*for Raspian/Raspberry pi OS newer than 'jessie'*)

(**Heads Up** *We've learned the hard way that RPi's running `jessie` won't restart the script on reboot if setup this way, Please set up these RPi's using the init script form shown in the next section.*)

Set up the script to be run as a system service as follows:

   ```shell
   sudo ln -s /opt/P2-RPi-ioT-gateway/p2-rpi-iot-gateway.service /etc/systemd/system/p2-rpi-iot-gateway.service

   sudo systemctl daemon-reload

   # tell system that it can start our script at system startup during boot
   sudo systemctl enable p2-rpi-iot-gateway.service
   
   # start the script running
   sudo systemctl start p2-rpi-iot-gateway.service
   
   # check to make sure all is ok with the start up
   sudo systemctl status p2-rpi-iot-gateway.service
   ```
   
**NOTE:** *Please remember to run the 'systemctl enable ...' once at first install, if you want your script to start up every time your RPi reboots!*

#### Run as Sys V init script (*your RPi is running 'jessie' or you just like this form*)

In this form our wrapper script located in the /etc/init.d directory and is run according to symbolic links in the `/etc/rc.x` directories.

Set up the script to be run as a Sys V init script as follows:

   ```shell
   sudo ln -s /opt/P2-RPi-ioT-gateway/p2-rpi-iot-gateway /etc/init.d/p2-rpi-iot-gateway

	# configure system to start this script at boot time
   sudo update-rc.d p2-rpi-iot-gateway defaults

   # let's start the script now, too so we don't have to reboot
   sudo /etc/init.d/p2-rpi-iot-gateway start
  
   # check to make sure all is ok with the start up
   sudo /etc/init.d/p2-rpi-iot-gateway status
   ```
   
### Update to latest

Like most active developers, we periodically upgrade our script. Use one of the following list of update steps based upon how you are set up.

#### Systemd commands to perform update

If you are setup in the systemd form, you can update to the latest we've published by following these steps:

   ```shell
   # go to local copy of repo
   cd /opt/P2-RPi-ioT-gateway

   # stop the service
   sudo systemctl stop p2-rpi-iot-gateway.service

   # get the latest version
   sudo git pull

   # reload the systemd configuration (in case it changed)
   sudo systemctl daemon-reload

   # restart the service with your new version
   sudo systemctl start p2-rpi-iot-gateway.service

   # if you want, check status of the running script
   systemctl status p2-rpi-iot-gateway.service

   ```
   
#### SysV init script commands to perform update

If you are setup in the Sys V init script form, you can update to the latest we've published by following these steps:

   ```shell
   # go to local copy of repo
   cd /opt/P2-RPi-ioT-gateway

   # stop the service
   sudo /etc/init.d/p2-rpi-iot-gateway stop

   # get the latest version
   sudo git pull

   # restart the service with your new version
   sudo /etc/init.d/p2-rpi-iot-gateway start

   # if you want, check status of the running script
   sudo /etc/init.d/p2-rpi-iot-gateway status

   ```


---

> If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices! 
> 
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep)

----

## Disclaimer and Legal

> *Raspberry Pi* is registered trademark of *Raspberry Pi (Trading) Ltd.*
>
> *Parallax, Propeller Spin, and the Parallax and Propeller Hat logos* are trademarks of Parallax Inc., dba Parallax Semiconductor
>
> This project is a community project not for commercial use.
> 
> This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by *Raspberry Pi (Trading) Ltd.* or any of its affiliates or subsidiaries.
> 
> Likewise, This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by *Parallax Inc., dba Parallax Semiconductor* or any of its affiliates or subsidiaries.

---

## License

Copyright © 2022 Iron Sheep Productions, LLC. All rights reserved.<br />
Licensed under the MIT License. <br>
<br>
Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)



[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[marketplace-version]: https://vsmarketplacebadge.apphb.com/version-short/ironsheepproductionsllc.spin2.svg

[marketplace-installs]: https://vsmarketplacebadge.apphb.com/installs-short/ironsheepproductionsllc.spin2.svg

[marketplace-rating]: https://vsmarketplacebadge.apphb.com/rating-short/ironsheepproductionsllc.spin2.svg

[license-shield]: https://camo.githubusercontent.com/bc04f96d911ea5f6e3b00e44fc0731ea74c8e1e9/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f69616e74726963682f746578742d646976696465722d726f772e7376673f7374796c653d666f722d7468652d6261646765
