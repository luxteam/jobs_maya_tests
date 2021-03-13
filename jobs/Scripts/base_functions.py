import maya.mel as mel
import maya.cmds as cmds
import glob
import datetime
import time
import json
import re
import os.path as path
import os
from event_recorder import event
from shutil import copyfile, move
from collections import deque
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
ENGINE = '{engine}'
RETRIES = {retries}
BATCH_RENDER = {batch_render}
LOGS_DIR = path.join(WORK_DIR, 'render_tool_logs')
RENDER_TOOL_LOG = path.join(WORK_DIR, 'renderTool.log')

def logging(message, case=None):
    message = ' >>> [RPR TEST] [' + datetime.datetime.now().strftime('%H:%M:%S') + '] ' + message + '\n'
    print(message)
    if BATCH_RENDER and case is not None:
        with open(RENDER_TOOL_LOG, 'a') as f:
            f.write(message)
    

def reportToJSON(case, render_time=0):
    path_to_file = path.join(WORK_DIR, case['case'] + '_RPR.json')

    with open(path_to_file, 'r') as file:
        report = json.loads(file.read())[0]

    # status for Athena suite will be set later
    if TEST_TYPE not in ['Athena']:
        if case['status'] == 'inprogress':
            if BATCH_RENDER:
                case['status'] = 'done'
            report['test_status'] = 'passed'
            report['group_timeout_exceeded'] = False
        else:
            report['test_status'] = case['status']

    logging('Create report json ({{}} {{}})'.format(
            case['case'], report['test_status']), case['case'])

    number_of_tries = case.get('number_of_tries', 0)
    if case['status'] == 'error':
        # remove old message
        for message in report['message']:
            if 'Testcase wasn\'t executed successfully' in message:
                report['message'].remove(message)
        if number_of_tries == RETRIES:
            error_message = 'Testcase wasn\'t executed successfully (all attempts were used)'
        else:
            error_message = 'Testcase wasn\'t executed successfully'
        report['message'].append(error_message)
        report['group_timeout_exceeded'] = False
    else:
        report['message'] = []

    report['date_time'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    report['render_time'] = render_time
    report['test_group'] = TEST_TYPE
    report['test_case'] = case['case']
    report['case_functions'] = case['functions']
    report['difference_color'] = 0
    report['script_info'] = case['script_info']
    report['render_log'] = path.join('render_tool_logs', case['case'] + '.log')
    report['scene_name'] = case.get('scene', '')
    report['number_of_tries'] = number_of_tries
    if case['status'] != 'skipped':
        report['file_name'] = case['case'] + case.get('extension', '.jpg')
        report['render_color_path'] = path.join('Color', report['file_name'])

    # save metrics which can be received witout call of functions of Maya
    with open(path_to_file, 'w') as file:
        file.write(json.dumps([report], indent=4))

    try:
        report['tool'] = mel.eval('about -iv')
    except Exception as e:
        logging('Failed to get Maya version. Reason: {{}}'.format(str(e)), case['case'])
    try:
        report['render_version'] = mel.eval('getRPRPluginVersion()')
    except Exception as e:
        logging('Failed to get render version. Reason: {{}}'.format(str(e)), case['case'])
    try:
        report['core_version'] = mel.eval('getRprCoreVersion()')
    except Exception as e:
        logging('Failed to get core version. Reason: {{}}'.format(str(e)), case['case'])

    # save metrics which can't be received witout call of functions of Maya (additional measures to avoid stucking of Maya)
    with open(path_to_file, 'w') as file:
        file.write(json.dumps([report], indent=4))


def render_tool_log_path(name):
    return path.join(LOGS_DIR, name + '.log')


def get_scene_path(case):
    scenePath = os.path.join(RES_PATH, 'Scenes')
    temp = os.path.join(scenePath, case['scene'][:-3])
    if os.path.isdir(temp):
        scenePath = temp
    return scenePath


def extract_img_from(folder, case):
    src_dir = path.join(WORK_DIR, 'Color', folder)
    img_name = cmds.renderSettings(firstImageName=True)[0]
        
    if os.path.exists(src_dir) and os.path.isdir(src_dir):
        try:
            move(path.join(src_dir, img_name), path.join(WORK_DIR, 'Color'))
            logging('Extract {{}} from {{}} folder'.format(img_name, folder), case['case'])
        except Exception as ex:
            logging('Error while extracting {{}} from {{}}: {{}}'.format(img_name, folder, ex), case['case'])
    else:
        logging("{{}} doesn't exist or isn't a folder".format(folder), case['case'])


def validateFiles(case):
    logging('Repath scene', case['case'])
    cmds.filePathEditor(refresh=True)
    unresolved_files = cmds.filePathEditor(query=True, listFiles='', unresolved=True, attributeOnly=True)
    source_path = os.path.join(RES_PATH, 'Sources')
    logging("Unresolved items: {{}}".format(str(unresolved_files)), case['case'])
    logging('Start repath scene', case['case'])
    logging("Source (target) path: {{}}".format(source_path), case['case'])
    if unresolved_files:
        for item in unresolved_files:
            cmds.filePathEditor(item, repath=source_path, recursive=True, ra=1)
    unresolved_files = cmds.filePathEditor(query=True, listFiles='', unresolved=True, attributeOnly=True)
    logging("Unresolved items: {{}}".format(str(unresolved_files)), case['case'])
    logging('Repath finished', case['case'])


def apply_case_functions(case, start_index, end_index):
    for function in case['functions'][start_index:end_index]:
        try:
            if re.match('((^\S+|^\S+ \S+) = |^print|^if|^for|^with)', function):
                exec(function)
            else:
                eval(function)
        except Exception as e:
            logging('Error "{{}}" with string "{{}}"'.format(e, function), case['case'])


def enable_rpr(case):
    if not cmds.pluginInfo('RadeonProRender', query=True, loaded=True):
        event('Load rpr', True, case)
        cmds.loadPlugin('RadeonProRender', quiet=True)
        event('Load rpr', False, case)
        logging('Load rpr', case)


def rpr_render(case, mode='color'):
    event('Prerender', False, case['case'])
    validateFiles(case)
    logging('Render image', case['case'])

    if not BATCH_RENDER:
        mel.eval('fireRender -waitForItTwo')
        start_time = time.time()
        mel.eval('renderIntoNewWindow render')
        cmds.sysFile(path.join(WORK_DIR, 'Color'), makeDir=True)
        test_case_path = path.join(WORK_DIR, 'Color', case['case'])
        cmds.renderWindowEditor('renderView', edit=1,  dst=mode)
        cmds.renderWindowEditor('renderView', edit=1, com=1,
                                writeImage=test_case_path)
        test_time = time.time() - start_time

        event('Postrender', True, case['case'])
        reportToJSON(case, test_time)


def postrender(case_num):
    with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
        cases = json.load(json_file)
    case = cases[case_num]

    logging('Postrender', case['case'])
    event("Postrender", True, case['case'])

    case_time = (datetime.datetime.now() - datetime.datetime.strptime(case['start_time'], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
    case['time_taken'] = case_time
    reportToJSON(case, case_time)

    apply_case_functions(case, case['functions'].index("rpr_render(case)") + 1, len(case['functions']))
    event("Postrender", False, case['case'])

    with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
        json.dump(cases, file, indent=4)

    event("Close tool", True, case['case'])


def prerender(case):
    logging('Prerender', case['case'])
    if not BATCH_RENDER:
        scene = case.get('scene', '')

        scenePath = os.path.join(get_scene_path(case), scene)
        logging("Scene path: {{}}".format(scenePath))

        scene_name = cmds.file(q=True, sn=True, shn=True)
        if scene_name != scene:
            try:
                event('Open scene', True, case['case'])
                cmds.file(scenePath, f=True, op='v=0;', prompt=False, iv=True, o=True)
                event('Open scene', False, case['case'])
                enable_rpr(case['case'])
            except Exception as e:
                logging(
                    "Can't prepare for render scene because of {{}}".format(str(e)))

        event("Prerender", True, case['case'])
        cmds.setAttr('RadeonProRenderGlobals.detailedLog', True)
    else:
        enable_rpr(case['case'])
        event("Prerender", True, case['case'])

    logging("mel.eval: athenaEnable -ae false")
    mel.eval('athenaEnable -ae false')

    if ENGINE == 'Tahoe':
        cmds.setAttr('RadeonProRenderGlobals.tahoeVersion', 1)
    elif ENGINE == 'Northstar':
        cmds.setAttr('RadeonProRenderGlobals.tahoeVersion', 2)
    elif ENGINE == 'Hybrid_Low':
        cmds.setAttr("RadeonProRenderGlobals.renderQualityFinalRender", 3)
    elif ENGINE == 'Hybrid_Medium':
        cmds.setAttr("RadeonProRenderGlobals.renderQualityFinalRender", 2)
    elif ENGINE == 'Hybrid_High':
        cmds.setAttr("RadeonProRenderGlobals.renderQualityFinalRender", 1)

    cmds.optionVar(rm='RPR_DevicesSelected')
    cmds.optionVar(iva=('RPR_DevicesSelected',
                        (RENDER_DEVICE in ['gpu', 'dual'])))
    cmds.optionVar(iva=('RPR_DevicesSelected',
                        (RENDER_DEVICE in ['cpu', 'dual'])))

    if RESOLUTION_X and RESOLUTION_Y:
        cmds.setAttr('defaultResolution.width', RESOLUTION_X)
        cmds.setAttr('defaultResolution.height', RESOLUTION_Y)

    cmds.setAttr('defaultRenderGlobals.imageFormat', 8)

    cmds.setAttr('RadeonProRenderGlobals.adaptiveThreshold', THRESHOLD)
    cmds.setAttr(
        'RadeonProRenderGlobals.completionCriteriaIterations', PASS_LIMIT)
    cmds.setAttr('RadeonProRenderGlobals.samplesPerUpdate', SPU)
    cmds.setAttr('RadeonProRenderGlobals.completionCriteriaSeconds', 0)

    if not BATCH_RENDER:
        apply_case_functions(case, 0, len(case['functions']))
    else:
        apply_case_functions(case, 0, case['functions'].index("rpr_render(case)") + 1)




def save_report(case):
    logging('Save report without rendering for ' + case['case'])

    if not os.path.exists(os.path.join(WORK_DIR, 'Color')):
        os.makedirs(os.path.join(WORK_DIR, 'Color'))

    work_dir = path.join(WORK_DIR, 'Color', case['case'] + '.jpg')
    source_dir = path.join(WORK_DIR, '..', '..', '..',
                           '..', 'jobs_launcher', 'common', 'img')

    # image for Athena suite will be set later
    if TEST_TYPE not in ['Athena']:
        if case['status'] == 'inprogress':
            copyfile(path.join(source_dir, 'passed.jpg'), work_dir)
        elif case['status'] != 'skipped':
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
            logging("SetProject skipped.")
            '''
            projPath = os.path.join(RES_PATH, TEST_TYPE)
            temp = os.path.join(projPath, case['scene'][:-3])
            if os.path.isdir(temp):
                projPath = temp
            mel.eval('setProject("{{}}")'.format(projPath.replace('\\', '/')))
            '''
        except:
            pass
            # logging("Can't set project in '" + projPath + "'")

    if case['status'] == 'fail' or case.get('number_of_tries', 0) >= RETRIES:
        case['status'] = 'error'
        func = 'save_report'
    elif case['status'] == 'skipped':
        func = 'save_report'
    else:
        case['number_of_tries'] = case.get('number_of_tries', 0) + 1

    functions[func](case)


# place for extension functions


def main(case_num=None):
    with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
        cases = json.load(json_file)

    event('Open tool', False, next(
        case['case'] for case in cases if case['status'] in ['active', 'fail', 'skipped']))
    if not BATCH_RENDER:
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

                # Athena group will be modified later (now it isn't final result)
                if TEST_TYPE not in ['Athena']:
                    with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
                        json.dump(cases, file, indent=4)

        event('Close tool', True, cases[-1]['case'])

        # Athena need additional time for work before close maya
        if TEST_TYPE not in ['Athena']:
            cmds.quit(abort=True)
        else:
            cmds.evalDeferred('cmds.quit(abort=True)')

    else:
        case = cases[case_num]

        if case['status'] == 'active':
            case['status'] = 'inprogress'

        case['start_time'] = str(datetime.datetime.now())
        case['number_of_tries'] = case.get('number_of_tries', 0) + 1
        
        with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
            json.dump(cases, file, indent=4)
        prerender(case)
