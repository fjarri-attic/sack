from PyQt4 import QtGui

from globals import *
import hotkeys


class MainMenu(QtGui.QMenuBar):

	def __init__(self):
		QtGui.QMenuBar.__init__(self)

		self._dyntr = DynamicTranslator()

		self._dyntr.add(self._setFileFormatsString)

		self._default_dir = '~'
		self._preferences_window = None

		file = self.addMenu("")
		self._dyntr.add(file.setTitle).translate("MainMenu", "&File")

		file_new = QtGui.QAction(self)
		self._dyntr.add(file_new.setText).translate("MainMenu", "&New Sack")
		file_new.setShortcut(hotkeys.NEW)
		file_new.triggered.connect(self._showFileNewDialog)
		file.addAction(file_new)

		file_open = QtGui.QAction(self)
		self._dyntr.add(file_open.setText).translate("MainMenu", "&Open Sack")
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
			self._dyntr.refresh()
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
