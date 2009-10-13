import sys
from PyQt4 import QtGui, QtCore

import brain

from dbwindow import DBWindow
import config
import hotkeys


class Application(QtGui.QApplication):

	create_db_window = QtCore.pyqtSignal(str, bool)

	def __init__(self):
		QtGui.QApplication.__init__(self, sys.argv)

		config.init()

		self._main_menu = MainMenu(self)
		self._db_windows = []

		self.create_db_window.connect(self.createDBWindow)

		self.setQuitOnLastWindowClosed(False)

	def createDBWindow(self, filename, new_file):
		db_window = DBWindow(self, filename, new_file)
		self._db_windows.append(db_window)
		db_window.show()

		# Mac OS specific - required in addition to show()
		db_window.raise_()


class MainMenu(QtGui.QMenuBar):

	def __init__(self, app):
		QtGui.QMenuBar.__init__(self)

		self._app = app
		self._file_formats = config.lang.menu.file_masks_sack + " (*.sack);;" + \
			config.lang.menu.file_masks_all + " (*.*)"
		self._default_dir = '~'

		file = self.addMenu(config.lang.menu.file)

		file_new = QtGui.QAction(config.lang.menu.file_new, self)
		file_new.setShortcut(hotkeys.NEW)
		file_new.triggered.connect(self._showFileNewDialog)
		file.addAction(file_new)

		file_open = QtGui.QAction(config.lang.menu.file_open, self)
		file_open.setShortcut(hotkeys.OPEN)
		file_open.triggered.connect(self._showFileOpenDialog)
		file.addAction(file_open)

		edit = self.addMenu(config.lang.menu.edit)
		view = self.addMenu(config.lang.menu.view)
		tools = self.addMenu(config.lang.menu.tools)

	def _showFileNewDialog(self):
		self._showFileDialog(QtGui.QFileDialog.getSaveFileName,
			config.lang.menu.file_new, True)

	def _showFileOpenDialog(self):
		self._showFileDialog(QtGui.QFileDialog.getOpenFileName,
			config.lang.menu.file_open, False)

	def _showFileDialog(self, func, title, new_file):
		filename = func(self, title,
			self._default_dir, self._file_formats)
		if filename is not None:
			self._app.create_db_window.emit(filename, new_file)


app = Application()
exitcode = app.exec_()
sys.exit(exitcode)
