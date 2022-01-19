# P2 RPi ioT Gateway - Web: 1-wire Demo

Enable an RPi to serve as an ioT gateway for our P2 Hardware - while dedicating only 2 pins for serial communication

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

## Files associated with this Demo

This demo consists of a web page to be placed where the RPi web server can find it and a P2 .spin2 file which runs on your P2 hardware connected via serial to your RPi Gateway.

| Spin2/webPage File Name(s) | Demonstration | Form 
| --- | --- | --- |
| [demo\_p2gw_1wireStatus.spin2](P2-Source/demo_p2gw_1wireStatus.spin2) | Display live 1-wire temp sensor data - read sensor send data to status folder on gateway | App
| [Archive of Demo Wab Page](demoWebPageSets/demoFiles-bs1wire.tar.gz) | Display live 1-wire temp sensor data - web page shows reported sensor data along with details of the RPi host which is running the web server | Web Page Folder 

Once this web page is put into place and the demo is run on the P2 you browse to the web page being presented from the RPi to see the new web sensor page: 
                                                                                            
![Demo Goal](./Docs/images/demo-1-wire.png)

## Install the 1-wire demo

The .spin2 source for this demo is already installed. But you will need to install the web page source. 

Installing is pretty easy. When you installed or updated the gateway project on your RPi the web-page demo files were already installed. They live in `/opt/P2-RPi-ioT-gateway/demoWebPageSets/`.  To unpack this demo file do:

```bash
cd /var/www/html
tar -xzvf /opt/P2-RPi-ioT-gateway/demoWebPageSets/demoFiles-bs1wire.tar.gz
```

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
