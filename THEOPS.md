# P2 RPi ioT Gateway - Serial Communications

Enable an RPi to serve as an ioT gateway for our P2 Hardware - while dedicating only 2 pins for serial communication

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE) 

---

**--------- This project currently UNDER DEVELOPMENT!  it is NOT yet ready for use! ---------**

---


We have a Spin2/Pasm2 object that runs on the P2 which communicates over bi-directional serial with a connected Raspberry Pi (RPi) which is in-turn running a python script which handles the requests arriving from the P2.  These requests will provide access to many services which together provide a rich internet-of-things (ioT) capability to our P2.

A custom protocol using service specific messages is sent over the serial interface between the two devices (P2 and RPi).  This page details this serial protocol.

## Service based Protocol

**NOTE:** this is an early draft.  We are still thinking through how unanticipated messages will be sent to the P2.  We are hoping to do some sort of notification mech where the P2 can be asynchronously notified that a value change, or tweet was recieved, etc. This table does NOT yet reflect this unanticipated message traffic.


| Service Type | intent | Messages |
| ------------------ | --------- | ---- |
| File Operations |||
| | P2 connect to, or create file on RPi |
| | | file-open {pathType}/{filename} - returns {fileId}
| | P2 reads values from file on RPi|
| | | file:{fileId} read value {key} - returns {value}
| | P2 writes values to file on RPi|
| | | file:{fileId} write {key}={value}
| | P2 remove file from RPi |
| | | file-remove:{fileId} - returns T/F where T means file was removed
| SMS (texting) |||
| | P2 asks RPi to send a text message to the phone number
| | | sms:{phoneNbr} text={messageText}
| | (Maybe? have to see if possible) P2 gets text message contents relayed from RPi
| | | - unknown at this time -
| Twitter |||
| | P2 asks RPi to send a message to a Twitter account
| | | tweet:{accountID} text={messageText}
| | P2 gets Twitter message contents relayed from RPi
| | | tweet-get:{accountID} - returns text={messageText}
| | RPi collects Twitter feed content into file allowing it to be accessed later by P2 or RPI web page
| | | (we are NOT yet sure if the P2 will be in control of this or this is an RPi side configuration...)
| Email  |||
| | P2 asks RPi to send an email message to one or more recipients, providing full/partial content for email
| | | email:[to={emailAddr}[,to={emailAddr}][,[to:cc:bcc]={emailAddr}]] text={emailText}
| | RPi logs outgoing email from P2 (allowing display on web backend, etc.)
| | | (we are NOT yet sure if the P2 will be in control of this or this is an RPi side configuration...)
| Web Server | The web pages display values found in files and post values to files when controls are interacted with. File operations provides the transfer of the file contents to/from the P2 ||
| | P2 sends values that are shown on a web page served from RPi (using file services)|
| | | see file operations - write
| | P2 Gets values sent from web page to the P2 (controls touched, text entered)|
| | | see file operations - read



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
