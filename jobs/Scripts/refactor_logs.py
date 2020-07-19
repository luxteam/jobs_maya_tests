import argparse
import os
import json
import datetime
import glob


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


def render_log(work_dir):
    files = [f for f in os.listdir(
        work_dir) if os.path.isfile(os.path.join(work_dir, f))]
    files = [f for f in files if 'renderTool' in f]

    logs = ''

    for f in files:
        logs += '\n\n\n----------LOGS FROM FILE ' + f + '----------\n\n\n'
        with open(os.path.realpath(os.path.join(work_dir, f))) as log:
            logs += log.read()
        os.remove(os.path.realpath(os.path.join(
            work_dir, f)))

    with open(os.path.realpath(os.path.join(work_dir, 'renderTool.log')), 'w') as f:
        for error in errors:
            if error['error'] in logs:
                f.write('[Error] {}\n'.format(error['message']))

        f.write('\n\nCases statuses from test_cases.json\n\n')

        cases = json.load(open(os.path.realpath(
            os.path.join(work_dir, 'test_cases.json'))))

        f.write('Active cases: {}\n'.format(
            len([n for n in cases if n['status'] == 'active'])))
        f.write('Inprogress cases: {}\n'.format(
            len([n for n in cases if n['status'] == 'inprogress'])))
        f.write('Fail cases: {}\n'.format(
            len([n for n in cases if n['status'] == 'fail'])))
        f.write('Error cases: {}\n'.format(
            len([n for n in cases if n['status'] == 'error'])))
        f.write('Done cases: {}\n'.format(
            len([n for n in cases if n['status'] == 'done'])))
        f.write('Skipped cases: {}\n\n'.format(
            len([n for n in cases if n['status'] == 'skipped'])))

        f.write('''\tPossible case statuses:\nActive: Case will be executed.
Inprogress: Case is in progress (if maya was crashed, case will be inprogress).
Fail: Maya was crashed during case. Fail report will be created.
Error: Maya was crashed during case. Fail report is already created.
Done: Case was finished successfully.
Skipped: Case will be skipped. Skip report will be created.\n
Case\t\tStatus\tTime\tTries
\n''')

        f.write(logs)

        for case in cases:
            case_time = '{:.2f}'.format(case.get("time_taken", 0))
            f.write('{}\t{}\t{}\t{}\n'.format(
                case['case'], case['status'], case_time, case.get('number_of_tries', 1)))


def performance_count(work_dir):
    old_event = {'name': 'init', 'time': '', 'start': True}
    time_diffs = []
    work_dir = os.path.join(work_dir, 'events')
    files = glob.glob(os.path.join(work_dir, '*.json'))
    files.sort(key=lambda x: os.path.getmtime(x))
    for f in files:
        with open(f, 'r') as json_file:
            event = json.load(json_file)
        if old_event['name'] == event['name'] and old_event['start'] and not event['start']:
            time_diff = datetime.datetime.strptime(
                event['time'], '%d/%m/%Y %H:%M:%S.%f') - datetime.datetime.strptime(
                old_event['time'], '%d/%m/%Y %H:%M:%S.%f')
            event_case = old_event.get('case', '')
            if not event_case:
                event_case = event.get('case', '')
            if event_case:
                time_diffs.append(
                    {'name': event['name'], 'time': time_diff.total_seconds(), 'case': event_case})
            else:
                time_diffs.append(
                    {'name': event['name'], 'time': time_diff.total_seconds()})
        old_event = event.copy()
    return time_diffs


def main(args):
    work_dir = os.path.abspath(args.output)  # .replace('\\', '/')

    render_log(work_dir)

    with open(os.path.realpath(os.path.join(work_dir, '..', os.path.basename(work_dir) + '_performance.json')), 'w') as f:
        f.write(json.dumps(performance_count(work_dir)))


if __name__ == '__main__':
    args = createArgsParser().parse_args()
    main(args)
