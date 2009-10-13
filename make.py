import os.path
from subprocess import Popen

os.chdir(os.path.abspath(os.path.dirname(__file__)))

def execute(cmd):
	result = Popen(cmd).wait()
	if result != 0:
		raise Exception("Error: " + str(result))

execute(["/Library/Frameworks/Python.framework/Versions/3.1/bin/pylupdate4", "sack.pro"])
execute(["lrelease", "sack.pro"])
execute(["/Library/Frameworks/Python.framework/Versions/3.1/bin/pyrcc4",
	"sack.qrc", "-o", "sack_qrc.py", "-py3"])
