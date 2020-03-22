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

sys.path.append(os.path.abspath(os.path.join(
	os.path.dirname(__file__), os.path.pardir, os.path.pardir)))

from jobs_launcher.core.kill_process import kill_process
from jobs_launcher.core.system_info import get_gpu
import jobs_launcher.core.config as core_config

ROOT_DIR = os.path.abspath(os.path.join(
	os.path.dirname(__file__), os.path.pardir, os.path.pardir))
PROCESS = ['Maya', 'maya.exe']

if platform.system() == 'Darwin':
	from Quartz import CGWindowListCopyWindowInfo
	from Quartz import kCGWindowListOptionOnScreenOnly
	from Quartz import kCGNullWindowID
	from Quartz import kCGWindowName


def get_windows_titles():
	try:
		if platform.system() == 'Darwin':
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
	parser.add_argument('--SPU', required=False, default=25, type=int)
	parser.add_argument('--fail_count', required=False, default=0, type=int)
	parser.add_argument('--threshold', required=False,
						default=0.05, type=float)

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


def launchMaya(cmdScriptPath, work_dir):
	system_pl = platform.system()
	core_config.main_logger.info('Launch script on Maya ({})'.format(cmdScriptPath))
	os.chdir(work_dir)
	p = psutil.Popen(cmdScriptPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


	while True:
		try:
			p.communicate(timeout=40)
			window_titles = get_windows_titles()
			core_config.main_logger.info(
				'Found windows: {}'.format(window_titles))
		except (psutil.TimeoutExpired, subprocess.TimeoutExpired) as err:
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
				rc = -1

				if system_pl == 'Windows':
					try:
						error_screen = pyscreenshot.grab()
						error_screen.save(os.path.join(
							args.output, 'error_screenshot.jpg'))
					except Exception as ex:
						pass

				core_config.main_logger.warning('Killing maya....')

				child_processes = p.children()
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
					p.terminate()
					time.sleep(10)
					p.kill()
					time.sleep(10)
					status = ch.status()
					core_config.main_logger.error(
						'Process is alive: {}. Name: {}. Status: {}'.format(ch, ch.name(), status))
				except psutil.NoSuchProcess:
					core_config.main_logger.warning(
						'Process is killed: {}'.format(ch))

				break
		else:
			rc = 0
			break

	if args.testType in ['Athena']:
		subprocess.call([sys.executable, os.path.realpath(os.path.join(
			os.path.dirname(__file__), 'extensions', args.testType + '.py')), args.output])
	return rc


def main(args):
	if args.testType in ['Support_2019', 'Support_2018']:
		args.tool = re.sub('[0-9]{4}', args.testType[-4:], args.tool)

	if which(args.tool) is None:
		core_config.main_logger.error('Can\'t find tool ' + args.tool)
		exit(-1)

	core_config.main_logger.info('Make "base_functions.py"')

	try:
		cases = json.load(open(os.path.realpath(
			os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'test_cases.json'))))
	except Exception as e:
		core_config.logging.error("Can't load test_cases.json")
		core_config.main_logger.error(str(e))
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
						   resolution_x=args.resolution_x, resolution_y=args.resolution_y, SPU=args.SPU, threshold=args.threshold)

	with open(os.path.join(args.output, 'base_functions.py'), 'w') as file:
		file.write(script)

	if (os.path.exists(args.testCases) and '.json' in args.testCases):
		with open(os.path.join(args.testCases)) as f:
			tc = f.read()
			test_cases = json.loads(tc)[args.testType]
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

	for case in cases:
		if sum([render_platform & set(skip_conf) == set(skip_conf) for skip_conf in case.get('skip_on', '')]):
			for i in case['skip_on']:
				skip_on = set(i)
				if render_platform.intersection(skip_on) == skip_on:
					case['status'] = 'skipped'

		if case['status'] != 'done':
			if case['status'] == 'inprogress':
				case['status'] = 'active'
				case['number_of_tries'] = case.get('number_of_tries', 0) + 1

			template = core_config.RENDER_REPORT_BASE
			template['test_case'] = case['case']
			template['render_device'] = get_gpu()
			template['test_status'] = 'error'
			template['script_info'] = case['script_info']
			template['scene_name'] = case.get('scene', '')
			template['file_name'] = 'failed.jpg'
			template['render_color_path'] = os.path.join('Color', 'failed.jpg')
			template['test_group'] = args.testType
			template['date_time'] = datetime.now().strftime(
				'%m/%d/%Y %H:%M:%S')

			with open(os.path.join(work_dir, case['case'] + core_config.CASE_REPORT_SUFFIX), 'w') as f:
				f.write(json.dumps([template], indent=4))

	with open(os.path.join(work_dir, 'test_cases.json'), 'w+') as f:
		json.dump(cases, f, indent=4)

	system_pl = platform.system()
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

	rc = launchMaya(cmdScriptPath, args.output)

	if args.testType in ['Athena']:
		subprocess.call([sys.executable, os.path.realpath(os.path.join(os.path.dirname(__file__), 'extensions', args.testType + '.py')), args.output])
	core_config.main_logger.info('Main func return : {}'.format(rc))
	return rc


def group_failed(args):
	try:
		cases = json.load(open(os.path.realpath(
			os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'test_cases.json'))))
	except Exception as e:
		core_config.logging.error("Can't load test_cases.json")
		core_config.main_logger.error(str(e))
		exit(-1)

	for case in cases:
		if case['status'] == 'active':
			case['status'] = 'skipped'

	with open(os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'test_cases.json'), 'w+') as f:
		json.dump(cases, f, indent=4)

	rc = main(args)
	kill_process(PROCESS)
	core_config.main_logger.info(
		'Finish simpleRender with code: {}'.format(rc))
	exit(rc)


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

	while True:
		iteration += 1

		core_config.main_logger.info(
			'Try to run script in maya (#' + str(iteration) + ')')

		rc = main(args)

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
		failed_count = 0

		for case in cases:
			if case['status'] in ['fail', 'error', 'inprogress']:
				failed_count += 1
				if args.fail_count == failed_count:
					group_failed(args)
			else:
				failed_count = 0

			if case['status'] in ['active', 'fail', 'inprogress']:
				active_cases += 1

		if active_cases == 0 or iteration > len(cases) * 3:	# 3- retries count
			# exit script if base_functions don't change number of active cases
			kill_process(PROCESS)
			core_config.main_logger.info('Finish simpleRender with code: {}'.format(rc))
			exit(rc)
