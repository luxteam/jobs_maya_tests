# Autotests for Radeon ProRender plugin for Autodesk Maya

## Install
 1. Clone this repo
 2. Get `jobs_launcher` as git submodule, using next commands

    ```
    git submodule init
    git submodule update
    ```

 3. Run `scripts/auto_config.bat`. This script will create `scripts/Devices.config.json` for your hardware configuration.
 4. Check that `MayaAssets` scenes placed in `C:/TestResources`.
 
    ***You should use the specific scenes which defined in `test-cases.json` files in `jobs/Tests/` folders.***


 5. Run `run.bat` for `scripts` folder with customised arguments with space separator:

    * First arg sets `RENDER_DEVICE` from `Devices.config.json`.
    * Second arg sets `FILE_FILTER`.
    * Third arg sets `TEST_FILTER`.
    * Fourth arg sets `RX`. Default is `0`.
    * Fifth arg sets `RY`. Default is `0`.
    * Sixth arg sets `SPU`. Default is `25`.
    * Seventh arg sets `ITER`. Default is `50`.
    * Eighth arg sets `THRESHOLD`. Default is `0.05`.
    * Ninth arg sets `TOOL`. Default is `2020`.
    * Tenth arg sets `ENGINE`. Default is `Tahoe`.
    * Eleventh arg sets `RETRIES`. Default is `2`.
    * Twelfth arg sets `UPDATE_REFS`. Default is `No`.

    Example:
    > run.bat cpu "regression.json~" "" 0 0 25 50 0.05 2020 Tahoe 2 No 1

    ***ATTENTION!***

    **The order of the arguments is important. You cannot skip arguments.**

    **Better to run via `CMD`. If you run through `PS`, empty arguments (like this "") will be ignored.**

## How to update weights.json
 1. Move to jobs_launcher
 2. Init jobs_launcher submodule by commnad: git submodule update --init
 3. Move to common/scripts/manual
 4. Download from Weekly report session_report.json (Add Tahoe/summary_report.json or Northstar/summary_report.json to url with report)
 5. Run generation of new weights.json: python3 analyze_summary_report.py --path <path_to_summary_report.json> --results_path <where_to_save_weight.json>
 6. Move new weight.json to jobs_test_maya/jobs/