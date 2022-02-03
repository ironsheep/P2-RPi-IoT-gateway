# P2 RPi ioT Gateway - Technology used

Enable an RPi to serve as an ioT gateway for our P2 Hardware - while dedicating only 2 pins for serial communication

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)



## P2 communication with RPi

We use a simple Full-duplex serial link between your P2 board and the Raspberry Pi. We've crafted a single .spin2 object which is compiled into your code.  To configure it you specify which two P2 pins are to be used when communicating with the RPi.

To use this in your own project you simply compile-in the gateway object, start it and then make calls to it.

## Gateway Deamon on RPi

On the RPi we have a single Python3 script which is run interactively or from power-on which listens to the serial traffic arriving from the P2. It validates the requests coming from the P2, and then acts on the request. Validation status and optionally requested data are returned to the P2 for each request.

The Daemon script also watches for directory changes (files to be modofied or new files appearing) in the Control directory.  Web pages that want to send values to our P2 write to this Control directory. The P2 application tells the RPi if it wants to be told of changes to specific files on the RPi. If the RPi knows that the P2 is listening and the file is changes the RPi sends each KV pair found in the changed file to the waiting P2.

## Interactive web-pages on RPi

... content TBA ...

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
