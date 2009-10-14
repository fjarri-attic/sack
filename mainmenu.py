from PyQt4 import QtGui

from appglobals import *
import hotkeys
import sack_qrc


class MainMenu(QtGui.QMenuBar):

	def __init__(self):
		QtGui.QMenuBar.__init__(self)

		self._file_formats = app.translate("MainMenu", "Sack databases") + " (*.sack);;" + \
			app.translate("MainMenu", "All files") + " (*.*)"
		self._default_dir = '~'
		self._preferences_window = None

		file = self.addMenu(app.translate("MainMenu", "&File"))

		file_new = QtGui.QAction(app.translate("MainMenu", "&New Sack"), self)
		file_new.setShortcut(hotkeys.NEW)
		file_new.triggered.connect(self._showFileNewDialog)
		file.addAction(file_new)

		file_open = QtGui.QAction(app.translate("MainMenu", "&Open Sack"), self)
		file_open.setShortcut(hotkeys.OPEN)
		file_open.triggered.connect(self._showFileOpenDialog)
		file.addAction(file_open)

		preferences = QtGui.QAction(app.translate("MainMenu", "&Preferences"), self)
		preferences.triggered.connect(self._showPreferences)
		file.addAction(preferences)

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
