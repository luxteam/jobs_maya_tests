import os.path as path
from shutil import copyfile
import sys


try:
	with open(path.join(sys.argv[1], 'renderTool.log')) as f: 
		if 'successfully uploaded data to AWS!' in f.read(): 
			copyfile(path.join(sys.argv[1], '..', '..', '..', '..', 'jobs_launcher', 'common', 'img', 'passed.jpg'), path.join(sys.argv[1], 'Color', 'MAYA_RS_AWS_001.jpg'))
		else:
			copyfile(path.join(sys.argv[1], '..', '..', '..', '..', 'jobs_launcher', 'common', 'img', 'error.jpg'), path.join(sys.argv[1], 'Color', 'MAYA_RS_AWS_001.jpg'))
except:pass