#!/usr/bin/env bash
#
# Copyright (C) 2016-2021 Savoir-faire Linux Inc.
#
# Author: Alexandre Viau <alexandre.viau@savoirfairelinux.com>
# Author: Maxim Cournoyer <maxim.cournoyer@savoirfairelinux.com>
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

# Import the spec file.
mkdir -p /opt/ring-project
cd /opt/ring-project
cp /opt/ring-project-ro/packaging/rules/rpm/* .

# Prepare the build tree.
rpmdev-setuptree

# Copy the source tarball.
cp /opt/ring-project-ro/jami_*.tar.gz /root/rpmbuild/SOURCES

# TODO if distrib
mkdir /opt/qt-jami-build
cd /opt/qt-jami-build

QT_MAJOR=5
QT_MINOR=15
QT_PATCH=0
wget https://download.qt.io/archive/qt/${QT_MAJOR}.${QT_MINOR}/${QT_MAJOR}.${QT_MINOR}.${QT_PATCH}/single/qt-everywhere-src-${QT_MAJOR}.${QT_MINOR}.${QT_PATCH}.tar.xz

if ! echo -n ${QT_TARBALL_CHECKSUM} qt-everywhere-src-*.tar.xz | sha256sum -c -
then
    echo "qt tarball checksum mismatch; quitting"
    exit 1
fi

mv qt-everywhere-src-${QT_MAJOR}.${QT_MINOR}.${QT_PATCH}.tar.xz /root/rpmbuild/SOURCES/jami-qtlib_${QT_MAJOR}.${QT_MINOR}.${QT_PATCH}.tar.xz
sed -i "s/RELEASE_VERSION/${RELEASE_VERSION}/g" jami-libqt.spec

# Set the version and associated comment.
sed -i "s/RELEASE_VERSION/${QT_MAJOR}.${QT_MINOR}.${QT_PATCH}/g" *.spec
rpmdev-bumpspec --comment="Automatic nightly release" \
                --userstring="Jenkins <jami@lists.savoirfairelinux.net>" *.spec


rpmbuild -ba jami-qtlib.spec

exit 0

# Build the daemon and install it.
rpmbuild -ba jami-daemon.spec
rpm --install /root/rpmbuild/RPMS/x86_64/jami-daemon-*

# Build the client library and install it.
rpmbuild -ba jami-libclient.spec
rpm --install /root/rpmbuild/RPMS/x86_64/jami-libclient-*

# Build the GNOME and Qt clients.
rpmbuild -ba jami-gnome.spec jami-qt.spec

# Move the built packages to the output directory.
mv /root/rpmbuild/RPMS/*/* /opt/output
touch /opt/output/.packages-built
chown -R ${CURRENT_UID}:${CURRENT_UID} /opt/output

# TODO: One click install: create a package that only installs the
# Jami RPM repo, the GPG key, then proceeds install the jami-qt
# package (will should at this point pull its own dependencies such as
# jami-libclient and jami-daemon from the newly configured
# repository).  See how Cisco OpenH264, Google Chrome, rpmfusion, COPR
# do it for inspiration.

## JAMI ONE CLICK INSTALL RPM

#copy script jami-all.postinst which add repo
mkdir -p /root/rpmbuild/BUILD/ring-project/packaging/rules/one-click-install/
cp jami-all.postinst  /root/rpmbuild/BUILD/ring-project/packaging/rules/one-click-install/

# build the package
rpmbuild -ba jami-gnome.spec jami-qt.spec

# move to output
mkdir -p /opt/output/one-click-install
mv /root/rpmbuild/RPMS/*/* /opt/output/one-click-install
touch /opt/output/one-click-install/.packages-built
chown -R ${CURRENT_UID}:${CURRENT_UID} /opt/output/one-click-install