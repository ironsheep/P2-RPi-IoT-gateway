# P2 RPi ioT Gateway - Setup SSH access to your RPi

Enable an RPi to serve as an ioT gateway for our P2 Hardware - while dedicating only 2 pins for serial communication

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)


**DRAFT: --Content is a work in progress--**

## Using SSH for logging into your RPi from your Desktop

When I work remotely from my RPi's i'm logging into them using the secure shell client (**ssh**.)  This is one of a suite of command-line tools which help us with remote access to our RPi's.  By secure shell access I mean that our communication between the two machines is encrypted.

**REF: [man(1)](https://man7.org/linux/man-pages/man1/man.1.html) pages for SSH and related tools:** The [OpenSSH Manual Pages](https://www.openssh.com/manual.html)

### Typical SSH/SCP use

Logging in to run commands on RPi:

```script
ssh pi@pip2iotgw.home    # log onto RPi pip2iotgw as the pi user

```

Copying a file to the RPi:

```script
scp file.txt pi@pip2iotgw.home:~/Documents  # copy your file to RPi:/home/pi/Documents/ folder
```

Copying the same file back to my current directory:

```script
scp pi@pip2iotgw.home:~/Documents/file.txt .  # copy file from RPi to your current folder
```

**NOTE** in these examples you see the use of the `.home` domain. This is true for my home network but most likely your network is configured differently! Please use whatever is appropriate for your network environment.

### Why I use SSH and related tools

I set up password-less ssh access to my RPi's for two major reasons:

1. I can from the command line on my desktop log into the RPi and run commands, or copy files to and from the RPi to my desktop

1. With SSH access enabled, I can work within VSCode on my Desktop but VSCode logs into the remote RPi for me and presents the files from the RPi to me as if they were on my Desktop machine. And with the terminal access built into VSCode, the commands I run in terminal are actually running on the RPi itself.  

### Enable password-less access

To work with SSH you will setup public/private keypair on your Desktop (if you haven't already, most of us already have) and you will tell the RPi about your ssh key by running the ssh-copy-id(1) command:

```script
ssh-copy-id pi@pip2iotgw.home  # then answer with RPi password and follow instructions
```

*This will prompt for the RPi password once during the setup but thereafter you can get in with out being prompted for a password.*

### Potential issues with using SSH

- SSH over WiFi can sometimes be blocked by your Wifi Access Point - it may need to be configured to allow the ssh traffic to be forwarded.  (e.g., Google Home APs can be difficult to set up - if you can even find a way to do it.)

- Sometimes your network is not fully setup for name resolution for your RPi names. In this case you can use the IP address of your RPi instead of the hostname to gain access

- Don't expect to be able to gain access to devices within your home from outside your home network. This is likely blocked unless you've specifically (and carefully configured it).  My firewall blocks all such access from outside my home and this is intentional!  I can get to any external machine (for which I'm granted access) from within my home. THis is not normally blocked.

### Light-weight network security practices

- Encrypt traffic when possible to prevent accidental exposure
- Don't let access to a network machine expose access to other machines on your network - all machines, all accounts should require authentication for access
- Shape any development password-less access to be from one, or a tiny few, of your more secure machines to the others. Don't allow the other machines to access each other (or back to your main development machines) without requiring passwords for access
- Don't attach any hardware to your network that still has default passwords for any account on the machine. Any reasonably informed attacker knows about these accounts and passwords
- Don't poke holes (allow traffic on specific ports) through your firewall unless you really know what you are doing and are doing it carefully. Test your careful work by doning penetration testing from outside to ensure you haven't created any unexpect holes in your firewall. Typical homes are **attacked many times a second** - the bad actors are trying to gain access via known ports/known services. If you expose these they will get in
- Password protect access to all wireless access points (e.g., a new device trying to connnect must provide password, use the encrypted forms of authentication)
- Have very few, one is best, external access points to your home network. Do have a firewall on every one of these external internet exposed machines which protects the rest of machines on your network 
- Remember Wireless Access Points are also an entrypoint into your home network from outside your home so make sure it's configured to defend against unwanted external users
- Don't post passwords to any network attached devices where they can be seen by people you aren't expecting to have access
- Basically do what you can to reasonably reduce accidental exposure because: If someone really wants to get into your network they will likely have more resources than you and they will get in.

### ...

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

Copyright © 2022 Iron Sheep Productions, LLC. All rights reserved.

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[marketplace-version]: https://vsmarketplacebadge.apphb.com/version-short/ironsheepproductionsllc.spin2.svg

[marketplace-installs]: https://vsmarketplacebadge.apphb.com/installs-short/ironsheepproductionsllc.spin2.svg

[marketplace-rating]: https://vsmarketplacebadge.apphb.com/rating-short/ironsheepproductionsllc.spin2.svg

[license-shield]: https://camo.githubusercontent.com/bc04f96d911ea5f6e3b00e44fc0731ea74c8e1e9/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f69616e74726963682f746578742d646976696465722d726f772e7376673f7374796c653d666f722d7468652d6261646765
