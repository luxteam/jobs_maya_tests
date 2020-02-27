#!/bin/bash
export PYTHONPATH=$PWD/../jobs/Scripts:$PYTHONPATH
export MAYA_SCRIPT_PATH=$PWD/../jobs/Scripts:$MAYA_SCRIPT_PATH
export MAYA_CMD_FILE_OUTPUT=$PWD/../Work/Results/Maya/renderTool.cb.log 

TOOL=${1:-2020}

maya${TOOL} -command "python(\"import cache_building\")"
