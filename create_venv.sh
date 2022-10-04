#!/bin/bash

set -e

sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
