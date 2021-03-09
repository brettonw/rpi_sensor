#! /usr/bin/env bash

# save our current location
origDir="$PWD";

# create and navigate to the temporary folder where we will run the install
tmpDir=$(basename $0 | sed -e "s/.bash$//");
tmpDir=$(mktemp -d -t $tmpDir);
if [ ! -d $tmpDir ]; then
  tmpDir="tmp_install";
  mkdir $tmpDir;
fi;
cd $tmpDir;
pwd;

# get the sshpass source and build it
VERSION="1.09";
curl -O -L  https://sourceforge.net/projects/sshpass/files/sshpass/$VERSION/sshpass-$VERSION.tar.gz && tar xvzf sshpass-$VERSION.tar.gz;
cd "sshpass-$VERSION";
./configure;
sudo make install;

# return to our original location and clean up
cd $origDir;
rm -rf $tmpDir;
