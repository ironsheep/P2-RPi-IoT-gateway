# P2 RPi ioT Gateway - Web: 1-wire Demo

Enable an RPi to serve as an ioT gateway for our P2 Hardware - while dedicating only 2 pins for serial communication

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

## Files associated with this Demo

This demo consists of a web page to be placed where the RPi web server can find it and a P2 .spin2 file which runs on your P2 hardware connected via serial to your RPi Gateway.

| Spin2/webPage File Name(s) | Demonstration | Form 
| --- | --- | --- |
| [demo\_p2gw_1wireStatus.spin2](P2-Source/demo_p2gw_1wireStatus.spin2) | Display live 1-wire temp sensor data - read sensor send data to status folder on gateway | App
| [Archive of Demo Web Page](demoWebPageSets/demoFiles-bs1wire.tar.gz) | Display live 1-wire temp sensor data - web page shows reported sensor data along with details of the RPi host which is running the web server | Web Page Folder 

Once this web page is put into place and the demo is run on the P2 you browse to the web page being presented from the RPi to see the new web sensor page: 
                                                                                            
![Demo Goal](./Docs/images/demo-1-wire.png)

## Wiring the 1-wire device

The **demo\_p2gw_1wireStatus.spin2** program is configured to use P2 pin 16 for the 1-wire device.


**P2 Connections expected by Demo:**

| P2 Purpose | P2 Pin # |
| --- | --- |
| Signal ground | GND near Pin 16|
| 1-wire data (DS18S20) | 16

Pick a pin on your P2 dev board to be used for 1-wire communications. The demo file provided by this project defines this pin to be 16. Feel free to choose a different pin. Just remember to adjust the constant in your code to use your pin choice.

## Install the 1-wire demo

The .spin2 source for this demo is found in `/opt/P2-RPi-ioT-gateway/P2-Source` You will need to install the web page source under the web server.

Installing is pretty easy. The web-page demo files are also present. They live in `/opt/P2-RPi-ioT-gateway/demoWebPageSets/`.  To unpack this demo file do:

```bash
cd /var/www/html
tar -xzvf /opt/P2-RPi-ioT-gateway/demoWebPageSets/demoFiles-bs1wire.tar.gz
```

This should create a folder `/var/www/html/bs1wire/' which now has a top-level `index.php` page therein.

After these files are unpacked you should be able to point your browser to: `http://{mypihostname|orIpAddress}/bs1wire`

## Run the demo

For this demo you need:

- P2 ready to load code
- P2 wired to RPi (3-wire serial cable)
- DS18S20 1-wire sensor wired to the P2
- RPi running our daemon (by hand or as Daemon from boot)
- Web page unpacked into proper place

### Startup

- Ensure that the Daemon script is running
- Compile and download `demo_p2gw_web_control.spin2` to the P2
  - The demo on startup sends driver status to the RPi 
  - The demo on startup also reads the 1-wire device and send values to the RPi
  - Open brower to your newly installed web page
  - This page should looks similar to the image above


### What's the page doing?

The web page is comprised of HTML code styled using CSS (as included files) and has PHP code intermixed with the HTML.

The PHP code loads and shows the values sent from the P2.  It also loads details about the host RPi on which it is running and shows these details.

As the P2 loops around to reading the sensor again it sends the latest value to the RPi again.  The web page has a referesh directing which causes it to reload periodically.  Each time it reloads it also re-reads the status values coming from the P2 and presents them.  This is why we see the temperature updating every so often.

This demo should provide a good reference for how you can create similar services. 

You are now controlling reading temperature from a web page which was read by your P2 and sent to the web-server to be displayed!

Enjoy!

##  Collections Used by this Demo

**remember:** *collections in gateway parlance are files which contain one or more key-value pairs.*

This demo uses a couple of collections (files) on the RPi. The status file is created when the P2 reads the Temperature 1-wire device and sends the value to the RPi. The Proc file is generated automatically whenever the Daemon is run.

Collections used:

| Collection Name | Created By | Description |
| --- | --- | --- |
| STATUS/**p2-1wireValues** | P2 write action | Value to send to web page
| PROC/**rpiHostInfo** | RPi Daemon | RPi details to be shown on web page

Within the status file the P2 places one key-value pair:

| Status Variable | Description |
| --- | --- |
| tempSensorStr | Temperature value (string) to be shown on web page

Whenever the web page is loaded (or reloaded - every N seconds) this file is read, the value for `tempSensorStr` is pulled from the file and shown on the web page

Additionally the web page shows content from one of our generated files **PROC/rpiHostInfo** which is maintained by our RPi Daemon and contains details of the RPi upon which the Daemon is running.

##  Tool I used to create the web page

I run on a Mac desktop.  My favorite tool for creating web pages is [Bootstrap Studio](https://bootstrapstudio.io/)  This tool provides easy WYSIWYG editing, easy CSS styling, good responsive layout code, and exports tiney files for you to place on your server.

However, I edit the PHP and make final tweaks to the HTML/CSS by hand. Yes I'm doing all of the "by hand editing" in visual studio.

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
