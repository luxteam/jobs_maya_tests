set PATH=c:\python39\;c:\python39\scripts\;%PATH%
set RENDER_DEVICE=%1
set FILE_FILTER=%2
set TESTS_FILTER="%3"
set RX=%4
set RY=%5
set SPU=%6
set ITER=%7
set THRESHOLD=%8
set TOOL=%9
shift
set ENGINE=%9
shift
set RETRIES=%9
shift
set UPDATE_REFS=%9

if not defined RX set RX=0
if not defined RY set RY=0
if not defined SPU set SPU=25
if not defined ITER set ITER=50
if not defined THRESHOLD set THRESHOLD=0.05
if not defined TOOL set TOOL=2020
if not defined ENGINE set ENGINE=Tahoe
if not defined RETRIES set RETRIES=2
if not defined UPDATE_REFS set UPDATE_REFS="No"

python -m pip install -r ..\jobs_launcher\install\requirements.txt

python ..\jobs_launcher\executeTests.py --test_filter %TESTS_FILTER% --file_filter %FILE_FILTER% --tests_root ..\jobs --work_root ..\Work\Results --work_dir Maya --cmd_variables Tool "C:\Program Files\Autodesk\Maya%TOOL%\bin\maya.exe" RenderDevice %RENDER_DEVICE% ResPath "C:\TestResources\MayaAssets" PassLimit %ITER% rx %RX% ry %RY% SPU %SPU% threshold %THRESHOLD% engine %ENGINE% retries %RETRIES% UpdateRefs %UPDATE_REFS%
