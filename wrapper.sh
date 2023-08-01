#!/usr/bin/env bash

home_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd $home_dir
source ./venv/bin/activate
python3 ./ruv_downloader.py $@
