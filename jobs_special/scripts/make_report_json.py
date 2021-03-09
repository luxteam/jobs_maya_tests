import argparse
import os


parser = argparse.ArgumentParser()
parser.add_argument('--work_dir', required=True)

args = parser.parse_args()
directory = args.work_dir

files = os.listdir(directory)
json_files = list(filter(lambda x: x.endswith('RPR.json'), files))
result_json = ""

for file in range(len(json_files)):

    if (len(json_files) == 1):
        f = open(os.path.join(directory, json_files[file]), 'r')
        text = f.read()
        f.close()
        result_json += text
        break

    if (file == 0):
        f = open(os.path.join(directory, json_files[file]), 'r')
        text = f.read()
        f.close()
        text = text[:-2]
        text = text + "," + "\r\n"
        result_json += text

    elif (file == (len(json_files))-1):
        f = open(os.path.join(directory, json_files[file]), 'r')
        text = f.read()
        f.close()
        text = text[2:]
        result_json += text

    else:
        f = open(os.path.join(directory, json_files[file]), 'r')
        text = f.read()
        f.close()
        text = text[2:]
        text = text[:-2]
        text = text + "," + "\r\n"
        result_json += text

with open(os.path.join(directory, "report.json"), 'w') as file:
    file.write(result_json)
