import argparse
import os
import subprocess
import psutil
import json
import ctypes
import pyscreenshot
import platform
import re
from datetime import datetime
from shutil import copyfile, move, which
import sys
import time
from utils import is_case_skipped

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))

import jobs_launcher.core.performance_counter as perf_count
import jobs_launcher.core.config as core_config
from jobs_launcher.core.system_info import get_gpu
from jobs_launcher.core.kill_process import kill_process



ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir))
PROCESS = ['Maya', 'maya.exe']

if platform.system() == 'Darwin':
    from Quartz import CGWindowListCopyWindowInfo
    from Quartz import kCGWindowListOptionOnScreenOnly
    from Quartz import kCGNullWindowID
    from Quartz import kCGWindowName
    from Quartz import CGWindowListCreateImage
    from Quartz import CGRectMake
    from Quartz import kCGWindowImageDefault


def get_windows_titles():
    try:
        if platform.system() == 'Darwin':
            # for receive kCGWindowName values from CGWindowListCopyWindowInfo function it's necessary to call any function of Screen Record API
            CGWindowListCreateImage(
                CGRectMake(0, 0, 1, 1),
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID,
                kCGWindowImageDefault
            )
            ws_options = kCGWindowListOptionOnScreenOnly
            windows_list = CGWindowListCopyWindowInfo(
                ws_options, kCGNullWindowID)
            maya_titles = {x.get('kCGWindowName', u'Unknown')
                           for x in windows_list if 'Maya' in x['kCGWindowOwnerName']}

            # duct tape for windows with empty title
            expected = {'Maya', 'Render View', 'Rendering...'}
            if maya_titles - expected:
                maya_titles.add('Detected windows ERROR')

            return list(maya_titles)

        elif platform.system() == 'Windows':
            EnumWindows = ctypes.windll.user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(
                ctypes.c_int), ctypes.POINTER(ctypes.c_int))
            GetWindowText = ctypes.windll.user32.GetWindowTextW
            GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
            IsWindowVisible = ctypes.windll.user32.IsWindowVisible

            titles = []

            def foreach_window(hwnd, lParam):
                if IsWindowVisible(hwnd):
                    length = GetWindowTextLength(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    GetWindowText(hwnd, buff, length + 1)
                    titles.append(buff.value)
                return True

            EnumWindows(EnumWindowsProc(foreach_window), 0)

            return titles
    except Exception as err:
        core_config.main_logger.error(
            'Exception has occurred while pull windows titles: {}'.format(str(err)))

    return []


def createArgsParser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--tool', required=True, metavar='<path>')
    parser.add_argument('--render_device', required=True)
    parser.add_argument('--output', required=True, metavar='<dir>')
    parser.add_argument('--testType', required=True)
    parser.add_argument('--res_path', required=True)
    parser.add_argument('--pass_limit', required=False, default=50, type=int)
    parser.add_argument('--resolution_x', required=False, default=0, type=int)
    parser.add_argument('--resolution_y', required=False, default=0, type=int)
    parser.add_argument('--testCases', required=True)
    parser.add_argument('--engine', required=False, default='1')
    parser.add_argument('--SPU', required=False, default=25, type=int)
    parser.add_argument('--error_count', required=False, default=0, type=int)
    parser.add_argument('--threshold', required=False,
                        default=0.05, type=float)
    parser.add_argument('--retries', required=False, default=2, type=int)
    parser.add_argument('--update_refs', required=True)

    return parser


def check_licenses(res_path, maya_scenes, testType):
    try:
        for scene in maya_scenes:
            scenePath = os.path.join(res_path, testType)
            try:
                temp = os.path.join(scenePath, scene[:-3])
                if os.path.isdir(temp):
                    scenePath = temp
            except:
                pass
            scenePath = os.path.join(scenePath, scene)

            with open(scenePath) as f:
                scene_file = f.read()

            license = 'fileInfo "license" "student";'
            scene_file = scene_file.replace(license, '')

            with open(scenePath, 'w') as f:
                f.write(scene_file)
    except Exception as ex:
        core_config.main_logger.error(
            'Error while deleting student license: {}'.format(ex))


def kill_maya(process):
    core_config.main_logger.warning('Killing maya....')
    child_processes = process.children()
    core_config.main_logger.warning(
        'Child processes: {}'.format(child_processes))
    for ch in child_processes:
        try:
            ch.terminate()
            time.sleep(10)
            ch.kill()
            time.sleep(10)
            status = ch.status()
            core_config.main_logger.error(
                'Process is alive: {}. Name: {}. Status: {}'.format(ch, ch.name(), status))
        except psutil.NoSuchProcess:
            core_config.main_logger.warning(
                'Process is killed: {}'.format(ch))

    try:
        process.terminate()
        time.sleep(10)
        process.kill()
        time.sleep(10)
        status = process.status()
        core_config.main_logger.error(
            'Process is alive: {}. Name: {}. Status: {}'.format(ch, ch.name(), status))
    except psutil.NoSuchProcess:
        core_config.main_logger.warning(
            'Process is killed: {}'.format(ch))


def get_finished_cases_number(output):
    for i in range(3):
        try:
            with open(os.path.join(os.path.abspath(output), 'test_cases.json')) as file:
                test_cases = json.load(file)
                return len([case['status'] for case in test_cases if case['status'] in ('skipped', 'error', 'done')])
        except Exception as e:
            core_config.main_logger.error('Failed to get number of finished cases (try #{}): Reason: {}'.format(i, str(e)))
            time.sleep(5)
    return -1


def launchMaya(cmdScriptPath, work_dir, error_windows):
    system_pl = platform.system()
    core_config.main_logger.info(
        'Launch script on Maya ({})'.format(cmdScriptPath))
    os.chdir(work_dir)
    perf_count.event_record(args.output, 'Open tool', True)
    p = psutil.Popen(cmdScriptPath, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, shell=True)

    prev_done_test_cases = get_finished_cases_number(args.output)
    # timeout after which Maya is considered hung
    restart_timeout = 440
    current_restart_timeout = restart_timeout


    while True:
        try:
            p.communicate(timeout=40)
            window_titles = get_windows_titles()
            core_config.main_logger.info(
                'Found windows: {}'.format(window_titles))
        except (psutil.TimeoutExpired, subprocess.TimeoutExpired) as err:
            current_restart_timeout -= 40
            fatal_errors_titles = ['Detected windows ERROR', 'maya', 'Student Version File', 'Radeon ProRender Error', 'Script Editor',
                                   'Autodesk Maya 2018 Error Report', 'Autodesk Maya 2018 Error Report', 'Autodesk Maya 2018 Error Report',
                                   'Autodesk Maya 2019 Error Report', 'Autodesk Maya 2019 Error Report', 'Autodesk Maya 2019 Error Report',
                                   'Autodesk Maya 2020 Error Report', 'Autodesk Maya 2020 Error Report', 'Autodesk Maya 2020 Error Report']
            window_titles = get_windows_titles()
            error_window = set(fatal_errors_titles).intersection(window_titles)
            if error_window:
                core_config.main_logger.error(
                    'Error window found: {}'.format(error_window))
                core_config.main_logger.warning(
                    'Found windows: {}'.format(window_titles))
                error_windows.update(error_window)
                rc = -1

                if system_pl == 'Windows':
                    try:
                        error_screen = pyscreenshot.grab()
                        error_screen.save(os.path.join(
                            args.output, 'error_screenshot.jpg'))
                    except Exception as ex:
                        pass

                kill_maya(p)

                break
            else:
                new_done_test_cases_num = get_finished_cases_number(args.output)
                if current_restart_timeout <= 0:
                    if new_done_test_cases_num == -1:
                        core_config.main_logger.error('Failed to get number of finished cases. Try to do that on next iteration')
                    elif prev_done_test_cases == new_done_test_cases_num:
                        # if number of finished cases wasn't increased - Maya got stuck
                        core_config.main_logger.error('Maya got stuck.')
                        rc = -1
                        current_restart_timeout = restart_timeout
                        kill_maya(p)
                        break
                    else:
                        prev_done_test_cases = new_done_test_cases_num
                        current_restart_timeout = restart_timeout
        else:
            rc = 0
            break

    perf_count.event_record(args.output, 'Close tool', False)

    if args.testType in ['Athena']:
        subprocess.call([sys.executable, os.path.realpath(os.path.join(
            os.path.dirname(__file__), 'extensions', args.testType + '.py')), args.output])
    return rc


def main(args, error_windows):
    perf_count.event_record(args.output, 'Prepare tests', True)
    if args.testType in ['Support_2019', 'Support_2018']:
        args.tool = re.sub('[0-9]{4}', args.testType[-4:], args.tool)

    core_config.main_logger.info('Make "base_functions.py"')

    try:
        cases = json.load(open(os.path.realpath(
            os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'test_cases.json'))))
    except Exception as e:
        core_config.logging.error("Can't load test_cases.json")
        core_config.main_logger.error(str(e))
        group_failed(args, error_windows)
        exit(-1)

    try:
        with open(os.path.join(os.path.dirname(__file__), 'base_functions.py')) as f:
            script = f.read()
    except OSError as e:
        core_config.main_logger.error(str(e))
        return 1

    if os.path.exists(os.path.join(os.path.dirname(__file__), 'extensions', args.testType + '.py')):
        with open(os.path.join(os.path.dirname(__file__), 'extensions', args.testType + '.py')) as f:
            extension_script = f.read()
        script = script.split('# place for extension functions')
        script = script[0] + extension_script + script[1]

    work_dir = os.path.abspath(args.output).replace('\\', '/')
    res_path = os.path.abspath(args.res_path).replace('\\', '/')

    maya_scenes = {x.get('scene', '') for x in cases if x.get('scene', '')}
    check_licenses(args.res_path, maya_scenes, args.testType)

    script = script.format(work_dir=work_dir, testType=args.testType, render_device=args.render_device, res_path=res_path, pass_limit=args.pass_limit,
                           resolution_x=args.resolution_x, resolution_y=args.resolution_y, SPU=args.SPU, threshold=args.threshold, engine=args.engine,
                           retries=args.retries)

    with open(os.path.join(args.output, 'base_functions.py'), 'w') as file:
        file.write(script)

    if os.path.exists(args.testCases) and args.testCases:
        with open(args.testCases) as f:
            test_cases = json.load(f)['groups'][args.testType]
            if test_cases:
                necessary_cases = [
                    item for item in cases if item['case'] in test_cases]
                cases = necessary_cases

    core_config.main_logger.info('Create empty report files')

    if not os.path.exists(os.path.join(work_dir, 'Color')):
        os.makedirs(os.path.join(work_dir, 'Color'))
    copyfile(os.path.abspath(os.path.join(work_dir, '..', '..', '..', '..', 'jobs_launcher',
                                          'common', 'img', 'error.jpg')), os.path.join(work_dir, 'Color', 'failed.jpg'))

    gpu = get_gpu()
    if not gpu:
        core_config.main_logger.error("Can't get gpu name")
    render_platform = {platform.system(), gpu}
    system_pl = platform.system()

    baseline_dir = 'rpr_maya_autotests_baselines'
    if args.engine == 'Northstar':
        baseline_dir = baseline_dir + '-NorthStar'
    elif args.engine == 'Hybrid_Low':
        baseline_dir = baseline_dir + '-HybridLow'
    elif args.engine == 'Hybrid_Medium':
        baseline_dir = baseline_dir + '-HybridMedium'
    elif args.engine == 'Hybrid_High':
        baseline_dir = baseline_dir + '-HybridHigh'

    if system_pl == "Windows":
        baseline_path_tr = os.path.join(
            'c:/TestResources', baseline_dir, args.testType)
    else:
        baseline_path_tr = os.path.expandvars(os.path.join(
            '$CIS_TOOLS/../TestResources', baseline_dir, args.testType))

    baseline_path = os.path.join(
        work_dir, os.path.pardir, os.path.pardir, os.path.pardir, 'Baseline', args.testType)

    if not os.path.exists(baseline_path):
        os.makedirs(baseline_path)
        os.makedirs(os.path.join(baseline_path, 'Color'))

    for case in cases:
        if is_case_skipped(case, render_platform, args.engine):
            case['status'] = 'skipped'

        if case['status'] != 'done':
            if case['status'] == 'inprogress':
                case['status'] = 'active'
                case['number_of_tries'] = case.get('number_of_tries', 0) + 1

            template = core_config.RENDER_REPORT_BASE.copy()
            template['test_case'] = case['case']
            template['render_device'] = get_gpu()
            template['script_info'] = case['script_info']
            template['scene_name'] = case.get('scene', '')
            template['test_group'] = args.testType
            template['date_time'] = datetime.now().strftime(
                '%m/%d/%Y %H:%M:%S')
            if case['status'] == 'skipped':
                template['test_status'] = 'skipped'
                template['file_name'] = case['case'] + case.get('extension', '.jpg')
                template['render_color_path'] = os.path.join('Color', template['file_name'])
                template['group_timeout_exceeded'] = False

                try:
                    skipped_case_image_path = os.path.join(args.output, 'Color', template['file_name'])
                    if not os.path.exists(skipped_case_image_path):
                        copyfile(os.path.join(work_dir, '..', '..', '..', '..', 'jobs_launcher', 
                            'common', 'img', "skipped.png"), skipped_case_image_path)
                except OSError or FileNotFoundError as err:
                    main_logger.error("Can't create img stub: {}".format(str(err)))
            else:
                template['test_status'] = 'error'
                template['file_name'] = 'failed.jpg'
                template['render_color_path'] = os.path.join('Color', 'failed.jpg')

            with open(os.path.join(work_dir, case['case'] + core_config.CASE_REPORT_SUFFIX), 'w') as f:
                f.write(json.dumps([template], indent=4))

        if 'Update' not in args.update_refs:
            try:
                copyfile(os.path.join(baseline_path_tr, case['case'] + core_config.CASE_REPORT_SUFFIX),
                         os.path.join(baseline_path, case['case'] + core_config.CASE_REPORT_SUFFIX))

                with open(os.path.join(baseline_path, case['case'] + core_config.CASE_REPORT_SUFFIX)) as baseline:
                    baseline_json = json.load(baseline)

                for thumb in [''] + core_config.THUMBNAIL_PREFIXES:
                    if thumb + 'render_color_path' and os.path.exists(os.path.join(baseline_path_tr, baseline_json[thumb + 'render_color_path'])):
                        copyfile(os.path.join(baseline_path_tr, baseline_json[thumb + 'render_color_path']),
                                 os.path.join(baseline_path, baseline_json[thumb + 'render_color_path']))
            except:
                core_config.main_logger.error('Failed to copy baseline ' +
                                              os.path.join(baseline_path_tr, case['case'] + core_config.CASE_REPORT_SUFFIX))

    with open(os.path.join(work_dir, 'test_cases.json'), 'w+') as f:
        json.dump(cases, f, indent=4)

    if system_pl == 'Windows':
        cmdRun = '''
		  set MAYA_CMD_FILE_OUTPUT=%cd%/renderTool.log
		  set PYTHONPATH=%cd%;PYTHONPATH
		  set MAYA_SCRIPT_PATH=%cd%;%MAYA_SCRIPT_PATH%
		  "{tool}" -command "python(\\"import base_functions\\");"
		'''.format(tool=args.tool)

        cmdScriptPath = os.path.join(args.output, 'script.bat')
        with open(cmdScriptPath, 'w') as file:
            file.write(cmdRun)

    elif system_pl == 'Darwin':
        cmdRun = '''
		  export MAYA_CMD_FILE_OUTPUT=$PWD/renderTool.log
		  export PYTHONPATH=$PWD:$PYTHONPATH
		  export MAYA_SCRIPT_PATH=$PWD:$MAYA_SCRIPT_PATH
		  "{tool}" -command "python(\\"import base_functions\\");"
		'''.format(tool=args.tool)

        cmdScriptPath = os.path.join(args.output, 'script.sh')
        with open(cmdScriptPath, 'w') as file:
            file.write(cmdRun)
        os.system('chmod +x {}'.format(cmdScriptPath))

    if which(args.tool) is None:
        core_config.main_logger.error('Can\'t find tool ' + args.tool)
        exit(-1)

    perf_count.event_record(args.output, 'Prepare tests', False)

    rc = launchMaya(cmdScriptPath, args.output, error_windows)

    if args.testType in ['Athena']:
        subprocess.call([sys.executable, os.path.realpath(os.path.join(
            os.path.dirname(__file__), 'extensions', args.testType + '.py')), args.output])
    core_config.main_logger.info('Main func return : {}'.format(rc))
    return rc


