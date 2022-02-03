# P2 RPi ioT Gateway - Developing a P2 Application interacting with the IoT Gateway

Enable an RPi to serve as an ioT gateway for our P2 Hardware - while dedicating only 2 pins for serial communication

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)



## Add Gateway to project

We use a simple Full-duplex serial link between your P2 board and the Raspberry Pi. We've crafted two .spin2 objects which are compiled into your code (The gateway object and a serial line-receiving queue object.) To configure the gateway you specify which two P2 pins are to be used when communicating with the RPi and iidenitfy the application running the gateway.

To use this in your own project you simply compile-in the gateway objects, start it and then make calls to it.

### IoT Gateway Objects

The following objects are compiled into your app.

- isp\_rpi\_iot_gw.spin2
- isp\_queue_serial.spin2
- jm_serial.spin2
- jm_nstrings.spin2

You simply include them with something like:

```script
OBJ { Objects Used by this Object }

    IoT_GW      :   "isp_rpi_iot_gw"            ' serial I/O to/from RPi
    rxQue       :   "isp_queue_serial"          ' acces our received data
```

Starting the gateway in Spin2 is also pretty simple:

```script
CON { RPi Gateway io pins }

  RX_GW    = 25  { I }                                          ' Raspberry Pi (RPi) Gateway
  TX_GW    = 24  { O }

  GW_BAUDRATE = 624_000   ' 624kb/s - allow P2 rx to keep up!

DAT { our hardware ID strings and 1-wire buffers, collection names }

  p2HardwareID    byte    "{your hardware descr here}",0

PUB main() | eOpStatus, nIdx, nCollId, eRxQStatus, eCmdId, tmpVar

    '' Start the RPi serial communications and COGs
    IoT_GW.startx(RX_GW, TX_GW, GW_BAUDRATE)    ' tell singleton our pins and rate

    ' (one time) tell the RPi about about this hardware
    IoT_GW.identify(@p2HardwareID)

  ... and do your app stuff from here on ...
  
   IoT_GW.stop()   ' if you wish to shutdown COGs and release serial lines
   
```


## Configure and Restart Daemon if turning on new service

If it is your first time using a new service of this gateway you may have to place configuration values in the **config.ini** Daemon settings file. The following services need one-time configuration:

| Service | config needed |
| --- | --- |
| email | if using **sendmail** the default values should work, if using **SendGrid** then enable sendgrid, set from address and add API key
| (more sevices TBA) |


## make calls to gateway object

... content TBA ...


---

> If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep)

---

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

Copyright © 2022 Iron Sheep Productions, LLC. All rights reserved.

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[marketplace-version]: https://vsmarketplacebadge.apphb.com/version-short/ironsheepproductionsllc.spin2.svg

[marketplace-installs]: https://vsmarketplacebadge.apphb.com/installs-short/ironsheepproductionsllc.spin2.svg

[marketplace-rating]: https://vsmarketplacebadge.apphb.com/rating-short/ironsheepproductionsllc.spin2.svg

[license-shield]: https://camo.githubusercontent.com/bc04f96d911ea5f6e3b00e44fc0731ea74c8e1e9/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f69616e74726963682f746578742d646976696465722d726f772e7376673f7374796c653d666f722d7468652d6261646765
