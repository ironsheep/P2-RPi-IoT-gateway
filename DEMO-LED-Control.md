# P2 RPi ioT Gateway - Web: LED Lights Control Demo

Enable an RPi to serve as an ioT gateway for our P2 Hardware - while dedicating only 2 pins for serial communication

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

## Files associated with this Demo

This demo consists of a web page to be placed where the RPi web server can find it and a P2 .spin2 file which runs on your P2 hardware connected via serial to your RPi Gateway.

| Spin2/webPage File Name(s) | Demonstration | Form 
| --- | --- | --- |
| [demo\_p2gw\_web_control.spin2](P2-Source/demo_p2gw_web_control.spin2) | Control the String of LED lights from a served web-page | App
| [Archive of Demo Wab Page] | String of LED lights - web page shows controls for LED Lights along with details of the RPi host which is running the web server | Web Page Folder 

Once this web page is put into place and the demo is run on the P2 you browse to the web page being presented from the RPi to see the new web control page: 

(image TBD)
                                                                                            

## Wiring the LED String

The **demo\_p2gw_1wireStatus.spin2** program is configured to use P2 pin 16 for the 1-wire device.


**P2 Connections expected by Demo:**

| P2 Purpose | P2 Pin # |
| --- | --- |
| Signal ground | GND near Pin 16|
| LED Serial Data out | 16

Pick a pin on your P2 dev board to be used for LED serial  communications. The demo file provided by this project defines this pin to be 16. Feel free to choose a different pin. Just remember to adjust the constant in your code to use your pin choice.

## Install the Web Control Demo

The .spin2 source for this demo is found in `/opt/P2-RPi-ioT-gateway/P2-Source` You will need to install the web page source under the web server.

Installing is pretty easy. The web-page demo files are also present. They live in `/opt/P2-RPi-ioT-gateway/demoWebPageSets/`.  To unpack this demo file do:

```bash
cd /var/www/html
--TBD--
```

This should create a folder `/var/www/html/-TBD-/' which now has a top-level `index.php` page therein.

After these files are unpacked you should be able to point your browser to: `http://{mypihostname|orIpAddress/-TBD-`

All that's left then is run the demo .spin2 on your P2 after making sure your P2 and your RPi are connected via serial and that your Gateway Daemon is already running.

This demo should provide a good reference for how to create similar services. 

Enjoy!

##  Tool I used to create the web page

I run on a Mac desktop.  My favorite tool for creating web pages is [Bootstrap Studio](https://bootstrapstudio.io/)  This tool provides easy WYSIWYG editing, easy CSS styling, good responsive layout code, and exports tiney files for you to place on your server.

### ...

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