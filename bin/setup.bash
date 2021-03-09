#!/usr/bin/env bash

# setup raspberry pi, enable wifi or wired networking
# give it a unique hostname on the network

# get the path where we are executing from
EXECUTING_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"


# get the name of the machine we are logging into
RASPBERRY_PI=$1;
if [[ -z  $RASPBERRY_PI  ]]; then
    echo "Usage: $0 <hostname> <password>";
    exit;
fi

# try to see if the machine is reachable
PING_RASPBERRY_PI="$(ping -o $RASPBERRY_PI 2>&1)";
echo $PING_RASPBERRY_PI | grep "56 data bytes" &> /dev/null;
if [ $? != 0 ]; then
    echo "Cannot connect to $RASPBERRY_PI";
    exit;
else
    echo "Found $RASPBERRY_PI";
fi

# check that we have sshpass
SSHPASS_PATH=$(which sshpass)
if [ ! -x "$SSHPASS_PATH" ]; then
    echo "building 'sshpass'...";
    $($EXECUTING_DIR/get-sshpass.bash 2>&1);
    SSHPASS_PATH=$(which sshpass)
    if [ ! -x "$SSHPASS_PATH" ]; then
        echo "    'sshpass' not installed";
        exit 1;
    fi
fi

# function to check that login works
checkLogin() {
    local LOGIN_USER=$1;
    local LOGIN_PASSWORD=$2;
    local LOGIN_MESSAGE=$3;

    echo "Logging into $LOGIN_USER@$RASPBERRY_PI ($LOGIN_MESSAGE)...";
    local LOGIN_RESPONSE="$(sshpass -p $LOGIN_PASSWORD ssh -o StrictHostKeyChecking=no $LOGIN_USER@$RASPBERRY_PI printenv 2>&1)";
    echo $LOGIN_RESPONSE | grep "USER=$LOGIN_USER" &> /dev/null;
    if [ $? == 0 ]; then
        return 0;
    else
        #echo "...Failed";
        echo "Login Response: $LOGIN_RESPONSE";
    fi
    return 1;
}

# set up a few defaults
RASPBERRY_PI_USER="pi";
RASPBERRY_PI_USER_PASSWORD="raspberry";

# we want to try to login with the defaults
checkLogin $RASPBERRY_PI_USER $RASPBERRY_PI_USER_PASSWORD "with default credentials";
if [ $? == 0 ]; then
    # get a new password for the box
    echo "Change the default password to secure the box.";
    NEW_RASPBERRY_PI_USER_PASSWORD=$2;
    while [[ -z $NEW_RASPBERRY_PI_USER_PASSWORD ]]; do
        read -p "What would you like the new password to be? " NEW_RASPBERRY_PI_USER_PASSWORD;
    done

    # actually set the password
    echo "Changing user '$RASPBERRY_PI_USER' password to ($NEW_RASPBERRY_PI_USER_PASSWORD)";
    sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "echo $RASPBERRY_PI_USER:$NEW_RASPBERRY_PI_USER_PASSWORD | sudo chpasswd" 2>&1
    RASPBERRY_PI_USER_PASSWORD=$NEW_RASPBERRY_PI_USER_PASSWORD;
else
    RASPBERRY_PI_USER_PASSWORD=$2;
    #echo "Using $RASPBERRY_PI_USER password ($RASPBERRY_PI_USER_PASSWORD)";
fi

# function to check login with specific global variables
checkLogin2() {
    local LOGIN_MESSAGE=$1;
    if [[ ! -z $RASPBERRY_PI_USER_PASSWORD ]]; then
        checkLogin $RASPBERRY_PI_USER $RASPBERRY_PI_USER_PASSWORD $LOGIN_MESSAGE;
        if [ $? != 0 ]; then
            RASPBERRY_PI_USER_PASSWORD="";
        fi
    fi
}

checkLogin2 "$RASPBERRY_PI_USER_PASSWORD";
while [[ -z $RASPBERRY_PI_USER_PASSWORD ]]; do
    read -p "What is the password for $RASPBERRY_PI_USER@$RASPBERRY_PI? " RASPBERRY_PI_USER_PASSWORD;
    checkLogin2 "retry";
done

# check that locale has been configured
currentLocale=$(sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "locale | grep 'LANG=en_US.UTF-8'");
if [[ -z $currentLocale ]]; then
    echo "Setting locale...";
    sshpass -p $RASPBERRY_PI_USER_PASSWORD scp $EXECUTING_DIR/set-locale.bash $RASPBERRY_PI_USER@$RASPBERRY_PI:~/;
    sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "sudo ~pi/set-locale.bash" 2>&1
    sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "sudo ~pi/set-locale.bash" 2>&1
    sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "sudo cp /etc/timezone /etc/timezone.dist; echo \"America/New_York\" | sudo tee /etc/timezone; sudo dpkg-reconfigure -f noninteractive tzdata;";
    sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "sudo cp /etc/default/keyboard /etc/default/keyboard.dist; sudo sed -i -e \"/XKBLAYOUT=/s/gb/us/\" /etc/default/keyboard; sudo service keyboard-setup restart;";
