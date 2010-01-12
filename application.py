"""
Main application class.
"""

from logging import warning, error

from PyQt4 import QtGui, QtCore

import qthelpers
from qthelpers import app

import window_db
import menus
import preferences

from make import APP_NAME, ORGANIZATION_NAME


# Map with default application settings (missing ones will be restored from here).
_DEFAULT_SETTINGS = {
	'dbwindow': {
		'width': 600, # starting width of DB window
		'height': 350 # starting height of DB window
	}
}


class Application(qthelpers.Application):

	def __init__(self, argv):

		qthelpers.Application.__init__(self, argv, APP_NAME,
			organization_name=ORGANIZATION_NAME)

		# ensure that all necessary values exist in config
		qthelpers.fillSettings(_DEFAULT_SETTINGS)

		# global menu for Mac OS
		# TODO: check what happens here for non-Macs
		self._main_menu = menus.MainMenu()

		self._db_windows = [] # created DB windows will be stored here
		self._preferences_window = None

		# we need menu to stay alive even if all DB windows are closed
		# (default Mac OS applications behavior)
		self.setQuitOnLastWindowClosed(False)

		# for debug purposes
		app.inst.createDBWindow("/Users/bogdan/gitrepos/sack/test.sack", False)

	def createDBWindow(self, filename, new_file):
		"""
		Create new DB window for given file (if new_file is
		True, the new file should be created).
		"""
		wnd = window_db.DBWindow(filename, new_file)
		self._db_windows.append(wnd)
		wnd.show()

	def showPreferencesWindow(self):
		"""Show preferences window (create it if necessary)"""

		if self._preferences_window is None:
			self._preferences_window = preferences.Preferences()

		self._preferences_window.show()
		self._preferences_window.raise_()
		self._preferences_window.activateWindow()

	def closePreferencesWindow(self):
		"""Preferences were closed, release reference to the window"""
		self._preferences_window = None
