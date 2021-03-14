#! /usr/bin/env bash

pip3 install adafruit-python-shell;
pip3 install adafruit-blinka;

set_config_var() {
    lua - "$1" "$2" "$3" <<EOF > "$3.bak"
    local key=assert(arg[1])
    local value=assert(arg[2])
    local fn=assert(arg[3])
    local file=assert(io.open(fn))
    local made_change=false
    for line in file:lines() do
      if line:match("^#?%s*"..key.."=.*$") then
        line=key.."="..value
        made_change=true
      end
      print(line)
    end

    if not made_change then
      print(key.."="..value)
    end
    EOF
    mv "$3.bak" "$3"
}

# enable i2c - code based on raspi-config
SETTING=on
STATUS=enabled
CONFIG=/boot/config.txt

set_config_var dtparam=i2c_arm $SETTING $CONFIG && sed /etc/modules -i -e "s/^#[[:space:]]*\(i2c[-_]dev\)/\1/"
if ! grep -q "^i2c[-_]dev" /etc/modules; then
printf "i2c-dev\n" >> /etc/modules
fi
dtparam i2c_arm=$SETTING
modprobe i2c-dev
