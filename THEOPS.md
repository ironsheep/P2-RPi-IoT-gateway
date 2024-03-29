# P2 RPi ioT Gateway - Serial Communications

Enable an RPi to serve as an ioT gateway for our P2 Hardware - while dedicating only 2 pins for serial communication

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

We have a Spin2/Pasm2 object that runs on the P2 which communicates over bi-directional serial with a connected Raspberry Pi (RPi) which is in-turn running a python script which handles the requests arriving from the P2.  These requests will provide access to many services which together provide a rich internet-of-things (ioT) capability to our P2.

A custom protocol using service specific messages is sent over the serial interface between the two devices (P2 and RPi).  This page details this serial protocol.

## Service based Protocol

**NOTE:** this is an early draft.  We are still thinking through how unanticipated messages will be sent to the P2.  We are hoping to do some sort of notification mech where the P2 can be asynchronously notified that a value change, or tweet was recieved, etc. This table does NOT yet reflect this unanticipated message traffic.

| Service Type | Message | Returns | Interpretation |
| ------------ | --------- | ---- | --- |
| **P2 Setup** | |||
| P2 -> RPi | ident:hwName={hardwareName}\<SEP>objVer={gwObjVersion}\n | | Identify P2 Device to RPi for use in logging, email send, etc. |
| P2 <- RPi | fident:status=True\n<br/>fident:status=False\<SEP>msg={errorMsg}\n | success=T/F<br/>msg when F | 
| **Collection Operations** ||||
| | **Collection Access/Open** |||
| P2 -> RPi | file-access:dir={folderEnum}\<SEP>mode={modeEnum}\<SEP>cname={fileBasename}\n | | P2 connect to, or create file on RPi |
| P2 <- RPi | faccess:status=True\<SEP>collId={collId}\n<br/> faccess:status=False\<SEP>msg={errorMsg}\n | success=T/F<br/>msg when F  | Returns Collection ID (handle) if success 
| | **Read value for Key** |||
| P2 -> RPi | file-read:cid={collId}\<SEP>key={keyName}\n | | P2 reads named value from collection on RPi |
| P2 <- RPi | fread:status=True\n\<SEP>varVal={desiredValue}<br/> fread:status=False\<SEP>msg={errorMsg}\n | success=T/F<br/>msg when F  | Returns {desiredValue} for key if success 
| | **Write/Replace Key/Value pair** |||
| P2 -> RPi | file-write:cid=1\<SEP>key={keyName}\<SEP>val={varValue}\n | | P2 writes value to collection on RPi|
| P2 <- RPi | fwrite:status=True\n<br/>fwrite:status=False\<SEP>msg={errorMsg}\n | success=T/F<br/>msg when F  | 


### Folder Enum Values

| Name | Value | Location | Meaning
| --- | --- | --- | --- |
| EFI_VAR | 100 | /var/{p2gwdir}/ folder | General purpose file store - not erased
| EFI_TMP | 101 | /tmp/{p2gwdir}/ folder | Temporary file store - may be erased by RPi
| EFI_CONTROL | 102 | /var/www/html/{p2gwdir}/control folder | values written by web server
| EFI_STATUS | 103 | /var/{p2gwdir}/status folder | values to be sent to web server
| EFI_LOG | 104 | /var/{p2gwdir}/log folder | logs (written by gateway daemon)
| EFI_MAIL | 105 | /var/{p2gwdir}/mail | record of mail sent by gateway daemon
| EFI_PROC | 106 | /var/{p2gwdir}/proc | read-only files maintained by gateway daemon

### File Access Enum Values


| Name | Value | Meaning
| --- | --- | --- |
| FM_READONLY | 200 | Open for read access
| FM_WRITE | 201 | Open for write (must already exist)
| FM\_WRITE_CREATE | 202 | Open for write
| FM_LISTEN | 203 | Inform that P2 wants to be notified if content changes

---

> If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./Docs/images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

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

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[marketplace-version]: https://vsmarketplacebadge.apphb.com/version-short/ironsheepproductionsllc.spin2.svg

[marketplace-installs]: https://vsmarketplacebadge.apphb.com/installs-short/ironsheepproductionsllc.spin2.svg

[marketplace-rating]: https://vsmarketplacebadge.apphb.com/rating-short/ironsheepproductionsllc.spin2.svg

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
