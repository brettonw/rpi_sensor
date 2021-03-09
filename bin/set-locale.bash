#! /usr/bin/env bash

# Set locale to en_US.UTF-8
cp /etc/locale.gen /etc/locale.gen.dist;
sed -i -e "/^[^#]/s/^/#/" -e "/en_US.UTF-8/s/^#//" /etc/locale.gen;

# switch the GB to US in the existing config
cp /var/cache/debconf/config.dat /var/cache/debconf/config.dat.dist;
sed -i -e "/^Value: en_GB.UTF-8/s/en_GB/en_US/" -e "/^ locales = en_GB.UTF-8/s/en_GB/en_US/" /var/cache/debconf/config.dat;

# generate the locale
locale-gen;
update-locale LANG=en_US.UTF-8;
