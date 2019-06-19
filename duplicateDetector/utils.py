# -*- coding: utf-8 -*-

import time


def clear_string(string: str) -> str:
	if isinstance(string, str):
		string = string.lower()
		string = string.replace("ß", "ss")
		string = string.replace("ä", "ae")
		string = string.replace("ö", "oe")
		string = string.replace("ü", "ue")
		string = string.replace(" ", "")
	return string


def get_data_and_labels(data, keys: list, label_field, data_limit=None, filter_field=None, filter_value=None):
	if filter_field is not None and filter_value is not None:
		data = filter_by_column(data, filter_field, filter_value)
	if data_limit:
		data = data[0:data_limit]
	data = data.applymap(str)
	data_strings = data[keys[0]].copy()
	for i in range(1, len(keys)):
		data_strings += data[keys[i]].copy()
	data_strings = data_strings.T.apply(clear_string)
	data_strings = data_strings.fillna("CVxTz").values
	labels = data[label_field].fillna("CVxTz").values
	return data_strings, labels


def measure(f):
	"""decorator to measure the time it takes to execute a method. prints the
	result after execution"""

	def run_method(*args, **kwargs):
		t1 = time.time()
		res = f(*args, **kwargs)
		print(f"\n{time.time()-t1} seconds\n")
		return res
	return run_method


def filter_by_column(data, field, value):
	return data[data[field] == value]
