set PYTHONPATH=%CD%\..\jobs\Scripts;%PYTHONPATH%
set MAYA_SCRIPT_PATH=%CD%\..\jobs\Scripts;%MAYA_SCRIPT_PATH%

set TOOL=%1
set ENGINE=%2
set LOG_FILE=%3

if not defined TOOL set TOOL=2020
if not defined ENGINE set ENGINE=Tahoe
if not defined LOG_FILE set LOG_FILE=renderTool.cb.log

set MAYA_CMD_FILE_OUTPUT=%CD%\%LOG_FILE%

"C:\Program Files\Autodesk\Maya%TOOL%\bin\maya.exe" -command "python(\"import cache_building\")" -file "C:\\TestResources\\rpr_maya_autotests_assets\\material_baseline.mb"