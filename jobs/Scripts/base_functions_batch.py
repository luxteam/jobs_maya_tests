import maya.mel as mel
import maya.cmds as cmds
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
LOGS_DIR = path.join(WORK_DIR, 'render_tool_logs')
FILE_FORMATS = {{0: 'gif', 1: 'pic', 2: 'rla', 3: 'tif', 4: 'tif', 5: 'sgi', 6: 'als', 7: 'iff', 8: 'jpg', 9: 'eps', 10: 'iff', 12: 'yuv', 13: 'sgi', 19: 'tga', 20: 'bmp', 31: 'psd', 32: 'png', 35: 'dds', 36: 'psd', 40: 'exr '}}
cases_num_queue = deque()
with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
    cases = json.load(json_file)


def logging(message, case=None):
    message = ' >>> [RPR TEST] [' + datetime.datetime.now().strftime('%H:%M:%S') + '] ' + message + '\n'
    if case is not None:
        open(os.path.join(LOGS_DIR, case['case']+'.log'), 'a').write(message)
    print(message)


def render_tool_log_path(name):
    return path.join(LOGS_DIR, name + '.log')


def get_current_frame_img_name():
    frame_number = "{{0:0{{1}}d}}".format(int(cmds.currentTime(q=True)), cmds.getAttr("defaultRenderGlobals.extensionPadding"))
    return "{{}}.{{}}".format(cmds.getAttr('defaultRenderGlobals.imageFilePrefix'), frame_number)


def pre_functions(case):
    rpr_render_index = case['functions'].index("rpr_render(case)")
    for function in case['functions'][:rpr_render_index + 1]:
        try:
            if re.match('((^\S+|^\S+ \S+) = |^print|^if|^for|^with)', function):
                logging("exec: {{}}".format(function), case)
                exec(function)
            else:
                logging("eval: {{}}".format(function), case)
                eval(function)
        except Exception as e:
            logging('Error "{{}}" with string "{{}}"'.format(e, function), case)


def post_functions(case):
    rpr_render_index = case['functions'].index("rpr_render(case)")
    for function in case['functions'][rpr_render_index + 1:]:
        try:
            if re.match('((^\S+|^\S+ \S+) = |^print|^if|^for|^with)', function):
                logging("exec: {{}}".format(function), case)
                exec(function)
            else:
                logging("eval: {{}}".format(function), case)
                eval(function)
        except Exception as e:
            logging('Error "{{}}" with string "{{}}"'.format(e, function), case)


def extract_img_from(folder, case):
    src_dir = path.join(WORK_DIR, 'Color', folder)
    if 'functions_before_render' in case and case['functions_before_render']:
        img_name = cmds.renderSettings(firstImageName=True)[0]
    else:
        img_name = get_current_frame_img_name()
        
    if os.path.exists(src_dir) and os.path.isdir(src_dir):
        try:
            move(path.join(src_dir, img_name), path.join(WORK_DIR, 'Color'))
            logging('Extract {{}} from {{}} folder'.format(img_name, folder), case)
        except Exception as ex:
            logging('Error while extracting {{}} from {{}}: {{}}'.format(img_name, folder, ex), case)
    else:
        logging("{{}} doesn't exist or isn't a folder".format(folder), case)


def reportToJSON(case, render_time=0):
    path_to_file = path.join(WORK_DIR, case['case'] + '_RPR.json')

    with open(path_to_file, 'r') as file:
        report = json.loads(file.read())[0]

    if case['status'] == 'inprogress':
        case['status'] = 'done'
        logging(case['case'] + ' done', case)
        report['test_status'] = 'passed'
        report['group_timeout_exceeded'] = False
    else:
        report['test_status'] = case['status']

    logging('Create report json ({{}} {{}})'.format(
            case['case'], report['test_status']), case)
    if case['status'] == 'error':
        number_of_tries = case.get('number_of_tries', 0)
        if number_of_tries == RETRIES:
            error_message = 'Testcase wasn\'t executed successfully (all attempts were used). Number of tries: {{}}'.format(str(number_of_tries))
        else:
            error_message = 'Testcase wasn\'t executed successfully. Number of tries: {{}}'.format(str(number_of_tries))
        report['message'] = [error_message]
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
    if case['status'] != 'skipped':
        report['file_name'] = case['case'] + case.get('extension', '.jpg')
        report['render_color_path'] = path.join('Color', report['file_name'])

    # save metrics which can be received witout call of functions of Maya
    with open(path_to_file, 'w') as file:
        file.write(json.dumps([report], indent=4))

    try:
        report['tool'] = mel.eval('about -iv')
    except Exception as e:
        logging('Failed to get Maya version. Reason: {{}}'.format(str(e)), case)
    try:
        report['render_version'] = mel.eval('getRPRPluginVersion()')
    except Exception as e:
        logging('Failed to get render version. Reason: {{}}'.format(str(e)), case)
    try:
        report['core_version'] = mel.eval('getRprCoreVersion()')
    except Exception as e:
        logging('Failed to get core version. Reason: {{}}'.format(str(e)), case)

    # save metrics which can't be received witout call of functions of Maya (additional measures to avoid stucking of Maya)
    with open(path_to_file, 'w') as file:
        file.write(json.dumps([report], indent=4))


