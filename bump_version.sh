#!/bin/sh
# Update the version and commit:
#
#   $ ./bump_version.sh X.Y.Z
#
HERE=$(dirname $(readlink -m $0))
sed -i "s/^__version__.*/__version__ = '$1'/" $HERE/odoorpc/__init__.py
sed -i "s/^version =.*/version = '$1'/" $HERE/setup.py
sed -i "s/^version =.*/version = '$1'/" $HERE/doc/source/conf.py
sed -i "s/^release =.*/release = '$1'/" $HERE/doc/source/conf.py
git ci -a -m "[IMP] Bump version to $1"