else
    echo "Locale is ($currentLocale)";
fi;

# try to set a host name
HOSTNAME=$(sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "hostname");
NEW_HOSTNAME="";
while [[ -z $NEW_HOSTNAME ]]; do
    read -p "What is hostname for $RASPBERRY_PI_USER@$RASPBERRY_PI? ($HOSTNAME) " NEW_HOSTNAME;
    if [ -z $NEW_HOSTNAME ]; then
        NEW_HOSTNAME=$HOSTNAME;
    fi
done
sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "sudo hostname $NEW_HOSTNAME";

# get a password to use for the new account
echo "Creating account for $USER@$RASPBERRY_PI...";
#echo "What is the password for this new user?";
#echo "(If you enter a blank password, a random one will be created)";
#read USER_PASSWORD;
USER_PASSWORD="";
if [[ -z $USER_PASSWORD ]]; then
    # if the user doesn't want to give one, we can just make one up - they will use ssh with
    # certs when we are done anyway, and they have access to the default user password with
    # sudo rights if they need to reset it
    OLD_LC_ALL="$LC_ALL";
    export LC_ALL=C;
    USER_PASSWORD=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1);
    export LC_ALL="$OLD_LC_ALL";
    echo "Created password for $USER ($USER_PASSWORD).";
fi

# try to login with the supplied credentials
checkLogin $USER $USER_PASSWORD "new user"
if [ $? != 0 ]; then
    # if that fails, create a new user and set the password
    echo "Creating new account...";
    sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "sudo adduser $USER --gecos '' --disabled-password" 2>&1
    sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "sudo usermod $USER -a -G pi,adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,netdev,spi,i2c,gpio" 2>&1
    echo "Updating password...";
    sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "echo $USER:$USER_PASSWORD | sudo chpasswd" 2>&1
else
    echo "Using existing account...";
fi

# update sudoers so <me> can sudo without passwords
echo "Checking for $USER in /etc/sudoers.d...";
sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "ls -1 /etc/sudoers.d | grep \"010_$USER\"" 2>&1
if [ $? != 0 ]; then
    echo "Adding $USER to /etc/sudoers.d...";
    sshpass -p $RASPBERRY_PI_USER_PASSWORD ssh $RASPBERRY_PI_USER@$RASPBERRY_PI "echo \"$USER ALL=(ALL) NOPASSWD: ALL\" | sudo tee /etc/sudoers.d/010_$USER-nopasswd > /dev/null" 2>&1;
fi

# from now on, we don't need to specify the user to the ssh commands, they will default to <me>


# if authorized keys doesn't exist
sshpass -p $USER_PASSWORD ssh $RASPBERRY_PI "test -e ~/.ssh/authorized_keys";
if [ $? != 0 ]; then
    # copy the identity so I can login quietly from now on - we copy the keys too, so we can
    # use git quietly
    echo "Installing certs...";
    sshpass -p $USER_PASSWORD ssh $RASPBERRY_PI "mkdir -p -m 700 .ssh";
    echo "  ...authorized keys";
    sshpass -p $USER_PASSWORD scp ~/.ssh/id_rsa.pub $RASPBERRY_PI:.ssh/authorized_keys;
    echo "  ...id";
    sshpass -p $USER_PASSWORD scp ~/.ssh/id_rsa $RASPBERRY_PI:.ssh/;
    echo "  ...pub";
    sshpass -p $USER_PASSWORD scp ~/.ssh/id_rsa.pub $RASPBERRY_PI:.ssh/;
    echo "  ...known_hosts";
    sshpass -p $USER_PASSWORD scp $EXECUTING_DIR/known_hosts $RASPBERRY_PI:.ssh/;
    echo "Done installing certs.";
else
    echo "Using existing certs...";
fi

# from now on, should be able to do operations without sshpass

# force update on all software packages (sudo apt-get update && sudo apt-get upgrade)
echo "Update raspberry pi...";
ssh $RASPBERRY_PI "sudo apt-get update -y && sudo apt-get full-upgrade -y;"

echo "Install software...";
ssh $RASPBERRY_PI "sudo apt-get install git apache2 python3-pip python3-gpiozero -y;"

# copy bashrc from ./config to /home/<me>/.bashrc
echo "Configuring home...";
scp $EXECUTING_DIR/.bashrc $RASPBERRY_PI:~/.bashrc
ssh $RASPBERRY_PI "echo > .hushlogin"
ssh $RASPBERRY_PI "if [ ! -d bin ]; then mkdir bin; fi;"

# git clone repository
echo "Cloning...";
ssh $RASPBERRY_PI "if [ ! -d rpi_sensor ]; then git clone git@github.com:brettonw/rpi_sensor.git; fi;"

# reboot the box to complete everything
ssh $RASPBERRY_PI "sudo reboot now";
