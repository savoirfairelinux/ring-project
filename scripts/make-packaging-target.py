#!/usr/bin/env python3
#
# Copyright (C) 2016-2021 Savoir-faire Linux Inc.
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
# Creates packaging targets for a distribution and architecture.
# This helps reduce the length of the top Makefile.
#

import argparse

template_header = """\
# -*- mode: makefile -*-
# This file was auto-generated by: scripts/make-packaging-target.py.
#
# We don't simply use jami-packaging-distro as the docker image name because
# we want to be able to build multiple versions of the same distro at the
# same time and it could result in race conditions on the machine as we would
# overwrite the docker image of other builds.
#
# This does not impact caching as the docker daemon does not care about the image
# names, just about the contents of the Dockerfile.
"""

target_template = """\
##
## Distro: %(distribution)s
##

PACKAGE_%(distribution)s_DOCKER_IMAGE_NAME:=jami-packaging-%(distribution)s$(RING_PACKAGING_IMAGE_SUFFIX)
PACKAGE_%(distribution)s_DOCKER_IMAGE_FILE:=.docker-image-$(PACKAGE_%(distribution)s_DOCKER_IMAGE_NAME)
DOCKER_EXTRA_ARGS =


PACKAGE_%(distribution)s_DOCKER_RUN_COMMAND = docker run \\
    --rm \\
    -e RELEASE_VERSION=$(RELEASE_VERSION) \\
    -e RELEASE_TARBALL_FILENAME=$(RELEASE_TARBALL_FILENAME) \\
    -e DEBIAN_VERSION=%(version)s \\
    -e CURRENT_UID=$(CURRENT_UID) \\
    -e CURRENT_GID=$(CURRENT_GID) \\
    -e DISTRIBUTION=%(distribution)s \\
    -v $(CURDIR):/opt/ring-project-ro:ro \\
    -v $(CURDIR)/packages/%(distribution)s:/opt/output \\
    -t $(DOCKER_EXTRA_ARGS) %(options)s \\
    $(PACKAGE_%(distribution)s_DOCKER_IMAGE_NAME)

$(PACKAGE_%(distribution)s_DOCKER_IMAGE_FILE): docker/Dockerfile_%(docker_image)s
	docker build \\
        -t $(PACKAGE_%(distribution)s_DOCKER_IMAGE_NAME) \\
        -f docker/Dockerfile_%(docker_image)s %(docker_build_args)s \\
        $(CURDIR)
	touch $(PACKAGE_%(distribution)s_DOCKER_IMAGE_FILE)

packages/%(distribution)s:
	mkdir -p packages/%(distribution)s

packages/%(distribution)s/%(output_file)s: $(RELEASE_TARBALL_FILENAME) packages/%(distribution)s $(PACKAGE_%(distribution)s_DOCKER_IMAGE_FILE)
	$(PACKAGE_%(distribution)s_DOCKER_RUN_COMMAND)
	touch packages/%(distribution)s/*

.PHONY: package-%(distribution)s
package-%(distribution)s: packages/%(distribution)s/%(output_file)s
PACKAGE-TARGETS += package-%(distribution)s

.PHONY: package-%(distribution)s-interactive
package-%(distribution)s-interactive: DOCKER_EXTRA_ARGS = -i
package-%(distribution)s-interactive: $(RELEASE_TARBALL_FILENAME) packages/%(distribution)s $(PACKAGE_%(distribution)s_DOCKER_IMAGE_FILE)
	$(PACKAGE_%(distribution)s_DOCKER_RUN_COMMAND) bash
"""


RPM_BASED_SYSTEMS_DOCKER_RUN_OPTIONS = (
    '--security-opt seccomp=./docker/profile-seccomp-fedora_28.json '
    '--privileged')


def generate_target(distribution, output_file, options='', docker_image='', version='', docker_build_args = ''):
    if (docker_image == ''):
        docker_image = distribution
    if (version == ''):
        version = "$(DEBIAN_VERSION)"
    return target_template % {
        "distribution": distribution,
        "docker_image": docker_image,
        "output_file": output_file,
        "options": options,
        "version": version,
        "docker_build_args": docker_build_args,
    }


