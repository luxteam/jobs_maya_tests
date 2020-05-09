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

shift
shift
shift
shift
shift
shift
shift
shift
shift

RBS_BUILD_ID=$1
RBS_JOB_ID=$2
RBS_URL=$3
RBS_ENV_LABEL=$4
IMAGE_SERVICE_URL=$5
RBS_USE=$6

python3 -m pip install -r ../jobs_launcher/install/requirements.txt

python3 ../jobs_launcher/executeTests.py --file_filter $FILE_FILTER --test_filter $TESTS_FILTER --tests_root ../jobs --work_root ../Work/Results --work_dir Maya --cmd_variables Tool "maya${TOOL}" RenderDevice "$RENDER_DEVICE" ResPath "$CIS_TOOLS/../TestResources/MayaAssets" PassLimit $ITER rx $RX ry $RY SPU $SPU threshold $THRESHOLD
