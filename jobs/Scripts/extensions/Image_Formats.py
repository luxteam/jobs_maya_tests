def setPass(case):
	work_dir = path.join(WORK_DIR, 'Color', case['case'] + case.get('extension', '.jpg'))
	source_dir = path.join(WORK_DIR, '..', '..', '..',
						   '..', 'jobs_launcher', 'common', 'img')

	copyfile(path.join(source_dir, 'passed.jpg'), work_dir)