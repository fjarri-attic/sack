from PyQt4 import QtGui, QtCore

import brain

from globals import *
import menus
import model_db
import window_search


@dynamically_translated
class DBWindow(QtGui.QMainWindow):

	def __init__(self, file_name, new_file):
		QtGui.QMainWindow.__init__(self)

		self.setWindowTitle(file_name)
		self._db_model = model_db.DatabaseModel(file_name, new_file)

		self.setMenuBar(menus.WindowMenu())

		tabbar = QtGui.QTabWidget()

		tabbar.setTabsClosable(True)
		tabbar.setUsesScrollButtons(True)
		tabbar.setMovable(True)

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

		#self.setCentralWidget(SearchWindow(self, self._db_model))
		tabbar.addTab(window_search.SearchWindow(self, self._db_model), 'first')
		self.setCentralWidget(tabbar)

		self.resize(app.settings.value('dbwindow/width'),
			app.settings.value('dbwindow/height'))

		self.dynTr(self._setStatusBar).refresh()

	def _setStatusBar(self):
		self.statusBar().showMessage(app.translate('DBWindow', 'Ready'))
