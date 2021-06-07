#!/bin/bash
export PYTHONPATH=$PWD/../jobs/Scripts:$PYTHONPATH
export MAYA_SCRIPT_PATH=$PWD/../jobs/Scripts:$MAYA_SCRIPT_PATH
export MAYA_CMD_FILE_OUTPUT=$PWD/../Work/Results/Maya/renderTool.cb.log 

TOOL=${1:-2020}
ENGINE=${2:-Tahoe}

maya${TOOL} -command "python(\"import cache_building\")" -file "$CIS_TOOLS/../TestResources/rpr_maya_autotests_assets/material_baseline.mb"