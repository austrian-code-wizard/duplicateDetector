import os


def _get_path():
	full_path = os.path.dirname(os.path.abspath(__file__))
	if os.name == "posix":
		space_char = "/"
	elif os.name == "nt":
		space_char = "\\"
	else:
		raise ValueError("Unable to determine root path for operating system")
	split_path = full_path.split(space_char)
	split_path.pop()
	return space_char.join(split_path)+space_char


ROOT_PATH = _get_path()


