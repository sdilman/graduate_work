#!/bin/sh
# Parameters:
# $1 - Group ID
# $2 - User ID
# $3 - Username and group
# $4 - Base path
set -e
set -x

groupadd -g "$1" "$3"
useradd -m -d "$4" -u "$2" -g "$3" -s /bin/bash "$3"
chown -R "$3":"$3" "$4"
