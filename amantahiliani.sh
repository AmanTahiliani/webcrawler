#!/bin/bash

url="https://www.cc.gatech.edu"
pages_to_parse=1000

python3 MultiThreaded.py "$url" --pages_to_parse="$pages_to_parse"