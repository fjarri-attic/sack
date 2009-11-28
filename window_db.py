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

		self._initMenu()

		self._tabbar = QtGui.QTabWidget()

		self._tabbar.setTabsClosable(True)
		self._tabbar.setUsesScrollButtons(True)
		self._tabbar.setMovable(True)
		self._tabbar.tabCloseRequested.connect(self._closeTab)
		self.setCentralWidget(self._tabbar)

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

		self._createSearchTab()

		self.resize(app.settings.value('dbwindow/width'),
			app.settings.value('dbwindow/height'))

		self.dynTr(self._setStatusBar).refresh()

	def _setStatusBar(self):
		self.statusBar().showMessage(app.translate('DBWindow', 'Ready'))

	def _initMenu(self):
		menu = menus.WindowMenu()
		self.setMenuBar(menu)

		menu.searchTabRequested.connect(self._createSearchTab)

	def _createSearchTab(self):
		new_tab = window_search.SearchWindow(self, self._db_model)
		new_index = self._tabbar.addTab(new_tab, new_tab.title())
		new_tab.titleChanged.connect(lambda new_title: self._refreshTabTitle(new_tab, new_title))

	def _refreshTabTitle(self, tab, title):
		tab_index = self._tabbar.indexOf(tab)
		self._tabbar.setTabText(tab_index, title)

	def _closeTab(self, index):
		self._tabbar.removeTab(index)
