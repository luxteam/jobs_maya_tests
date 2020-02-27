set PYTHONPATH=%CD%\..\jobs\Scripts;%PYTHONPATH%
set MAYA_SCRIPT_PATH=%CD%\..\jobs\Scripts;%MAYA_SCRIPT_PATH%
set MAYA_CMD_FILE_OUTPUT=%cd%\..\Work\Results\Maya\renderTool.cb.log 

set TOOL=%1
if not defined TOOL set TOOL=2020

"C:\Program Files\Autodesk\Maya%TOOL%\bin\maya.exe" -command "python(\"import cache_building\")"