def group_failed(args, error_windows):
    core_config.main_logger.error('Group failed')
    status = 'skipped'
    try:
        cases = json.load(open(os.path.realpath(
            os.path.join(os.path.abspath(args.output), 'test_cases.json'))))
    except Exception as e:
        core_config.logging.error("Can't load test_cases.json")
        core_config.main_logger.error(str(e))
        cases = json.load(open(os.path.realpath(os.path.join(os.path.dirname(
            __file__), '..', 'Tests', args.testType, 'test_cases.json'))))
        status = 'inprogress'

    for case in cases:
        if case['status'] == 'active':
            case['status'] = status

    with open(os.path.join(os.path.abspath(args.output), 'test_cases.json'), "w+") as f:
        json.dump(cases, f, indent=4)

    rc = main(args, error_windows)
    kill_process(PROCESS)
    core_config.main_logger.info(
        "Finish simpleRender with code: {}".format(rc))
    exit(rc)

def sync_time(work_dir):
    for rpr_json_path in os.listdir(work_dir):
        if rpr_json_path.endswith('_RPR.json'):
            try:
                with open(os.path.join(work_dir, rpr_json_path)) as rpr_json_file:
                    rpr_json = json.load(rpr_json_file)

                with open(os.path.join(work_dir, rpr_json[0]['render_log'])) as logs_file:
                    logs = logs_file.read()

                sync_minutes = re.findall(
                    'RPR scene synchronization time: (\d*)m', logs)
                sync_seconds = re.findall(
                    'RPR scene synchronization time: .*?(\d*)s', logs)
                sync_milisec = re.findall(
                    'RPR scene synchronization time: .*?(\d*)ms', logs)

                sync_minutes = float(next(iter(sync_minutes or []), 0))
                sync_seconds = float(next(iter(sync_seconds or []), 0))
                sync_milisec = float(next(iter(sync_milisec or []), 0))

                synchronization_time = sync_minutes * 60 + sync_seconds + sync_milisec / 1000
                rpr_json[0]['sync_time'] = synchronization_time
                rpr_json[0]['render_time'] -= synchronization_time

                with open(os.path.join(work_dir, rpr_json_path), 'w') as rpr_json_file:
                    rpr_json_file.write(json.dumps(rpr_json, indent=4))
            except:
                core_config.main_logger.error("Can't count sync time for " + rpr_json_path)


