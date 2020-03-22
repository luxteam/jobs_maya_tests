#!/bin/bash
export PYTHONPATH=$PWD/../jobs/Scripts:$PYTHONPATH
export MAYA_SCRIPT_PATH=$PWD/../jobs/Scripts:$MAYA_SCRIPT_PATH
export MAYA_CMD_FILE_OUTPUT=$PWD/../Work/Results/Maya/renderTool.cb.log 

TOOL=${1:-2020}

/Applications/Autodesk/Maya${TOOL}/Maya.app/Contents/bin/Render -r FireRender -rgb true -log "%MAYA_CMD_FILE_OUTPUT%/renderTool.cb.log" -rd "%MAYA_CMD_FILE_OUTPUT%" -im "cache_building" -of jpg "$CIS_TOOLS/../TestResources/MayaAssets/cache.mb"
