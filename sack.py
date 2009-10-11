import sys
from PyQt4 import QtGui, QtCore

import brain

from dbwindow import DBWindow
import config

class Application(QtGui.QApplication):

	def __init__(self):
		QtGui.QApplication.__init__(self, sys.argv)

		config.init()

		self._main_menu = MainMenu(self)
		self._db_windows = []

	def registerDBWindow(self, window):
		self._db_windows.append(window)

class MainMenu(QtGui.QMenuBar):

	def __init__(self, app):
		QtGui.QMenuBar.__init__(self)
		self._app = app

		file = self.addMenu(config.lang.menu.file)

		file_new = QtGui.QAction(config.lang.menu.file_new, self)
		file_new.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_N)
		file.addAction(file_new)
		self.connect(file_new, QtCore.SIGNAL('triggered()'), self.showFileNewDialog)

		edit = self.addMenu(config.lang.menu.edit)
		view = self.addMenu(config.lang.menu.view)
		tools = self.addMenu(config.lang.menu.tools)

	def showFileNewDialog(self):
		filename = QtGui.QFileDialog.getSaveFileName(self, 'New Sack', '~',
			config.lang.menu.file_masks_sack + " (*.sack);;" +
			config.lang.menu.file_masks_all + " (*.*)")
		if filename is not None:
			db_window = DBWindow(filename, True)
			self._app.registerDBWindow(db_window)

app = Application()
sys.exit(app.exec_())
