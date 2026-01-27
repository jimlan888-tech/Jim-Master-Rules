#!/bin/bash
set -e
npm config set registry https://registry.npmmirror.com
npm config delete proxy || true
pip3 install --upgrade pip
pip3 install opencv-python ultralytics RPi.GPIO pigpio
