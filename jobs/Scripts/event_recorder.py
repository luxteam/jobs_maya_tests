import glob
import json
import os.path as path
import datetime
from distutils.util import strtobool
from sys import argv

def event(name, start, case):
    with open(path.join('events', str(glob.glob('events/*.json').__len__() + 1) + '.json'), 'w') as f:
        f.write(json.dumps({'name': name, 'time': datetime.datetime.utcnow().strftime(
            '%d/%m/%Y %H:%M:%S.%f'), 'start': start, 'case': case}, indent=4))

if __name__ == "__main__":
    event(argv[1], bool(strtobool(argv[2])), argv[3])