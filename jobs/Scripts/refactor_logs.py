import argparse
import os
import json


errors = [
	{'error': 'rprCachingShadersWarningWindow',
	 'message': 'Render cache built during cases'},
	{'error': 'Error: Radeon ProRender: IO error',
	 'message': 'Some files/textures are missing'},
	 {'error': 'Error occurred during execution of MEL script',
	 'message': 'Error occurred during execution of MEL script'}
]


def createArgsParser():
	parser = argparse.ArgumentParser()

	parser.add_argument('--output', required=True, metavar='<dir>')

	return parser


def main(args):
	work_dir = os.path.abspath(args.output).replace('\\', '/')
	files = [f for f in os.listdir(
		work_dir) if os.path.isfile(os.path.join(work_dir, f))]
	files = [f for f in files if 'renderTool' in f]

	logs = ''

	for f in files:
		logs += '\n\n\n----------LOGS FROM FILE ' + f + '----------\n\n\n'
		with open(os.path.realpath(os.path.join(os.path.abspath(args.output).replace('\\', '/'), f))) as log:
			logs += log.read()
		os.remove(os.path.realpath(os.path.join(
			os.path.abspath(args.output).replace('\\', '/'), f)))

	with open(os.path.realpath(os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'renderTool.log')), 'w') as f:
		for error in errors:
			if error['error'] in logs:
				f.write('[Error] {}\n'.format(error['message']))

		f.write('\n\nCases statuses from test_cases.json\n\n')

		cases = json.load(open(os.path.realpath(
			os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'test_cases.json'))))

		f.write('Active cases: {}\n'.format(len([n for n in cases if n['status'] == 'active'])))
		f.write('Inprogress cases: {}\n'.format(len([n for n in cases if n['status'] == 'inprogress'])))
		f.write('Fail cases: {}\n'.format(len([n for n in cases if n['status'] == 'fail'])))
		f.write('Error cases: {}\n'.format(len([n for n in cases if n['status'] == 'error'])))
		f.write('Done cases: {}\n'.format(len([n for n in cases if n['status'] == 'done'])))
		f.write('Skipped cases: {}\n\n'.format(len([n for n in cases if n['status'] == 'skipped'])))

		f.write('''\tPossible case statuses:\nActive: Case will be executed.
Inprogress: Case is in progress (if maya was crashed, case will be inprogress).
Fail: Maya was crashed during case. Fail report will be created.
Error: Maya was crashed during case. Fail report is already created.
Done: Case was finished successfully.
Skipped: Case will be skipped. Skip report will be created.
\n''')

		for case in cases:
			f.write('{} - {}\n'.format(case['case'], case['status']))

		f.write(logs)


if __name__ == '__main__':
	args = createArgsParser().parse_args()
	main(args)
