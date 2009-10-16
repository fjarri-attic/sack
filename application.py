"""
Main application class.
"""

from PyQt4 import QtGui, QtCore

import dbwindow
from globals import *
import mainmenu
import preferences


# Map with default application settings (missing ones will be restored from here).
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

		# ensure that all necessary values exist in config
		self._fillSettings(_DEFAULT_SETTINGS)

		self._translator = None
		self._reloadTranslator()

		# on Mac OS menu is global for all windows
		self._main_menu = mainmenu.MainMenu()

		self._db_windows = [] # created DB windows will be stored here
		self._preferences_window = None

		self.createDBWindow.connect(self._createDBWindow)
		self.showPreferencesWindow.connect(self._showPreferencesWindow)
		self.closePreferencesWindow.connect(self._closePreferencesWindow)
		self.reloadTranslator.connect(self._reloadTranslator)

		# we need menu to stay alive even if all DB windows are closed
		# (default Mac OS applications behavior)
		self.setQuitOnLastWindowClosed(False)

	reloadTranslator = QtCore.pyqtSignal()

	def _reloadTranslator(self):
		"""
		Reload translator file according to current language
		value from settings.
		"""

		translator = QtCore.QTranslator()

		# get current language; if it is None, use current locale
		lang_from_config = app.settings.value("ui/language")
		if lang_from_config is None:
			locale = QtCore.QLocale.system()
			lang_from_config = locale.name()

		translations = {}
		for short_name, _, full_path in findTranslationFiles():
			translations[short_name] = full_path

		# if language file was not found, use the backup one
		if lang_from_config not in translations:
			QtCore.qWarning("Translation file for " + lang_from_config +
				" was not found, falling back")
			lang_from_config = app.settings('ui/language_fallback')

		# load translation file
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
		# if language is set to current locale, and locale has changed -
		# we need to reload translator
			if app.settings.value("ui/language") == None:
				self._reloadTranslator()

		QtGui.Application.changeEvent(self, e)

	createDBWindow = QtCore.pyqtSignal(str, bool)

	def _createDBWindow(self, filename, new_file):
		"""
		Create new DB window for given file (if new_file is
		True, the new file should be created).
		"""
		wnd = dbwindow.DBWindow(filename, new_file)
		self._db_windows.append(wnd)
		wnd.show()

	showPreferencesWindow = QtCore.pyqtSignal()

	def _showPreferencesWindow(self):
		"""Show preferences window (create it if necessary)"""

		if self._preferences_window is None:
			self._preferences_window = preferences.Preferences()

		self._preferences_window.show()
		self._preferences_window.raise_()
		self._preferences_window.activateWindow()

	closePreferencesWindow = QtCore.pyqtSignal()

	def _closePreferencesWindow(self):
		"""Preferences were closed, release reference to the window"""
		self._preferences_window = None

	def _fillSettings(self, data):
		"""Fill missing settings with default ones"""

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
