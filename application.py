from configparser import RawConfigParser
import os.path

from PyQt4 import QtGui, QtCore

from appglobals import *
import dbwindow
import mainmenu
import sack_qrc


class Application(QtGui.QApplication):

	create_db_window = QtCore.pyqtSignal(str, bool)

	def __init__(self, argv):
		QtGui.QApplication.__init__(self, argv)
		self.setApplicationName("Sack")
		self.setOrganizationName("Manti")

		self._fillDefaultSettings()

		self.reloadTranslator()

		self._main_menu = mainmenu.MainMenu()

		self._db_windows = []

		self.create_db_window.connect(self._createDBWindow)

		self.setQuitOnLastWindowClosed(False)


	def reloadTranslator(self):

		file_name = ':/translations/sack_' + app.settings.value("ui/language") + '.qm'
		translation_file = QtCore.QFile(file_name)

		if translation_file.exists():
			translator = QtCore.QTranslator()
			translator.load(file_name)
			self.installTranslator(translator)

	def _createDBWindow(self, filename, new_file):
		db_window = dbwindow.DBWindow(filename, new_file)
		self._db_windows.append(db_window)
		db_window.show()

		# Mac OS specific - required in addition to show()
		db_window.raise_()

	def _fillDefaultSettings(self):

		defaults = {
			'ui': {
				'language': 'en'
			},
			'dbwindow': {
				'width': 600,
				'height': 350
			}
		}

		def fill(settings, data):
			for key in data:
				if isinstance(data[key], dict):
					settings.beginGroup(key)
					fill(settings, data[key])
					settings.endGroup()
				else:
					if not settings.contains(key):
						settings.setValue(key, data[key])

		settings = QtCore.QSettings()
		fill(settings, defaults)
