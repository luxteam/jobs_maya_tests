set PYTHONPATH=%CD%\..\jobs\Scripts;%PYTHONPATH%
set MAYA_SCRIPT_PATH=%CD%\..\jobs\Scripts;%MAYA_SCRIPT_PATH%
set MAYA_CMD_FILE_OUTPUT=%CD%\..\Work\Results\Maya

set TOOL=%1
if not defined TOOL set TOOL=2020

"C:\\Program Files\\Autodesk\\Maya%TOOL%\\bin\\Render.exe" -r FireRender -rgb true -log "%MAYA_CMD_FILE_OUTPUT%\renderTool.cb.log" -rd "%MAYA_CMD_FILE_OUTPUT%" -im "cache_building" -of jpg "C:\\TestResources\\MayaAssets\\cache.mb"
