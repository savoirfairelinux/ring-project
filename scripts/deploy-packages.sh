#!/bin/bash
#
# Copyright (C) 2016 Savoir-faire Linux Inc.
#
# Author: Alexandre Viau <alexandre.viau@savoirfairelinux.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#
# This script sings and deploys pacakges from packages/distro.
# It should be ran from the project root directory.
#

# Exit immediately if a command exits with a non-zero status
set -e

for i in "$@"
do
case $i in
    --distribution=*)
    DISTRIBUTION="${i#*=}"
    shift
    ;;
    --keyid=*)
    KEYID="${i#*=}"
    shift
    ;;
    --remote-repository-location=*)
    REMOTE_REPOSITORY_LOCATION="${i#*=}"
    shift
    ;;
    --remote-manual-download-location=*)
    REMOTE_MANUAL_DOWNLOAD_LOCATION="${i#*=}"
    shift
    ;;
    *)
    echo "Unrecognized option ${i}"
    exit 1
    ;;
esac
done

##################################################
## Create local repository for the given distro ##
##################################################
echo "#########################"
echo "## Creating repository ##"
echo "#########################"

DISTRIBUTION_REPOSITOIRY_FOLDER=$(realpath repositories)/${DISTRIBUTION}
rm -rf ${DISTRIBUTION_REPOSITOIRY_FOLDER}
mkdir -p ${DISTRIBUTION_REPOSITOIRY_FOLDER}/conf

# Distributions file
cat << EOF > ${DISTRIBUTION_REPOSITOIRY_FOLDER}/conf/distributions
Origin: ring
Label: Ring ${DISTRIBUTION} Repository
Codename: ring
Architectures: i386 amd64
Components: main
Description: This repository contains Ring ${DISTRIBUTION} packages
SignWith: ${KEYID}
EOF

# Options file
cat << EOF > ${DISTRIBUTION_REPOSITOIRY_FOLDER}/conf/options
basedir ${DISTRIBUTION_REPOSITOIRY_FOLDER}
EOF

####################################
## Add packages to the repository ##
####################################

for package in packages/${DISTRIBUTION}*/*.deb; do

    # Sign the deb
    echo "## signing: ${package} ##"
    dpkg-sig -k ${KEYID} --sign builder ${package}

    # Include the deb
    echo "## including ${package} ##"
    # Removing to avoid the error of adding the same deb twice.
    # This happens with arch all packages, which are generated in amd64 and i386.
    package_name=$(dpkg -I ${package} | grep -m 1 Package: | awk '{print $2}')
    package_arch=$(dpkg -I ${package} | grep -m 1 Architecture: | awk '{print $2}')
    reprepro --verbose --basedir ${DISTRIBUTION_REPOSITOIRY_FOLDER} --architecture ${package_arch} remove ring ${package_name}
    reprepro --verbose --basedir ${DISTRIBUTION_REPOSITOIRY_FOLDER} includedeb ring ${package}
done

# Rebuild the index
reprepro --verbose --basedir ${DISTRIBUTION_REPOSITOIRY_FOLDER} export ring

# Show the contents
reprepro --verbose --basedir ${DISTRIBUTION_REPOSITOIRY_FOLDER} list ring

#######################################
## create the manual download folder ##
#######################################
DISTRIBUTION_MANUAL_DOWNLOAD_FOLDER=$(realpath manual-download)/${DISTRIBUTION}
mkdir -p ${DISTRIBUTION_MANUAL_DOWNLOAD_FOLDER}
for package in packages/${DISTRIBUTION}*/*.deb; do
    cp ${package} ${DISTRIBUTION_MANUAL_DOWNLOAD_FOLDER}
    package_name=$(dpkg -I ${package} | grep -m 1 Package: | awk '{print $2}')
    package_arch=$(dpkg -I ${package} | grep -m 1 Architecture: | awk '{print $2}')
    cp ${package} ${DISTRIBUTION_MANUAL_DOWNLOAD_FOLDER}/${package_name}_${package_arch}.deb
done

############
## deploy ##
############

# Deploy the repository
echo "##########################"
echo "## deploying repository ##"
echo "##########################"
rsync --archive --recursive --verbose --delete ${DISTRIBUTION_REPOSITOIRY_FOLDER} ${REMOTE_REPOSITORY_LOCATION}

# deploy the manual download files
echo "#####################################"
echo "## deploying manual download files ##"
echo "#####################################"
rsync --archive --recursive --verbose --delete ${DISTRIBUTION_MANUAL_DOWNLOAD_FOLDER} ${REMOTE_MANUAL_DOWNLOAD_LOCATION}

# remove deployed files
rm -rf manual-download
rm -rf repositories
