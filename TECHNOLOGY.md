# P2 RPi ioT Gateway - Technology used

Enable an RPi to serve as an ioT gateway for our P2 Hardware - while dedicating only 2 pins for serial communication

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

## Table of Contents

On this Page:

- [P2 communication with RPi](https://github.com/ironsheep/P2-RPi-IoT-gateway/blob/main/TECHNOLOGY.md#p2-communication-with-rpi) 
- [Gateway Deamon on RPi](https://github.com/ironsheep/P2-RPi-IoT-gateway/blob/main/TECHNOLOGY.md#gateway-deamon-on-rpi) 
- [Interactive web-pages on RPi](https://github.com/ironsheep/P2-RPi-IoT-gateway/blob/main/TECHNOLOGY.md#interactive-web-pages-on-rpi) 

Additional pages:

- [Main Page](README.md)
- [Technology Used](TECHNOLOGY.md) (this page)
- [Developing your own P2 Application](DEVELOP.md) using IoT gateway services

---


## P2 communication with RPi

We use a simple Full-duplex serial link between your P2 board and the Raspberry Pi. We've crafted two .spin2 objects which are compiled into your code (The gateway object and a serial line-receiving queue object.) To configure the gateway you specify which two P2 pins are to be used when communicating with the RPi and iidenitfy the application running the gateway.

To use this in your own project you simply compile-in the gateway objects, start it and then make calls to it.

### IoT Gateway Objects

The following objects are compiled into your app.

- isp\_rpi\_iot_gw.spin2
- isp\_queue_serial.spin2
- jm_serial.spin2
- jm_nstrings.spin2

### Tools I use when working on the .spin2 Gateway Objects


## Gateway Deamon on RPi

On the RPi we have a single Python3 script which is run interactively (or from power-on as Daemon) which listens to the serial traffic arriving from the P2. It validates the requests coming from the P2, and then acts on the request. Validation status and, optionally, requested data are returned to the P2 for each request.

The Daemon script also watches for directory changes (files to be modified or new files appearing) in the Control directory.  Web pages that want to send values to our P2 write to this Control directory. The P2 application tells the RPi if it wants to be told of changes to specific files on the RPi. If the RPi knows that the P2 is listening and the file is changed the RPi sends each KV pair found in the changed file to the waiting P2.

### Tools I use when working on the python Daemon script

I'm doing all of my Python editing in [Visual Studio Code](https://code.visualstudio.com/) (VSCode) which I run on my desktop and remote into my RPi containing the python scripts using SSH. In order to use SSH to get into my RPi's I have the following extensions installed into VSCode:

- [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh)
- [Remote - SSH: Editing Configuration Files](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh-edit)
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Python Extension Pack](https://marketplace.visualstudio.com/items?itemName=donjayamanne.python-extension-pack)
- [Python Indent](https://marketplace.visualstudio.com/items?itemName=KevinRose.vsc-python-indent)

### Python References

I use the following references when needing to do something I haven't before in the Python language:

| Language | References |
| --- | --- |
| **Python** |
|| [Python Tutorial/Ref. at W3 Schools](https://www.w3schools.com/python/)
|| [python.org docs](https://www.python.org/doc/)
|| [Python Package Index](https://pypi.org/) for when I need new libraries/frameworks for use with python

## Interactive web-pages on RPi

Now that you've set up your RPi per our instructions you have the [Apache2](https://en.wikipedia.org/wiki/Apache_HTTP_Server) web server running on the RPi and you have the [PHP](https://en.wikipedia.org/wiki/PHP) interpreter installed.

In order to provide interaction with our P2 we write our RPi web pages in PHP. In most simple cases we have a single index.php file (web page interpreted source) placed in a directory under the web server.  But what is a php file?

- PHP files can contain text, HTML, CSS, JavaScript, and PHP code
- PHP code is executed on the server, and the result is returned to the browser as plain HTML
- PHP files have extension ".php"

In other words, the index.php file is comprised of HTML code styled using CSS (typically as included files) and has PHP code intermixed with the HTML.  This entire file when requested by a browser is first interpreted by the PHP Interpreter and the resulting HTML is returned to the browser.

In our gateway web pages we use PHP to:

- Load `status` files which contain 1 or more KV pairs
- Load `proc` files which contain 1 or more KV pairs
- Write `control` files which also contain 1 or more KV pairs
- Retrieve values from HTML/PHP forms 

As an example (taken from our web-control demo) here are the actions behind the web page controlling the LED string attached to the P2

- The PHP code loads the values sent from the P2 and uses them as default values for the form it presents.  It also loads details about the host RPi on which it is running and shows these details.

- When you adjust the controls on the form and then press [Submit] all values you have set are then written into a control file as key-value pairs. The values placed in the file are shown below the form so you can see what is written to the file.

- The P2, when it started up, notified the RPi that it wanted to hear about any changes made to the control file (which the web-page writes to.)

- The Daemon sees that the file changed (since the web page just wrote to it), loads the KV pairs from the file and then sends them to the P2.

- Lastly the P2 evaluates the change as they arrive and tells the LED string what to change (Color, light pattern, delay, etc.)


### Tools I use when working on the web pages

I run on a Mac desktop.  My favorite tool for creating web pages is [Bootstrap Studio](https://bootstrapstudio.io/)  This tool provides easy WYSIWYG editing, easy CSS styling, good responsive layout code (pages you create can display well on mobile devices), and exports tiny files for you to place on your server.

However, I edit the PHP and make final tweaks to the HTML/CSS by hand. Yes I'm doing all of the "by hand editing" in [Visual Studio Code](https://code.visualstudio.com/) (VSCode) which I run on my desktop and remote into my RPi containing the pages using SSH. In order to use SSH to get into my RPi's I have the following extensions installed into VSCode:

- [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh)
- [Remote - SSH: Editing Configuration Files](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh-edit)

### HTML, CSS and PHP References

I use the following references when needing to do something I haven't before in each language:

| Language | References |
| --- | --- |
| **HTML** |
|| [HTML Tutorial/Ref. at W3 Schools](https://www.w3schools.com/html/)
|| [JavaScript Tutorial/Ref. at W3 Schools](https://www.w3schools.com/js/)
|| [Bootstrap Tutorial/Ref. at W3 Schools](https://www.w3schools.com/bootstrap/bootstrap_ver.asp) (Pick the version you use)
| **CSS** |
|| [CSS Tutorial/Ref. at W3 Schools](https://www.w3schools.com/css/)
| **PHP** |
|| [PHP Tutorial/Ref. at W3 Schools](https://www.w3schools.com/php/)

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