def run_generate(parsed_args):
    print(generate_target(parsed_args.distribution,
                          parsed_args.output_file,
                          parsed_args.options,
                          parsed_args.docker_image,
                          parsed_args.version))


def run_generate_all(parsed_args):
    targets = [
        # Debian
        {
            "distribution": "debian_10",
            "output_file": "$(DEBIAN_DSC_FILENAME)",
            "options": "-e QTVER=$(QT_MAJOR).$(QT_MINOR).$(QT_PATCH) --privileged --security-opt apparmor=docker-default",
        },
        {
            "distribution": "debian_10_i386",
            "output_file": "$(DEBIAN_DSC_FILENAME)",
            "options": "--privileged --security-opt apparmor=docker-default",
        },
        {
            "distribution": "debian_10_armhf",
            "output_file": "$(DEBIAN_DSC_FILENAME)",
            "options": "--privileged --security-opt apparmor=docker-default",
        },
        {
            "distribution": "debian_10_arm64",
            "output_file": "$(DEBIAN_DSC_FILENAME)",
            "options": "--privileged --security-opt apparmor=docker-default"
        },
        {
            "distribution": "debian_10_qt",
            "output_file": "$(DEBIAN_QT_DSC_FILENAME)",
            "options": "-e QT_MAJOR=$(QT_MAJOR) -e QT_MINOR=$(QT_MINOR) -e QT_PATCH=$(QT_PATCH) -e QT_TARBALL_CHECKSUM=$(QT_TARBALL_CHECKSUM) --privileged --security-opt apparmor=docker-default",
            "version": "$(DEBIAN_QT_VERSION)",
        },
        {
            "distribution": "debian_10_oci",
            "docker_image": "debian_10",
            "output_file": "$(DEBIAN_OCI_DSC_FILENAME)",
            "options": "-e OVERRIDE_PACKAGING_DIR=$(DEBIAN_OCI_PKG_DIR) --privileged --security-opt apparmor=docker-default",
            "version": "$(DEBIAN_OCI_VERSION)",
        },
        {
            "distribution": "debian_10_i386_oci",
            "docker_image": "debian_10_i386",
            "output_file": "$(DEBIAN_OCI_DSC_FILENAME)",
            "options": "-e OVERRIDE_PACKAGING_DIR=$(DEBIAN_OCI_PKG_DIR) --privileged --security-opt apparmor=docker-default",
            "version": "$(DEBIAN_OCI_VERSION)",
        },
        {
            "distribution": "debian_10_armhf_oci",
            "docker_image": "debian_10_armhf",
            "output_file": "$(DEBIAN_DSC_FILENAME)",
            "options": "-e OVERRIDE_PACKAGING_DIR=$(DEBIAN_OCI_PKG_DIR) --privileged --security-opt apparmor=docker-default",
            "version": "$(DEBIAN_OCI_VERSION)"
        },
        {
            "distribution": "debian_10_arm64_oci",
            "docker_image": "debian_10_arm64",
            "output_file": "$(DEBIAN_DSC_FILENAME)",
            "options": "-e OVERRIDE_PACKAGING_DIR=$(DEBIAN_OCI_PKG_DIR) --privileged --security-opt apparmor=docker-default",
            "version": "$(DEBIAN_OCI_VERSION)"
        },
        # Raspbian
        {
            "distribution": "raspbian_10_armhf",
            "output_file": "$(DEBIAN_DSC_FILENAME)",
            "options": "--privileged --security-opt apparmor=docker-default",
        },
        {
            "distribution": "raspbian_10_armhf_oci",
            "docker_image": "raspbian_10_armhf",
            "output_file": "$(DEBIAN_DSC_FILENAME)",
            "options": "-e OVERRIDE_PACKAGING_DIR=$(DEBIAN_OCI_PKG_DIR) --privileged --security-opt apparmor=docker-default",
            "version": "$(DEBIAN_OCI_VERSION)",
        },
        # Ubuntu
        {
            "distribution": "ubuntu_18.04",
            "output_file": "$(DEBIAN_DSC_FILENAME)",
        },
        {
            "distribution": "ubuntu_18.04_i386",
            "output_file": "$(DEBIAN_DSC_FILENAME)",
        },
        {
            "distribution": "ubuntu_18.04_oci",
            "docker_image": "ubuntu_18.04",
            "output_file": "$(DEBIAN_OCI_DSC_FILENAME)",
            "options": "-e OVERRIDE_PACKAGING_DIR=$(DEBIAN_OCI_PKG_DIR)",
            "version": "$(DEBIAN_OCI_VERSION)",
        },
        {
            "distribution": "ubuntu_18.04_i386_oci",
            "docker_image": "ubuntu_18.04_i386",
            "output_file": "$(DEBIAN_OCI_DSC_FILENAME)",
            "options": "-e OVERRIDE_PACKAGING_DIR=$(DEBIAN_OCI_PKG_DIR)",
            "version": "$(DEBIAN_OCI_VERSION)",
        },
        {
            "distribution": "ubuntu_20.04",
            "output_file": "$(DEBIAN_DSC_FILENAME)",
            "options": "--privileged --security-opt apparmor=docker-default",
        },
        {
            "distribution": "ubuntu_20.04_oci",
            "docker_image": "ubuntu_20.04",
            "output_file": "$(DEBIAN_OCI_DSC_FILENAME)",
            "options": "-e OVERRIDE_PACKAGING_DIR=$(DEBIAN_OCI_PKG_DIR) --privileged --security-opt apparmor=docker-default",
            "version": "$(DEBIAN_OCI_VERSION)",
        },
        {
            "distribution": "ubuntu_20.10",
            "output_file": "$(DEBIAN_DSC_FILENAME)",
            "options": "--privileged --security-opt apparmor=docker-default",
        },
        {
            "distribution": "ubuntu_20.10_oci",
            "docker_image": "ubuntu_20.10",
            "output_file": "$(DEBIAN_OCI_DSC_FILENAME)",
            "options": "-e OVERRIDE_PACKAGING_DIR=$(DEBIAN_OCI_PKG_DIR) --privileged --security-opt apparmor=docker-default",
            "version": "$(DEBIAN_OCI_VERSION)",
        },

        # Fedora
        {
            "distribution": "fedora_32",
            "output_file": ".packages-built",
            "options": RPM_BASED_SYSTEMS_DOCKER_RUN_OPTIONS
        },
        {
            "distribution": "fedora_33",
            "output_file": ".packages-built",
            "options": RPM_BASED_SYSTEMS_DOCKER_RUN_OPTIONS
        },
        {
            "distribution": "rhel_8",
            "output_file": ".packages-built",
            "options": RPM_BASED_SYSTEMS_DOCKER_RUN_OPTIONS,
            "docker_build_args": "--build-arg PASS=${PASS}"
        },
        # OpenSUSE
        {
            "distribution": "opensuse-leap_15.2",
            "output_file": ".packages-built",
            "options": RPM_BASED_SYSTEMS_DOCKER_RUN_OPTIONS
        },
        {
            "distribution": "opensuse-tumbleweed",
            "output_file": ".packages-built",
            "options": RPM_BASED_SYSTEMS_DOCKER_RUN_OPTIONS
        },
        # Snap
        {
            "distribution": "snap",
            "output_file": ".packages-built",
        },

    ]

    for target in targets:
        print(generate_target(**target))


def parse_args():
    ap = argparse.ArgumentParser(
        description="Packaging targets generation tool"
    )

    ga = ap.add_mutually_exclusive_group(required=True)

    # Action arguments
    ga.add_argument('--generate',
                    action='store_true',
                    help='Generate a single packaging target')
    ga.add_argument('--generate-all',
                    action='store_true',
                    help='Generates all packaging targets')

    # Parameters
    ap.add_argument('--distribution')
    ap.add_argument('--output_file')
    ap.add_argument('--options', default='')
    ap.add_argument('--docker_image', default='')
    ap.add_argument('--version', default='')

    parsed_args = ap.parse_args()

    return parsed_args


def main():
    parsed_args = parse_args()

    print(template_header)
    if parsed_args.generate:
        run_generate(parsed_args)
    elif parsed_args.generate_all:
        run_generate_all(parsed_args)

if __name__ == "__main__":
    main()
