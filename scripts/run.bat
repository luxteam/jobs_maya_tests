set PATH=c:\python35\;c:\python35\scripts\;%PATH%
set RENDER_DEVICE=%1
set FILE_FILTER=%2
set TESTS_FILTER="%3"
rem set SPU=%4

rem if "%SPU%" EQU "" set SPU=10

python -m pip install -r ..\jobs_launcher\install\requirements.txt

python ..\jobs_launcher\executeTests.py --test_filter %TESTS_FILTER% --file_filter %FILE_FILTER% --tests_root ..\jobs --work_root ..\Work\Results --work_dir Maya --cmd_variables Tool "C:\Program Files\Autodesk\Maya2019\bin\maya.exe" RenderDevice %RENDER_DEVICE% ResPath "C:\TestResources\MayaAssets" PassLimit 50 rx 0 ry 0 SPU 10