def validateFiles(case):
    logging('Repath scene', case)
    cmds.filePathEditor(refresh=True)
    unresolved_files = cmds.filePathEditor(query=True, listFiles='', unresolved=True, attributeOnly=True)
    logging("Unresolved items: {{}}".format(str(unresolved_files)), case)
    logging('Start repath scene', case)
    if unresolved_files:
        for item in unresolved_files:
            cmds.filePathEditor(item, repath=RES_PATH, recursive=True, ra=1)
    unresolved_files = cmds.filePathEditor(query=True, listFiles='', unresolved=True, attributeOnly=True)
    logging("Unresolved items: {{}}".format(str(unresolved_files)), case)
    logging('Repath finished', case)


def enable_rpr(case):
    if not cmds.pluginInfo('RadeonProRender', query=True, loaded=True):
        event('Load rpr', True, case)
        cmds.loadPlugin('RadeonProRender', quiet=True)
        event('Load rpr', False, case)
        logging('Load rpr')


def rpr_render(case, mode='color'):
    event("Prerender", False, case['case'])
    validateFiles(case)
    logging('Prerender done', case)
    
    
def pre_render(case=None, separate_case=True):
    logging('Prerender')
    enable_rpr(case['case'] if case is not None else "")

    event("Prerender", True, case['case'] if separate_case else "")

    logging("mel.eval: athenaEnable -ae false")
    mel.eval('athenaEnable -ae false')

    if ENGINE == 'Tahoe':
        logging("cmds.setAttr: RadeonProRenderGlobals.tahoeVersion, 1")
        cmds.setAttr('RadeonProRenderGlobals.tahoeVersion', 1)
    elif ENGINE == 'Northstar':
        logging("cmds.setAttr: RadeonProRenderGlobals.tahoeVersion, 2")
        cmds.setAttr('RadeonProRenderGlobals.tahoeVersion', 2)
    elif ENGINE == 'Hybrid_Low':
        logging("cmds.setAttr: RadeonProRenderGlobals.renderQualityFinalRender, 3")
        cmds.setAttr("RadeonProRenderGlobals.renderQualityFinalRender", 3)
    elif ENGINE == 'Hybrid_Medium':
        logging("cmds.setAttr: RadeonProRenderGlobals.renderQualityFinalRender, 2")
        cmds.setAttr("RadeonProRenderGlobals.renderQualityFinalRender", 2)
    elif ENGINE == 'Hybrid_High':
        logging("cmds.setAttr: RadeonProRenderGlobals.renderQualityFinalRender, 1")
        cmds.setAttr("RadeonProRenderGlobals.renderQualityFinalRender", 1)

    logging("cmds.optionVar: rm=RPR_DevicesSelected")
    cmds.optionVar(rm='RPR_DevicesSelected')
    logging("cmds.optionVar: iva=RPR_DevicesSelected, (RENDER_DEVICE in ['gpu', 'dual'])")
    cmds.optionVar(iva=('RPR_DevicesSelected',
                        (RENDER_DEVICE in ['gpu', 'dual'])))
    logging("cmds.optionVar: iva=RPR_DevicesSelected, (RENDER_DEVICE in ['cpu', 'dual'])")
    cmds.optionVar(iva=('RPR_DevicesSelected',
                        (RENDER_DEVICE in ['cpu', 'dual'])))

    if RESOLUTION_X and RESOLUTION_Y:
        logging("cmds.setAttr: defaultResolution.width, RESOLUTION_X")
        cmds.setAttr('defaultResolution.width', RESOLUTION_X)
        logging("cmds.setAttr: defaultResolution.height, RESOLUTION_Y")
        cmds.setAttr('defaultResolution.height', RESOLUTION_Y)

    logging("cmds.setAttr: defaultRenderGlobals.imageFormat, 8")
    cmds.setAttr('defaultRenderGlobals.imageFormat', 8)

    logging("cmds.setAttr: RadeonProRenderGlobals.adaptiveThreshold, THRESHOLD")
    cmds.setAttr('RadeonProRenderGlobals.adaptiveThreshold', THRESHOLD)
    logging("cmds.setAttr: RadeonProRenderGlobals.completionCriteriaIterations, PASS_LIMIT")
    cmds.setAttr(
        'RadeonProRenderGlobals.completionCriteriaIterations', PASS_LIMIT)
    logging("cmds.setAttr: RadeonProRenderGlobals.samplesPerUpdate, SPU")
    cmds.setAttr('RadeonProRenderGlobals.samplesPerUpdate', SPU)
    logging("cmds.setAttr: RadeonProRenderGlobals.completionCriteriaSeconds, 0")
    cmds.setAttr('RadeonProRenderGlobals.completionCriteriaSeconds', 0)

    logging("cmds.setAttr: defaultRenderGlobals.startFrame / endFrame / byFrameStep")
    cmds.setAttr("defaultRenderGlobals.startFrame", 1)
    cmds.setAttr("defaultRenderGlobals.endFrame", len(cases_num_queue))
    cmds.setAttr("defaultRenderGlobals.byFrameStep", 1)

    if separate_case:
        pre_functions(case)
    else:
        event("Prerender", False, "")