if __name__ == '__main__':
    core_config.main_logger.info('simpleRender start working...')

    args = createArgsParser().parse_args()

    try:
        os.makedirs(args.output)
    except OSError as e:
        pass

    iteration = 0

    try:
        copyfile(os.path.realpath(os.path.join(os.path.dirname(
            __file__), '..', 'Tests', args.testType, 'test_cases.json')),
            os.path.realpath(os.path.join(os.path.abspath(
                args.output).replace('\\', '/'), 'test_cases.json')))
    except:
        core_config.logging.error("Can't copy test_cases.json")
        core_config.main_logger.error(str(e))
        exit(-1)

    error_windows = set()

    while True:
        iteration += 1

        core_config.main_logger.info(
            'Try to run script in maya (#' + str(iteration) + ')')

        rc = main(args, error_windows)

        try:
            move(os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'renderTool.log'),
                 os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'renderTool' + str(iteration) + '.log'))
        except:
            core_config.main_logger.error('No renderTool.log')

        try:
            cases = json.load(open(os.path.realpath(
                os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'test_cases.json'))))
        except Exception as e:
            core_config.logging.error("Can't load test_cases.json")
            core_config.main_logger.error(str(e))
            exit(-1)

        active_cases = 0
        current_error_count = 0

        for case in cases:
            if case['status'] in ['fail', 'error', 'inprogress']:
                current_error_count += 1
                if args.error_count == current_error_count:
                    group_failed(args, error_windows)
            else:
                current_error_count = 0

            if case['status'] in ['active', 'fail', 'inprogress']:
                active_cases += 1

        if active_cases == 0 or iteration > len(cases) * args.retries:
            for case in cases:
                error_message = ''
                number_of_tries = case.get('number_of_tries', 0)
                if case['status'] in ['fail', 'error']:
                    error_message = "Testcase wasn't executed successfully (all attempts were used). Number of tries: {}".format(str(number_of_tries))
                elif case['status'] in ['active', 'inprogress']:
                    if number_of_tries:
                        error_message = "Testcase wasn't finished. Number of tries: {}".format(str(number_of_tries))
                    else:
                        error_message = "Testcase wasn't run"

                if error_message:
                    core_config.main_logger.info("Testcase {} wasn't finished successfully: {}".format(case['case'], error_message))
                    path_to_file = os.path.join(args.output, case['case'] + '_RPR.json')

                    with open(path_to_file, 'r') as file:
                        report = json.load(file)

                    report[0]['group_timeout_exceeded'] = False
                    report[0]['message'].append(error_message)
                    if len(error_windows) != 0:
                        report[0]['message'].append("Error windows {}".format(error_windows))

                    with open(path_to_file, 'w') as file:
                        json.dump(report, file, indent=4)

            # exit script if base_functions don't change number of active cases
            kill_process(PROCESS)
            core_config.main_logger.info(
                'Finish simpleRender with code: {}'.format(rc))
            sync_time(args.output)
            exit(rc)
