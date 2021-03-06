# shellcheck shell=bash

set -ex

getconf _NPROCESSORS_ONLN
free -m
df -h
df -h /var/tmp

export CH_TEST_TARDIR=/var/tmp/tarballs
export CH_TEST_IMGDIR=/var/tmp/images
export CH_TEST_PERMDIRS='/var/tmp/perms_test /run/perms_test'

unset JAVA_HOME  # otherwise Spark tries to use host's Java

sudo usermod --add-subuids 10000-65536 "$USER"
sudo usermod --add-subgids 10000-65536 "$USER"

[[ $CH_BUILDER ]]  # no default builder for Travis
if [[ $CH_BUILDER != docker ]]; then
    export SUDO_RM_FIRST=yes
    sudo rm "$(command -v docker)"
fi

set +ex
