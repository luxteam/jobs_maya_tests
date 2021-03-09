import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

ROOT_DIR = os.path.dirname(os.path.abspath(__file__+'\\..\\..\\..'))

scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)

sheet = client.open("Skipped Tests").worksheet("Maya")
workspace = sheet.range('A5:C1000')
case_descriptions = dict(zip(sheet.col_values(2)[4:],sheet.col_values(3)[4:]))

# delete all preveious entries
for cell in workspace:
	cell.value = ''

sheet.update_cells(workspace)

current_cell_row = 0


# getting all "test_cases.json" files
for dirpath, dirnames, filenames in os.walk(ROOT_DIR+'\\jobs\\Tests'):
	for tests_file_name in [f for f in filenames if f.endswith(".json")]:
		found_skipped_tests = False
		tests_file_path = os.path.join(dirpath, tests_file_name)

		# parsing files to json
		with open(tests_file_path) as test_file:
			tests_info = json.load(test_file)
		for test_case in tests_info:
			if(test_case['status'] == 'skipped' or 'skip_engine' in test_case or 'skip_config' in test_case):
				if(not found_skipped_tests):
					found_skipped_tests = True
					workspace[3 * current_cell_row].value = dirpath.split("\\")[-1]
					current_cell_row += 1
				if(test_case["case"] in case_descriptions):
					workspace[3 * current_cell_row + 2].value = case_descriptions[test_case["case"]]
				workspace[3 * current_cell_row + 1].value = test_case["case"]
				current_cell_row += 1

sheet.update_cells(workspace)