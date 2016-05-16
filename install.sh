#!/usr/bin/env bash
# WARNING: intended/tested for fedora/gnome 3

DESKTOP_DIR=~/.local/share/applications
WORKING_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cat $WORKING_DIR/resources/passpy.desktop | sed "s~/path/to~${WORKING_DIR}~g" \
    > $DESKTOP_DIR/passpy.desktop

chmod 755 $WORKING_DIR/pass.py

echo "alias passpy='${WORKING_DIR}/pass.py &'" >> ~/.bashrc
. ~/.bashrc

echo "Done! Be sure to have M2Crypto installed (sudo dnf install m2crypto)!"