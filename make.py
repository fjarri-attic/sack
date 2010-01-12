import os

import qthelpers

APP_NAME = "Sack"
ORGANIZATION_NAME = "Manti"
SOURCES = [
	'application.py',
	'menus.py',
	'preferences.py',
	'window_db.py',
	'window_object.py',
	'window_search.py'
]

if __name__ == "__main__":
	prj = qthelpers.QtProject(os.path.abspath(os.path.dirname(__file__)), sources=SOURCES)
	prj.build()
