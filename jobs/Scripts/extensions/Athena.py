import os.path as path
from shutil import copyfile
import sys
import traceback
import json
sys.path.append(path.abspath(path.join(path.dirname(__file__), path.pardir, path.pardir, path.pardir)))
from jobs_launcher.core.config import main_logger


def process_results(output):
    try:
        with open(path.join(output, 'MAYA_RS_AWS_001_RPR.json'), 'r') as file:
            report = json.load(file)[0]
        with open(path.join(output, 'renderTool.log')) as f:
            if 'successfully uploaded data to AWS!' in f.read():
                main_logger.info('Replace rendered image by passed image (Athena extension)')
                copyfile(path.join(output, '..', '..', '..', '..', 'jobs_launcher', 'common',
                                   'img', 'passed.jpg'), path.join(output, 'Color', 'MAYA_RS_AWS_001.jpg'))
                report['test_status'] = 'passed'
            else:
                main_logger.info('Replace rendered image by error image (Athena extension)')
                copyfile(path.join(output, '..', '..', '..', '..', 'jobs_launcher', 'common',
                                   'img', 'error.jpg'), path.join(output, 'Color', 'MAYA_RS_AWS_001.jpg'))
                report['test_status'] = 'failed'
                report['message'].append('Data wan\'t uploaded to AWS')
        report['group_timeout_exceeded'] = False
        with open(path.join(output, 'MAYA_RS_AWS_001_RPR.json'), 'w') as file:
            json.dump([report], file, indent=4)
    except Exception as e:
        main_logger.error('Failed to execute Athena extension. Exception: {}'.format(str(e)))
        main_logger.error('Traceback: {}'.format(traceback.format_exc()))
