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
LOGS_DIR = path.join(WORK_DIR, 'render_tool_logs')


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

	report['file_name'] = case['case'] + '.jpg'
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


def enable_rpr():
	if not cmds.pluginInfo('RadeonProRender', query=True, loaded=True):
		cmds.loadPlugin('RadeonProRender', quiet=True)
		logging('Load rpr')
	if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
		cmds.loadPlugin('fbxmaya', quiet=True)
		logging('Load fbx')


def rpr_render(case):
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

	reportToJSON(case, test_time)


def prerender(case):
	logging('Prerender')
	scene = case.get('scene', '')
	scene_name = cmds.file(q=True, sn=True, shn=True)
	if scene_name != scene:
		try:
			cmds.file(scene, f=True, op='v=0;', prompt=False, iv=True, o=True)
		except:
			logging("Can't load scene. Exit Maya")
			cmds.evalDeferred('cmds.quit(abort=True)')

	validateFiles()

	enable_rpr()

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

	enable_rpr()

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
			cmds.evalDeferred('cmds.quit(abort=True)')

	if case['status'] == 'fail':
		case['status'] = 'error'
		func = 'save_report'

	functions[func](case)


# place for extension functions


def main():
	if not os.path.exists(os.path.join(WORK_DIR, LOGS_DIR)):
		os.makedirs(os.path.join(WORK_DIR, LOGS_DIR))

	with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
		cases = json.load(json_file)

	for case in cases:
		if case['status'] in ['active', 'fail']:
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

			case_function(case)

			if case['status'] == 'inprogress':
				case['status'] = 'done'
				logging(case['case'] + ' done')

			with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
				json.dump(cases, file, indent=4)

		if case['status'] == 'skipped':
			save_report(case)

	cmds.evalDeferred('cmds.quit(abort=True)')


main()
