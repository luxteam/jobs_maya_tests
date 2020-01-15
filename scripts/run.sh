#!/bin/bash
RENDER_DEVICE=$1
FILE_FILTER=$2
TESTS_FILTER="$3"

python3 -m pip install -r ../jobs_launcher/install/requirements.txt
python3 ../jobs_launcher/executeTests.py --file_filter $FILE_FILTER --test_filter $TESTS_FILTER --tests_root ../jobs --work_root ../Work/Results --work_dir Maya --cmd_variables Tool maya2019 RenderDevice "$RENDER_DEVICE" ResPath "$CIS_TOOLS/../TestResources/MayaAssets" PassLimit 50 rx 0 ry 0 SPU 10
