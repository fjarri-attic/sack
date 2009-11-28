"""
Global application menu.
"""

from PyQt4 import QtGui

from globals import *
import hotkeys


@dynamically_translated
class MainMenu(QtGui.QMenuBar):

	def __init__(self):
		QtGui.QMenuBar.__init__(self)

		self.dynTr(self._setFileFormatsString).refresh()

		# default directory for New and Open file dialogs
		# TODO: remember the last used directory and use it here
		self._default_dir = '~'

		# File menu

		file = self.addMenu("")
		self.dynTr(file.setTitle).translate("MainMenu", "&File")

		file_new = QtGui.QAction(self)
		self.dynTr(file_new.setText).translate("MainMenu", "&New Sack")
		file_new.setShortcut(hotkeys.NEW)
		file_new.triggered.connect(self._showFileNewDialog)
		file.addAction(file_new)

		file_open = QtGui.QAction(self)
		self.dynTr(file_open.setText).translate("MainMenu", "&Open Sack")
		file_open.setShortcut(hotkeys.OPEN)
		file_open.triggered.connect(self._showFileOpenDialog)
		file.addAction(file_open)

		# not translating this name, because on Mac OS it will be automatically
		# linked to application's standard preferences menu item
		# TODO: translate this for non-Macs
		preferences = QtGui.QAction("&Preferences", self)
		preferences.triggered.connect(app.inst.showPreferencesWindow)
		file.addAction(preferences)

	def _setFileFormatsString(self):
		"""Helper for dynamic translation - set file formats string."""
		self._file_formats = app.translate("MainMenu", "Sack databases") + \
			" (*.sack);;" + app.translate("MainMenu", "All files") + " (*.*)"

	def _showFileNewDialog(self):
		# Using Save File dialog, because we need to create physical representation
		# of DB on a medium before starting to change it.
		# In other words, do not bother with copying an in-memory DB to disk.
		self._showFileDialog(QtGui.QFileDialog.getSaveFileName,
			app.translate("MainMenu", "New Sack"), True)

	def _showFileOpenDialog(self):
		self._showFileDialog(QtGui.QFileDialog.getOpenFileName,
			app.translate("MainMenu", "Open Sack"), False)

	def _showFileDialog(self, func, title, new_file):
		"""Show dialog for choosing file to open"""
		filename = func(self, title,
			self._default_dir, self._file_formats)
		if filename is not None:
			app.inst.createDBWindow(filename, new_file)


class WindowMenu(MainMenu):

	searchTabRequested = QtCore.pyqtSignal()

	def __init__(self):
		MainMenu.__init__(self)

		actions = self.addMenu("")
		self.dynTr(actions.setTitle).translate("MainMenu", "&Actions")

		action_search = QtGui.QAction(self)
		self.dynTr(action_search.setText).translate("MainMenu", "&Search")
		action_search.triggered.connect(self.searchTabRequested)
		actions.addAction(action_search)
