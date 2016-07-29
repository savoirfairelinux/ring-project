#!/usr/bin/env bash
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
# This script is used in the packaging containers to build packages on
# rpm-based distros.
#

set -e

cp -r /opt/ring-project-ro /opt/ring-project
cd /opt/ring-project

# import the spec file
cp packaging/rules/fedora/ring.spec .

# Set the version
sed -i 's/RELEASE_VERSION/${RELEASE_VERSION}/g' ring.spec
rpmdev-bumpspec --comment="Automatic nightly release" --userstring="Jenkins <ring@lists.savoirfairelinux.net>" ring.spec

# install build deps
yum-builddep ring.spec

# create orig tarball
# TODO: maybe strip things from the package here, just like we do in Debian.
mv ${RELEASE_TARBALL_FILENAME} ../ring_${DEBIAN_VERSION}.orig.tar.gz

GET_ORIG_SOURCE_OVERRIDE_USCAN_TARBALL=$(readlink -f ../ring_*.orig.tar.gz) debian/rules get-orig-source

# move the tarball to the work directory
mkdir -p /opt/ring-packaging
mv ring_*.orig.tar.gz /opt/ring-packaging

# move to work directory
cd /opt/ring-packaging

# unpack the orig tarball
tar -xvf /opt/ring-packaging/ring_*.orig.tar.gz

# move to ring-project dir
cd ring-project

# import debian folder into ring-packaging directory
cp --verbose -r /opt/ring-project/debian .

# create the package
dpkg-buildpackage -uc -us

# move the artifacts to output
cd ..
mv *.orig.tar* *.debian.tar* *deb *changes *dsc /opt/output
chown -R ${CURRENT_UID}:${CURRENT_UID} /opt/output
