#!/bin/bash
set -e
mkdir -p demo
if [ ! -f demo/test.img ]; then
  fallocate -l 1G demo/test.img
  echo "Created demo/test.img (1G)"
else
  echo "demo/test.img already exists"
fi
echo "To attach: sudo losetup -fP demo/test.img"
