# rpi_sensor

## Instructions
### Image the SD Card
### Setup a Raspberry Pi (headless)
- Use the [Raspberry Pi Imager](https://www.raspberrypi.org/software/) to put Pi OS Lite on an SD Card.
- After the image is complete, mount the SD card again. It will be a partition called, "boot".
- Copy the files from "rpi_sensor/boot" to the "boot" partition.
- Unmount the SD card, put it into a Raspberry Pi, and power it up.

### First steps to configure
After the Raspberry Pi boots and connects to your WiFi, connect to it from a shell on your computer:
```
    ssh pi@<ip address>
```
The default password is "raspberry", and you should change this immediately after logging in:
```
    passwd
```
I like to get rid of all the "stuff" that the system tells you when you login:
```
    echo > .hushlogin
```
Then you will need to configure the software:
```
    sudo raspi-config
```
* Option 6, "Advanced Options" -> "Expand Filesystem", exit and reboot. It will ask you if you want to reboot, if you say "no" you can reboot manually like this:
```
    sudo reboot now
```

After logging in again, run "raspi-config" and take the following steps:
```
    sudo raspi-config
```
* Option 8, "Update"
* Option 1, "System Options" -> Hostname
* Option 5, "Localisation Options" -> (Locale | Timezone | Keyboard | WLAN Country), in that order.
    - I use locale "en_US.UTF8", and uncheck "en_GB..."

After all of that, I like to reboot the system and log in again.

### Update and set up a new user:
To update the software on the computer and add a new user, I run the following steps:
```
    sudo apt update -y && sudo apt full-upgrade -y
    # this might take a little while
    
    sudo adduser <username>
    sudo usermod <username> -a -G pi,adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,netdev,spi,i2c,gpio
    cd /etc/sudoers.d
    sudo cp 010_pi-nopasswd 010_<username>-nopasswd
    sudo nano 010_<username>-nopasswd
    # change the username from "pi" to <username> in the file
```
From your host computer, copy your .ssh directory and .bashrc to the new machine (omit <username> if it's the same as your host username):
```
    scp -r .ssh <username>@<raspberrypi-hostname>:~/
    scp .bashrc <username>@<raspberrypi-hostname>:~/
```

### Install software
```
    sudo apt install git apache2 python3-pip python3-gpiozero -y
```

### Testing the Bedrock service
```
curl -X POST -d '{"name": "linuxize", "event": "ok"}' -H "Content-Type: application/json; charset=UTF-8" http://localhost/cgi-bin/rpi_sensor.py -i
```
