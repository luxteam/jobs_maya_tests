set PATH=c:\python39\;c:\python39\scripts\;%PATH%

python ..\jobs_launcher\executeTests.py --tests_root ..\jobs_special --work_root ..\Work\Results --work_dir Maya --cmd_variables Tool "C:\Program Files\Autodesk\Maya2018\bin\maya.exe" RenderDevice gpu ResPath "C:\TestResources\rpr_gltf_autotests_assets\Maya" PassLimit 50 rx 0 ry 0 SPU 10