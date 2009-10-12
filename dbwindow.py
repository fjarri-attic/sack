from PyQt4 import QtGui, QtCore

import brain

import config

class DBWindow(QtGui.QMainWindow):
	def __init__(self, app_obj, file_name, new_file):
		QtGui.QMainWindow.__init__(self)

		self._app_obj = app_obj
		self.setWindowTitle(file_name)
		self._connection = brain.connect(None, file_name,
			open_existing=(0 if new_file else 1))

		tabbar = QtGui.QTabWidget()
		tabbar.addTab(QtGui.QWidget(), 'first')
		tabbar.addTab(QtGui.QWidget(), 'second')

		tags_dock = QtGui.QDockWidget('tags')
		shelf_dock = QtGui.QDockWidget('shelf')

		self.setCentralWidget(tabbar)
		self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, tags_dock)
		self.addDockWidget(QtCore.Qt.RightDockWidgetArea, shelf_dock)

		self.resize(int(config.options.geometry.db_window_width),
			int(config.options.geometry.db_window_height))

		self.statusBar().showMessage('Ready')
