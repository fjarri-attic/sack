from PyQt4 import QtGui

from appglobals import *
import hotkeys


class DynamicTranslator:

	class Changer:
		def __init__(self, changer):
			self._changer = changer
			self._context = None
			self._text = None

		def translate(self, context, text):
			self._context = context
			self._text = text
			self.refresh()

		def refresh(self):
			if self._text is not None:
				self._changer(app.translate(self._context, self._text))
			else:
				self._changer()

	def __init__(self):
		self._changers = []

	def add(self, changer):
		c = self.Changer(changer)
		self._changers.append(c)
		return c

	def refresh(self):
		for changer in self._changers:
			changer.refresh()


class MainMenu(QtGui.QMenuBar):

	def __init__(self):
		QtGui.QMenuBar.__init__(self)

		self._dyn = DynamicTranslator()

		self._dyn.add(self._setFileFormatsString)

		self._default_dir = '~'
		self._preferences_window = None

		file = self.addMenu("")
		self._dyn.add(file.setTitle).translate("MainMenu", "&File")

		file_new = QtGui.QAction(app.translate("MainMenu", "&New Sack"), self)
		file_new.setShortcut(hotkeys.NEW)
		file_new.triggered.connect(self._showFileNewDialog)
		file.addAction(file_new)

		file_open = QtGui.QAction(app.translate("MainMenu", "&Open Sack"), self)
		file_open.setShortcut(hotkeys.OPEN)
		file_open.triggered.connect(self._showFileOpenDialog)
		file.addAction(file_open)

		# not translating this name, because on Mac OS it will be automatically
		# linked to application's standard preferences menu item
		preferences = QtGui.QAction("&Preferences", self)
		preferences.triggered.connect(self._showPreferences)
		file.addAction(preferences)

	def _setFileFormatsString(self):
		self._file_formats = app.translate("MainMenu", "Sack databases") + " (*.sack);;" + \
			app.translate("MainMenu", "All files") + " (*.*)"

	def changeEvent(self, e):
		if e.type() == QtCore.QEvent.LanguageChange:
			self._dyn.refresh()
		QtGui.QMenuBar.changeEvent(self, e)

	def _showFileNewDialog(self):
		self._showFileDialog(QtGui.QFileDialog.getSaveFileName,
			app.translate("MainMenu", "New Sack"), True)

	def _showFileOpenDialog(self):
		self._showFileDialog(QtGui.QFileDialog.getOpenFileName,
			app.translate("MainMenu", "Open Sack"), False)

	def _showFileDialog(self, func, title, new_file):
		filename = func(self, title,
			self._default_dir, self._file_formats)
		if filename is not None:
			app.inst.createDBWindow.emit(filename, new_file)

	def _showPreferences(self):
		app.inst.showPreferencesWindow.emit()
