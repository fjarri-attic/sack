from configparser import RawConfigParser
import os.path

from PyQt4 import QtGui, QtCore

from appglobals import *
import dbwindow
import mainmenu
import preferences
import sack_qrc


_DEFAULT_SETTINGS = {
	'ui': {
		'language': 'en' # user interface language
	},
	'dbwindow': {
		'width': 600, # starting width of DB window
		'height': 350 # starting height of DB window
	}
}


class Application(QtGui.QApplication):

	def __init__(self, argv):
		QtGui.QApplication.__init__(self, argv)
		self.setApplicationName("Sack")
		self.setOrganizationName("Manti")

		self._fillSettings(_DEFAULT_SETTINGS)

		self.reloadTranslator()

		self._main_menu = mainmenu.MainMenu()

		self._db_windows = []
		self._preferences_window = None

		self.createDBWindow.connect(self._createDBWindow)
		self.showPreferencesWindow.connect(self._showPreferencesWindow)
		self.closePreferencesWindow.connect(self._closePreferencesWindow)

		self.setQuitOnLastWindowClosed(False)


	def reloadTranslator(self):

		file_name = ':/translations/sack_' + app.settings.value("ui/language") + '.qm'
		translation_file = QtCore.QFile(file_name)

		if translation_file.exists():
			translator = QtCore.QTranslator()
			translator.load(file_name)
			self.installTranslator(translator)

	createDBWindow = QtCore.pyqtSignal(str, bool)

	def _createDBWindow(self, filename, new_file):
		wnd = dbwindow.DBWindow(filename, new_file)
		self._db_windows.append(wnd)
		wnd.show()

	showPreferencesWindow = QtCore.pyqtSignal()

	def _showPreferencesWindow(self):
		if self._preferences_window is None:
			self._preferences_window = preferences.Preferences()

		self._preferences_window.show()
		self._preferences_window.raise_()
		self._preferences_window.activateWindow()

	closePreferencesWindow = QtCore.pyqtSignal()

	def _closePreferencesWindow(self):
		self._preferences_window = None

	def _fillSettings(self, data):

		def fill(settings, dict_obj):
			for key in dict_obj:
				if isinstance(dict_obj[key], dict):
					settings.beginGroup(key)
					fill(settings, dict_obj[key])
					settings.endGroup()
				else:
					if not settings.contains(key):
						settings.setValue(key, dict_obj[key])

		settings = QtCore.QSettings()
		fill(settings, data)
