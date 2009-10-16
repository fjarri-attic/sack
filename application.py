from configparser import RawConfigParser
import os.path

from PyQt4 import QtGui, QtCore

import dbwindow
from globals import *
import mainmenu
import preferences


_DEFAULT_SETTINGS = {
	'ui': {
		'language': None, # user interface language; None = use current locale
		'language_fallback': 'en_US' # if language file was not found, use this one
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

		self._translator = None
		self._reloadTranslator()

		self._main_menu = mainmenu.MainMenu()

		self._db_windows = []
		self._preferences_window = None

		self.createDBWindow.connect(self._createDBWindow)
		self.showPreferencesWindow.connect(self._showPreferencesWindow)
		self.closePreferencesWindow.connect(self._closePreferencesWindow)
		self.reloadTranslator.connect(self._reloadTranslator)

		self.setQuitOnLastWindowClosed(False)

	reloadTranslator = QtCore.pyqtSignal()

	def _reloadTranslator(self):

		translator = QtCore.QTranslator()

		lang_from_config = app.settings.value("ui/language")
		if lang_from_config is None:
			locale = QtCore.QLocale.system()
			lang_from_config = locale.name()

		translations = {}
		for short_name, _, full_path in findTranslationFiles():
			translations[short_name] = full_path

		if lang_from_config not in translations:
			QtCore.qWarning("Translation file for " + lang_from_config +
				" was not found, falling back")
			lang_from_config = app.settings('ui/language_fallback')

		if lang_from_config in translations:
			if self._translator is not None:
				self.removeTranslator(self._translator)
				self._translator = None

			if translator.load(translations[lang_from_config]):
				self.installTranslator(translator)
				self._translator = translator
			else:
				QtCore.qCritical("Failed to load translation file " +
					translations[lang_from_config])
		else:
			QtCore.qCritical("Translation file for " +
				lang_from_config + " was not found")

	def changeEvent(self, e):
		if e.type() == QtCore.QEvent.LocaleChange:
			if app.settings.value("ui/language") == None:
				self._reloadTranslator()

		QtGui.Application.changeEvent(self, e)

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
