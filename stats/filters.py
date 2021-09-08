# Filter by Label names
# Author: Maximilian Noppel
# Date: April 2021



def filterByLabel(dat):
	"""
	Additional function to filter by label names. Not used for
	the evaluation.
	"""

	names = [
		"stat",
		"heart",
		"standby",
		"heartbeat",
		"mmc",
		"panel",
		"usr",
		"user",
		"pwr",
		"power",
		"usb",
		"front",
		"status",
		"wan",
		"wlan",
		"disk",
		"wireless",
		"2.4ghz",
		"5ghz",
		"3g",
		"4g",
		"5g",
		"wps",
		"numlock",
		"capslock",
		"alarm",
		"bt"
	]

	idxs = []
	for row in dat["label"]:
		row = str(row).lower()
		if row == "nan":
			idxs.append(False)
			continue
		res = False
		for l in names:
			if row.__contains__(l):
				res = True
		if res == False:
			print(row)
		idxs.append(res)


	return dat[idxs]