"""
Main class for Database window
"""

from PyQt4 import QtGui, QtCore

import brain

from globals import *
import models


@dynamically_translated
class DBWindow(QtGui.QMainWindow):

	def __init__(self, file_name, new_file):
		QtGui.QMainWindow.__init__(self)

		self.setWindowTitle(file_name)
		self._db_model = models.DatabaseModel(file_name, new_file)

		#tabbar = QtGui.QTabWidget()

		#tabbar.setTabsClosable(True)
		#tabbar.setUsesScrollButtons(True)
		#tabbar.setMovable(True)

		#tabbar.addTab(SearchWindow(), 'first')
		#tabbar.addTab(QtGui.QWidget(), 'second')

		#tags_dock = QtGui.QDockWidget()
		#self.dynTr(tags_dock.setWindowTitle).translate('DBWindow', 'Tags')

		#tags = QtGui.QListView()
		#tags_dock.setWidget(tags)

		#shelf_dock = QtGui.QDockWidget()
		#self.dynTr(shelf_dock.setWindowTitle).translate('DBWindow', 'Shelf')

		#shelf = QtGui.QListView()
		#shelf_dock.setWidget(shelf)

		#self.setCentralWidget(tabbar)
		#self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, tags_dock)
		#self.addDockWidget(QtCore.Qt.RightDockWidgetArea, shelf_dock)

		self.setCentralWidget(SearchWindow(self._db_model))

		self.resize(app.settings.value('dbwindow/width'),
			app.settings.value('dbwindow/height'))

		self.dynTr(self._setStatusBar).refresh()

	def _setStatusBar(self):
		self.statusBar().showMessage(app.translate('DBWindow', 'Ready'))


class SearchResultsView(QtGui.QListView):

	def __init__(self):
		QtGui.QListView.__init__(self)

class SearchWindow(QtGui.QSplitter):

	def __init__(self, db_model):
		QtGui.QSplitter.__init__(self, QtCore.Qt.Vertical)
		self.addWidget(SearchResultsView())
		self.addWidget(QtGui.QPlainTextEdit())

		self._db_model = db_model
