#!/bin/sh
set -e
target=$1
root=$2
rm -rf $root/$target
echo cleanup complete
