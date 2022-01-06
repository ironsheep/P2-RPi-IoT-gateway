# P2 RPi ioT Gateway - EMAIL Services Setup
Enable an RPi to serve as an ioT gateway for our P2 Hardware - while dedicating only 2 pins for serial communication

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE) 

---

**--------- This project currently UNDER DEVELOPMENT!  it is NOT yet ready for use! ---------**

---

## Install Email Service support

To enable email send from your RPi chose then follow the instructions for one of these two forms:

1. mail is sent from another machine on your network, not directly from this RPi
1. mail is sent directly from this RPi


## (1) Install to have mail delivered by another machine on your network

I the author's case mail is delivered by one of a single machine on the authors network so that it is the only machine which needs to know email account and password necessary to send email.

To configure this is a single install and answer a couple of questions during the install.  The author uses postfix for all mail delivery even on this RPi.

To install and configure for this form do:

```bash
$ sudo apt-get install postfix postfix-doc
```

During install you will be prompted for:

- mail configuration, choose:
 - satellite
- hostname of machine that delievers the email:
 - {your email deliveror hostname}
- default email domain:
 - the authors home network is known by one domain name. Use this domain here:
 - {your external domain name} 

Once these questions are answered the postfix packages will finish install and then configure themselves. At this time you can now send an email from the command line. 

```bash
$ sendmail youremail@example.com
To: differentemail@example.com
From: anyone@example.com
Subject: Test Send Mail
Hello World
.<return>  # this will end the entry of the email and send it
```

If you addressed it correctly and you see the email arrive in your inbox then you have a working email send system. Congratulations!

### Configure the gateway daemon to use sendmail

Lastly, we need to tell the python script that it should use [sendmail(1)](http://manpages.ubuntu.com/manpages/trusty/man1/citmail.1.html) for sending email.

Ensure the following is set in your **config.ini**:

```bash
[EMAIL]
use_sendgrid = false
```

This completes your setup of email using delivery by another machine on your network.


## (2) Install to have mail sent directly from this RPi

Most direct-send email mechanisms request the use and storage of the username and password in clear-text on the sending RPi.  We are choosing to use the SendGrid free account so there is only an API Key stored on the sneding RPi.  Get your free account and API Key by doing:

### Prerequisites

Be sure to perform the following prerequisites to complete this form of email setup.

- Sign up for a SendGrid account.
- Enable Two-factor authentication.
- Create and SendGrid API Key with **Mail Send > Full Access** permissions.
- Complete Domain Authentication.
- Configure SendGrid use in the gateway **config.ini**:
 - Turn on SendGrid use by the gateway
 - Record your API Key in the **config.ini**

### Sign up for a SendGrid account

When you sign up for a free [SendGrid account](https://signup.sendgrid.com/), you'll be able to send 100 emails per day forever. 

### Enable Two-factor authentication controlling later access to your account

Twilio SendGrid requires customers to enable Two-factor authentication (2FA). You can enable 2FA with SMS (direct texting your mobile device) or by using the [Authy](https://authy.com/) app. See the [2FA section of our authentication documentation](https://docs.sendgrid.com/ui/account-and-settings/two-factor-authentication) for instructions.

### Create and store a SendGrid API key
Unlike a username and password — credentials that allow access to your full account — an API key is authorized to perform a limited scope of actions. If your API key is compromised, you can also cycle it (delete and create another) without changing your other account credentials.

Visit our [API Key documentation](https://docs.sendgrid.com/ui/account-and-settings/api-keys) for instructions on creating an API key, ignore the storing your key sections we don't care about this aspect.

**WARNING Be real careful here!** *you have can only copy your API Key while the page showing your key is open. If you close this page without copying it you will have to generate a new key!*

### Configure the gateway daemon to use your new SendGrid account

Lastly, we need to tell the python script that it should use SendGrid for sending email.

Ensure the following is set in your **config.ini**:

```bash
[EMAIL]
use_sendgrid = true

sendgrid_api_key = {api_key}
```

**NOTE**: replace **{api_key}** with your new API Key.

**TBA, UNDONE** (*add script to test email send and specify it's use here.*)

This completes your setup of email delivery via SendGrid.

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
