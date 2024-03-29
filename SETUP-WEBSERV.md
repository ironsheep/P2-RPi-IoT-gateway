# P2 RPi ioT Gateway - RPi Backend Webserver Setup

Enable an RPi to serve as an ioT gateway for our P2 Hardware - while dedicating only 2 pins for serial communication

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

## Install the Backend web server along with the PHP interpreter

By default our Raspberry Pi OS that we chose does not come with the web server installed. However it is very easy to install it.  

Before we do any new software installation let's make sure we have the latest updates to our existing installed software.  Remember the `upd` command you installed. Let's run that now:

```bash
$ upd
+ sudo apt-get update
Hit:1 http://archive.raspberrypi.org/debian bullseye InRelease                                                      
Hit:2 http://raspbian.raspberrypi.org/raspbian bullseye InRelease                                                   
Reading package lists... Done
+ sudo apt-get dist-upgrade
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
Calculating upgrade... Done
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
```

Ok, ours is up-to-date.

Now let's install the web server and it's documentation:

```bash
$ sudo apt-get install apache2 apache2-doc php
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following additional packages will be installed:
  apache2-bin apache2-data apache2-utils libapr1 libaprutil1 libaprutil1-dbd-sqlite3 libapache2-mod-php7.4 php-common php7.4 php7.4-cli php7.4-common php7.4-json php7.4-opcache php7.4-readline libaprutil1-ldap liblua5.3-0
Suggested packages:
  apache2-suexec-pristine | apache2-suexec-custom php-pear
The following NEW packages will be installed:
  apache2 apache2-bin apache2-data apache2-doc apache2-utils libapr1 libaprutil1 libaprutil1-dbd-sqlite3 libaprutil1-ldap liblua5.3-0 libapache2-mod-php7.4 php php-common php7.4 php7.4-cli php7.4-common php7.4-json php7.4-opcache php7.4-readline
0 upgraded, 10 newly installed, 0 to remove and 0 not upgraded.
Need to get 6,260 kB of archives.
After this operation, 32.6 MB of additional disk space will be used.
Do you want to continue? [Y/n] 
```

(Simply press return at the [Y/n] prompt to proceed with the install.)

### Adjust web page folders

Let's adjust the web page folders so that creating files at the `pi` user will not interfere with the pages being dimsplayed:

```bash
ls -lh /var/www/
sudo chgrp www-data /var/www  # set group to the web server group
sudo chmod g+s /var/www  # set sticky bit so files created under here will be set to group
sudo chown -R pi:www-data /var/www/html/  # recursively change owner of files/folder within
sudo chmod g+s /var/www/html
sudo chmod -R 770 /var/www/html/ 
ls -lh /var/www/
sudo service apache2 restart  # restart server to pick up latest changes
```

### Allow .php files as default page in folder

Let's adjust the apache2 setup so that .php suffixed entry pages in folder just work (without needing the .php suffix)

Let's edit the **/etc/apache2/sites-enabled/000-default.conf** file (using sudo vi {filename} of course)  Make the following content adjustment:

```bash
        DocumentRoot /var/www/html   # locate this line
        DirectoryIndex index.html index.htm index.php  # add this line !!
```

Once this line is added, then restart the server to pick up the change:

```bash
sudo service apache2 restart  # restart server to pick up latest changes
```

This configuration addition allows us to now have `.../folder/index.php` files as our top-level files under `/var/www/html/`  this makes it real easy to support many projects as we simply create a new `/var/www/html/{newFolder}` and then create `/var/www/html/{newFolder}/index.php` and place our new web-page content in this new file.

When browsing to your new project your URL looks someting like: `http://{mypihostname|orIpAddress/{newFolder}` 

*Pretty nice, right?*


### Create PHP Test page

Create a simple but useful PHP test file. Let's change to our web server directory:

```bash
cd /var/www/html
```

Now create the file  `info.php` in this directory. The file should contain the following 3 lines:

```php
<?php  
phpinfo()
?>
```

### Testing the install

Now let's test both the server and the php execution under the server:

Browse to `http://{fullrpihostname|or ip address}/` - this should display the default web page:

![RPi New install Web page](./Docs/images/DefaultWWWPage.png)

Next, browse to `http://{fullrpihostname|or ip address}/info.php` - this should display the new PHP Info page:


![New PHP Info Page](./Docs/images/NewPhpInfoPage.png)

If you are seeing these pages the Apache2 web server and the PHP interpreter packages are installed and working. You are now ready to play with the new Web Served P2 data DEMOs!

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

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[marketplace-version]: https://vsmarketplacebadge.apphb.com/version-short/ironsheepproductionsllc.spin2.svg

[marketplace-installs]: https://vsmarketplacebadge.apphb.com/installs-short/ironsheepproductionsllc.spin2.svg

[marketplace-rating]: https://vsmarketplacebadge.apphb.com/rating-short/ironsheepproductionsllc.spin2.svg

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
