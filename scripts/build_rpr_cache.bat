
set PYTHONPATH=%cd%;PYTHONPATH
set MAYA_SCRIPT_PATH=%cd%;%MAYA_SCRIPT_PATH%
set MAYA_CMD_FILE_OUTPUT=%cd%/renderTool.cb.log 

set TOOL=%1
if not defined TOOL set TOOL=2020

"C:\Program Files\Autodesk\Maya%TOOL%\bin\maya.exe" -command "python(\"import cache_building\")"
