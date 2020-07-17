import maya.mel as mel
import maya.cmds as cmds
import datetime
import time
import json
import re
import os.path as path
import os
from shutil import copyfile
import fireRender.rpr_material_browser

WORK_DIR = '{work_dir}'
TEST_TYPE = '{testType}'
RENDER_DEVICE = '{render_device}'
RES_PATH = '{res_path}'
PASS_LIMIT = {pass_limit}
RESOLUTION_X = {resolution_x}
RESOLUTION_Y = {resolution_y}
SPU = {SPU}
THRESHOLD = {threshold}
ENGINE = {engine}
LOGS_DIR = path.join(WORK_DIR, 'render_tool_logs')


def event(name, start, case):
    with open(path.join('events', str(glob.glob('events/*.json').__len__() + 1) + '.json'), 'w') as f:
        f.write(json.dumps({{'name': name, 'time': datetime.datetime.now().strftime(
            '%d/%m/%Y %H:%M:%S.%f'), 'start': start, 'case': case}}, indent=4))


def logging(message):
    print(' >>> [RPR TEST] [' +
          datetime.datetime.now().strftime('%H:%M:%S') + '] ' + message)


def reportToJSON(case, render_time=0):
    path_to_file = path.join(WORK_DIR, case['case'] + '_RPR.json')

    with open(path_to_file, 'r') as file:
        report = json.loads(file.read())[0]

    if case['status'] == 'inprogress':
        report['test_status'] = 'passed'
    else:
        report['test_status'] = case['status']

    logging('Create report json ({{}} {{}})'.format(
            case['case'], report['test_status']))

    report['file_name'] = case['case'] + case.get('extension', '.jpg')
    # TODO: render device may be incorrect (if it changes in case)
    report['render_device'] = cmds.optionVar(q='RPR_DevicesName')[0]
    report['tool'] = mel.eval('about -iv')
    report['date_time'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    report['render_version'] = mel.eval('getRPRPluginVersion()')
    report['core_version'] = mel.eval('getRprCoreVersion()')
    report['render_color_path'] = path.join('Color', report['file_name'])
    report['render_time'] = render_time
    report['test_group'] = TEST_TYPE
    report['test_case'] = case['case']
    report['difference_color'] = 0
    report['script_info'] = case['script_info']
    report['render_log'] = path.join('render_tool_logs', case['case'] + '.log')
    report['scene_name'] = case.get('scene', '')

    with open(path_to_file, 'w') as file:
        file.write(json.dumps([report], indent=4))


def render_tool_log_path(name):
    return path.join(LOGS_DIR, name + '.log')


def validateFiles():
    logging('Repath scene')
    # TODO: repath from folder with group
    unresolved_files = cmds.filePathEditor(
        query=True, listFiles='', unresolved=True, attributeOnly=True)
    if unresolved_files:
        for item in unresolved_files:
            cmds.filePathEditor(item, repath=RES_PATH, recursive=True, ra=1)


def enable_rpr(case):
    if not cmds.pluginInfo('RadeonProRender', query=True, loaded=True):
        event('Load rpr', True, case)
        cmds.loadPlugin('RadeonProRender', quiet=True)
        event('Load rpr', False, case)
        logging('Load rpr')


def rpr_render(case):
    event('Prerender', False, case['case'])
    logging('Render image')

    mel.eval('fireRender -waitForItTwo')
    start_time = time.time()
    mel.eval('renderIntoNewWindow render')
    cmds.sysFile(path.join(WORK_DIR, 'Color'), makeDir=True)
    test_case_path = path.join(WORK_DIR, 'Color', case['case'])
    cmds.renderWindowEditor('renderView', edit=1,  dst='color')
    cmds.renderWindowEditor('renderView', edit=1, com=1,
                            writeImage=test_case_path)
    test_time = time.time() - start_time

    event('Postrender', True, case['case'])
    reportToJSON(case, test_time)


def prerender(case):
    logging('Prerender')
    scene = case.get('scene', '')
    scene_name = cmds.file(q=True, sn=True, shn=True)
    if scene_name != scene:
        try:
            event('Open scene', True, case['case'])
            cmds.file(scene, f=True, op='v=0;', prompt=False, iv=True, o=True)
            event('Open scene', False, case['case'])
            validateFiles()
            enable_rpr(case['case'])
        except Exception as e:
            logging(
                "Can't prepare for render scene because of {{}}".format(str(e)))

    event('Prerender', True, case['case'])

    cmds.setAttr('RadeonProRenderGlobals.detailedLog', True)
    mel.eval('athenaEnable -ae false')

    cmds.setAttr('RadeonProRenderGlobals.tahoeVersion', ENGINE)

    cmds.optionVar(rm='RPR_DevicesSelected')
    cmds.optionVar(iva=('RPR_DevicesSelected',
                        (RENDER_DEVICE in ['gpu', 'dual'])))
    cmds.optionVar(iva=('RPR_DevicesSelected',
                        (RENDER_DEVICE in ['cpu', 'dual'])))

    if RESOLUTION_X and RESOLUTION_Y:
        cmds.setAttr('defaultResolution.width', RESOLUTION_X)
        cmds.setAttr('defaultResolution.height', RESOLUTION_Y)

    cmds.setAttr('defaultRenderGlobals.currentRenderer',
                 type='string' 'FireRender')

    cmds.setAttr('defaultRenderGlobals.imageFormat', 8)

    cmds.setAttr('RadeonProRenderGlobals.adaptiveThreshold', THRESHOLD)
    cmds.setAttr(
        'RadeonProRenderGlobals.completionCriteriaIterations', PASS_LIMIT)
    cmds.setAttr('RadeonProRenderGlobals.samplesPerUpdate', SPU)
    cmds.setAttr('RadeonProRenderGlobals.completionCriteriaSeconds', 0)

    for function in case['functions']:
        try:
            if re.match('((^\S+|^\S+ \S+) = |^print|^if|^for|^with)', function):
                exec(function)
            else:
                eval(function)
        except Exception as e:
            logging('Error "{{}}" with string "{{}}"'.format(e, function))
    event('Postrender', False, case['case'])


def save_report(case):
    logging('Save report without rendering for ' + case['case'])

    if not os.path.exists(os.path.join(WORK_DIR, 'Color')):
        os.makedirs(os.path.join(WORK_DIR, 'Color'))

    work_dir = path.join(WORK_DIR, 'Color', case['case'] + '.jpg')
    source_dir = path.join(WORK_DIR, '..', '..', '..',
                           '..', 'jobs_launcher', 'common', 'img')

    if case['status'] == 'inprogress':
        copyfile(path.join(source_dir, 'passed.jpg'), work_dir)
    else:
        copyfile(
            path.join(source_dir, case['status'] + '.jpg'), work_dir)

    enable_rpr(case['case'])

    reportToJSON(case)


def case_function(case):
    functions = {{
        'prerender': prerender,
        'save_report': save_report
    }}

    func = 'prerender'

    if case['functions'][0] == 'check_test_cases_success_save':
        func = 'save_report'
    else:
        try:
            projPath = os.path.join(RES_PATH, TEST_TYPE)
            temp = os.path.join(projPath, case['scene'][:-3])
            if os.path.isdir(temp):
                projPath = temp
            mel.eval('setProject("{{}}")'.format(projPath.replace('\\', '/')))
        except:
            logging("Can't set project in '" + projPath + "'")

    # 2- retries count
    if case['status'] == 'fail' or case.get('number_of_tries', 1) == 2:
        case['status'] = 'error'
        func = 'save_report'
    elif case['status'] == 'skipped':
        func = 'save_report'
    else:
        case['number_of_tries'] = case.get('number_of_tries', 0) + 1

    functions[func](case)


# place for extension functions


def main():
    if not os.path.exists(os.path.join(WORK_DIR, LOGS_DIR)):
        os.makedirs(os.path.join(WORK_DIR, LOGS_DIR))

    with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
        cases = json.load(json_file)

    event('Open tool', False, next(
        case['case'] for case in cases if case['status'] in ['active', 'fail', 'skipped']))

    for case in cases:
        if case['status'] in ['active', 'fail', 'skipped']:
            if case['status'] == 'active':
                case['status'] = 'inprogress'

            with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
                json.dump(cases, file, indent=4)

            log_path = render_tool_log_path(case['case'])
            if not path.exists(log_path):
                with open(log_path, 'w'):
                    logging('Create log file for ' + case['case'])
            cmds.scriptEditorInfo(historyFilename=log_path, writeHistory=True)

            logging(case['case'] + ' in progress')

            start_time = datetime.datetime.now()
            case_function(case)
            case_time = (datetime.datetime.now() - start_time).total_seconds()
            case['time_taken'] = case_time

            if case['status'] == 'inprogress':
                case['status'] = 'done'
                logging(case['case'] + ' done')

            with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
                json.dump(cases, file, indent=4)

    event('Close tool', True, cases[-1]['case'])

    # Athena need additional time for work before close maya
    if TEST_TYPE not in ['Athena']:
        cmds.quit(abort=True)
    else:
        cmds.evalDeferred('cmds.quit(abort=True)')


main()
