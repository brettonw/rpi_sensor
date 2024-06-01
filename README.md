# rpi_sensor

## Controller
A controller is an external system that manages devices. the rpi_sensor is NOT a controller for cross-device management. 

## Device
A device is a collection of entities are managed as a group. At startup, the device loads the configuration and ensures that all controls are set to their last desired value. Entities are updated on a 10-second cadence (this could be made configurable in the future).

The device can be polled for status, which returns all the entities by name with the date and time of their last update, date and time of their last change, and their last known value. Note that last update and last change may not be the same thing. Controllers are responsible for tracking history if that is needed.

A future extension is for devices to post changes to a controller like Home Assistant, rather than be polled.

## Entity
An entity is an abstraction of a single-function element inside a device. It may be configured with an alias to help the user, and internal references may use either the entity name or its alias. This allows operations to be moved from one entity to another to reflect organization changes like plugging a pump into a different outlet on the strip.

### Sensors
Sensors have a "get" function, and generally report an observed piece of information.

#### Numeric Sensors
Numeric Sensors return a number, like temperature, pressure, humidity, range, pH, and etc. They may or may not have associated units. rpi_sensor does not provide unit conversion services, as this sometimes requires external information.

#### State-Based Sensors
State-based sensors return a discrete value from a list of possibilities. That could be as simple as \[on, off\], or a longer list of options like \[off, low, medium, high\] or just \[A, B, C, D, E, F, G\].

### Controls
Controls extend Sensors with the addition of a "set" function, and generally perform some action in response to the value assignment. They support the "get" function by returning the last value set. Operations performed might be to change a GPIO pin value, or use I2C to trigger a device.

#### Numeric Controls
Numeric controls take a single number as input and perform an action with it. 

#### State-Based Controls
State-based controls take a state name as input and perform an action with it.

### Adapters
Adapters translate a numeric sensor/control to a state-based one, or vice versa. Adapters must be configured with a target entity that it is adapting to another type.

#### Sensor Adapters
(It's not immediately clear that this is an interesting concept for a sensor.)

#### Control Adapters
A numeric-to-state adapter provides a way to map a numeric input to a state output. Two kinds of numeric-to-state adapters are "simple" and "Schmidt Trigger". The simple configuration should provide the ranges of values to be assigned to each state. The Schmidt trigger configuration specifies trigger ranges for changing state that are dependent on the existing state. 

A state-to-numeric adapter is configured with a numeric value for each state and calls the target with it when set.

A numeric-to-numeric adapter could be used to create a canonical or percentage-based interface to another numeric entity 

### Virtual Entities
A virtual entity can provide some enhanced functionality inside a device by combining some other entites and exposing a simple sensor or control interface. An obvious example is a thermostat for a device that has a temperature sensor, a heater control, and a cooler control. The external control is a target temperature, and the configuration specifies the heater and cooler entity along with things like temperature tolerances. We expose a generic example called a PID for this purpose.

## Drivers
Drivers connect an actual circuit device to the entity concept inside rpi_sensor. These may be the software that operates a specific I2C device, but also include install capabilities. Drivers are typically a pair, consisting of a bash script for installation and a python program for circuit interaction.

---
## update
The device transits across all entites and calling update on each driver, passing the entity description as a parameter. The returned value is compared to the existing value, and the update time and change time are updated as appropriate.

## get
The device transits across all the entities and returns a JSON-formatted string with the name of each entity and its value.

## set
A value is passed to the set method, and subsequently to the driver by the entity.

## configuration
A numeric type will always have a range, a state type will always have a list of states (is this true even for pedantic types like "switch"), should we have an explicit binary type? set parameters will be validated against the range or states. States in the entity configuration are arrays of arrays - the first entry in each array being the canonical name of that state, with synonyms that will be recognized... Entities can be configured to report or no.

---

# ALMOST ALL OF THE BELOW IS COMPLETELY OUTDATED
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
