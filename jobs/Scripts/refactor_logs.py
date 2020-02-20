import argparse
import os
import json


errors = [
	{'error': 'rprCachingShadersWarningWindow',
	 'message': 'Render cache built during cases'},
	{'error': 'Error: Radeon ProRender: IO error',
	 'message': 'Some files/textures are missing'}
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
				f.write('!!!{}!!!\n\n\n'.format(error['message']))

		f.write(logs)

		f.write('\n\n\nCases statuses from test_cases.json\n\n')

		cases = json.load(open(os.path.realpath(
			os.path.join(os.path.abspath(args.output).replace('\\', '/'), 'test_cases.json'))))

		for case in cases:
			f.write(case['case'] + ' - ' + case['status'] + '\n')


if __name__ == '__main__':
	args = createArgsParser().parse_args()
	main(args)
