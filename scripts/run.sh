#!/bin/bash
RENDER_DEVICE=$1
FILE_FILTER=$2
TESTS_FILTER="$3"
RX=${4:-0}
RY=${5:-0}
SPU=${6:-25}
ITER=${7:-50}
THRESHOLD=${8:-0.05}
TOOL=${9:-2020}
ENGINE=${10:-Tahoe}
RETRIES=${11:-2}
UPDATE_REFS=${12:-No}

if [ $CIS_RENDER_DEVICE -ne "Apple M1" ]; then
    python3.9 -m pip install --user -r ../jobs_launcher/install/requirements.txt
fi

python3.9 ../jobs_launcher/executeTests.py --file_filter $FILE_FILTER --test_filter $TESTS_FILTER --tests_root ../jobs --work_root ../Work/Results --work_dir Maya --cmd_variables Tool "/Applications/Autodesk/maya${TOOL}/Maya.app/Contents/bin" RenderDevice "$RENDER_DEVICE" ResPath "$CIS_TOOLS/../TestResources/rpr_maya_autotests_assets" PassLimit $ITER rx $RX ry $RY SPU $SPU threshold $THRESHOLD engine $ENGINE retries $RETRIES UpdateRefs $UPDATE_REFS

