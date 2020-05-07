# Autotests for Radeon ProRender plugin for Autodesk Maya

[![Deployed submodule](https://rpr.cis.luxoft.com/buildStatus/icon?job=Utils/jobs_launcher-Deploy&build=last&config=release-badge)](https://rpr.cis.luxoft.com/job/Utils/job/jobs_launcher-Deploy)

## Install

1. Clone this repo
2. Get `jobs_launcher` as git submodule, using next commands
    >`git submodule init`

    >`git submodule update`
3. Run `scripts/auto_config.bat`. This script will create `scripts/Devices.config.json` for your hardware configuration.
4. Check that `rpr_maya_autotests` scenes placed in `C:/TestResources`

## Running tests

1. Go to "scripts" directory
   >`cd scripts`
2. Run `scripts/run.bat %RENDER_DEVICE% %FILE_FILTER% %TESTS_FILTER% %RX% %RY% %SPU% %ITER% %THRESHOLD% %TOOL%`. For example:

     > ./run.bat gpu none Smoke 50 50 5 0.05 2020

     Where
     * `RENDER_DEVICE` define what hardware will be used.
         0 - GPU (if you have more than one GPU, CPU index will be increased)
         1 - CPU
         RenderDevice also can take "CPU", "AMD Radeon R9 200  HD 7900 Series", if this strings exist in `Device.config.json`
     * `FILE_FILTER` is file in `jobs` directory. File can contain list of groups (see `full` file) or json structure that describes witch cases from groups should be rendered (that file must have `.json` extension). You can type `none` if you don't want to declare file. See `regression.json` or example below:
    > {
    "Group1":"case1,case2",
    "Group2":"case1,case2,case3"
    }
     * `TESTS_FILTER` is name of group that you want to render. You can use it with FILE_FILTER if file isn't `json`. You can use quotes to run several groups at the same time. For example:
    > ./run.bat gpu none "Support_2018 Support_2019"
     * `RX` and `RY` are resolution. If doesn't defines it is taken from case or manifest or run.bat default values (in this order of priority).
     * `SPU` If doesn't defines it is taken from case or manifest or run.bat default values (in this order of priority).
     * `ITER` If doesn't defines it is taken from case or manifest or run.bat default values (in this order of priority).
     * `THRESHOLD` If doesn't defines it is taken from case or manifest or run.bat default values (in this order of priority).
     * `TOOL` version of maya. 2020 is default, except support groups

## Adding test group

1. Create directory for your new group.
2. Copy manifest file (you can take it from `Smoke`). Set custom `testType`. If you need you also can change `tool`, `render_device`, `pass_limit`, `resolution_x`, `resolution_y`, `SPU` and `threshold`. Moreover, you can define `error_count` to stop execution of autotests if `error_count` cases in row are error.
3. Set timeout for simpleRender in seconds (1800 in `Smoke`).

## Adding test cases

For adding autotests you should create `test_cases.json`. You can see examples on any group or below.

    {
        "case": "MAYA_SM_150",
        "status": "active",
        "functions": [
            "cmds.setAttr('RadeonProRenderGlobals.denoiserEnabled', 1)",
            "rpr_render(case)",
            "cmds.setAttr('RadeonProRenderGlobals.denoiserEnabled', 0)"
        ],
        "script_info": [
            "Denoiser",
            "Yes"
        ],
        "scene": "normal_scene.ma",
        "skip_on": [
            ["AMD Radeon (TM) Pro WX 7100 Graphics"],
            ["Darwin 10.14.6(64bit)"],
            ["AMD Radeon VII", "Windows 10(64bit)"]
        ]
    }
* Status should be `skipped` or `active`
* Function should contain `rpr_render(case)` for render or `check_test_cases_success_save` for save without rendering.
* Skip_on field contains list of lists with parameters of system. It can contain one or two strings with gpu name and os name. In example below case will be skipped on 7100 gpu, on osx and on Radeon VII on windows.