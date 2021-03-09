# If not running interactively, don't do anything
[[ "$-" != *i* ]] && return

# Use case-insensitive filename globbing
shopt -s nocaseglob;

# When changing directory small typos can be ignored by bash
# for example, cd /vr/lgo/apaache would find /var/log/apache
shopt -s cdspell;

set -a

PS1="\! (\h) \W : ";
HISTCONTROL=ignoredups;
unset HISTFILE;

LC_CTYPE=en_US.UTF-8;
LC_ALL=en_US.UTF-8;

GPG_TTY=$(tty);

PATH=.:~/bin:~/rpi_sensor/rpi/bin:$PATH;
set +a

function ec {
    nano $*;
}

function sudoec {
    sudo nano $*;
}