def pre_frame():
    # Same as peekLeft
    case = cases[cases_num_queue[0]]
    
    logging("Preframe preparation", case)
    event("Prerender", True, case['case'])

    if case['status'] == 'active':
        case['status'] = 'inprogress'

    case['start_time'] = str(datetime.datetime.now())
    case['number_of_tries'] = case.get('number_of_tries', 0) + 1
    
    with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
        json.dump(cases, file, indent=4)

    cmds.commandLogging( logFile=path.join(LOGS_DIR, case['case']))

    pre_functions(case)


def post_frame():
    case = cases[cases_num_queue.popleft()]
    logging("Postframe operations", case)
    event("Postrender", True, case['case'])
    
    case_time = (datetime.datetime.now() - datetime.datetime.strptime(case['start_time'], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
    case['time_taken'] = case_time
    reportToJSON(case, case_time)

    post_functions(case)
    event("Postrender", False, case['case'])

    #? Is it possible to make an elegant solution?
    source_name = path.join(WORK_DIR, 'Color', get_current_frame_img_name()) 
    new_name = "{{}}.{{}}".format(path.join(WORK_DIR, 'Color', case['case']), FILE_FORMATS[cmds.getAttr("defaultRenderGlobals.imageFormat")])
    logging("Image rename", case)
    cmds.sysFile(source_name, rename=new_name)

    with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
        json.dump(cases, file, indent=4)


def post_render(case_num=None, separate_case=True):
    logging('Postrender')

    if separate_case:
        
        with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
            cases = json.load(json_file)
        case = cases[case_num]

        event("Postrender", True, case['case'])

        case_time = (datetime.datetime.now() - datetime.datetime.strptime(case['start_time'], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
        case['time_taken'] = case_time
        reportToJSON(case, case_time)

        post_functions(case)
        event("Postrender", False, case['case'])
        with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
            json.dump(cases, file, indent=4)

        event("Close tool", True, case['case'])
    else:
        event("Close tool", True, "")


# place for extension functions


def main(case_num=None, separate_case=True):
    event('Open tool', False, "")
    logging('Entered main')
    if separate_case:
        # Case number defined directly, if functions_before_render flag is True
        case = cases[case_num]

        if case['status'] == 'active':
            case['status'] = 'inprogress'

        case['start_time'] = str(datetime.datetime.now())
        case['number_of_tries'] = case.get('number_of_tries', 0) + 1
        
        with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
            json.dump(cases, file, indent=4)
        pre_render(case, separate_case)
    else:
        scene_name = cmds.file(q=True, sn=True, shn=True)
        cameras = cmds.listCameras(p=True)
        for cam in cameras:
            if cmds.getAttr("{{}}.renderable".format(cam)) == 1:
                current_cam = cam

        case_num = -1
        for case in cases:
            case_num += 1
            
            if 'functions_before_render' not in case or not case['functions_before_render']:
                if 'scene' in case and case['scene'] == scene_name and case['status'] in ['active', 'inprogress']:
                    if 'camera' not in case or case['camera'] == current_cam:
                        cases_num_queue.append(case_num)

        pre_render(separate_case=separate_case)

    
