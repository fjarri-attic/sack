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

		self.setCentralWidget(SearchWindow(self, self._db_model))

		self.resize(app.settings.value('dbwindow/width'),
			app.settings.value('dbwindow/height'))

		self.dynTr(self._setStatusBar).refresh()

	def _setStatusBar(self):
		self.statusBar().showMessage(app.translate('DBWindow', 'Ready'))


class SearchResultsView(QtGui.QListView):

	def __init__(self, parent=None):
		QtGui.QListView.__init__(self, parent)


class TagsListView(QtGui.QListView):

	def __init__(self, parent=None):
		QtGui.QListView.__init__(self, parent)


class SearchConditionEdit(QtGui.QPlainTextEdit):

	def __init__(self, parent=None):
		QtGui.QPlainTextEdit.__init__(self, parent)
		self.refreshSizeHints()

	def refreshSizeHints(self):
		metrics = self.fontMetrics()
		self.setBaseSize(0, metrics.height())
		self.setMinimumHeight(metrics.height())
		self.setSizeIncrement(0, metrics.height() + metrics.lineSpacing())

	searchRequested = QtCore.pyqtSignal(str)

	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Return:
			self.searchRequested.emit(self.toPlainText())
		else:
			QtGui.QPlainTextEdit.keyPressEvent(self, event)


@dynamically_translated
class SearchWindow(QtGui.QSplitter):

	def __init__(self, parent, db_model):
		QtGui.QSplitter.__init__(self, QtCore.Qt.Horizontal, parent)

		self._search_model = models.SearchResultsModel(self, db_model)
		tags_model = models.TagsListModel(self, db_model, self._search_model)

		splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self)

		# create tags panel
		tags_widget = QtGui.QWidget(self)
		tags_header = QtGui.QLabel()
		self.dynTr(tags_header.setText).translate('SearchWindow', 'Tags')
		tags_view = TagsListView()
		tags_view.setModel(tags_model)
		tags_layout = QtGui.QVBoxLayout()
		tags_layout.addWidget(tags_header)
		tags_layout.addWidget(tags_view)
		tags_widget.setLayout(tags_layout)

		self.addWidget(tags_widget)

		# create results view panel
		results_widget = QtGui.QWidget(self)
		self._results_header = QtGui.QLabel()
		self.dynTr(self._setResultsHeader).refresh()
		results_view = SearchResultsView()
		results_view.setModel(self._search_model)
		results_layout = QtGui.QVBoxLayout()
		results_layout.addWidget(self._results_header)
		results_layout.addWidget(results_view)
		results_widget.setLayout(results_layout)

		# create search edit panel
		edit_widget = QtGui.QWidget(self)
		condition_edit = SearchConditionEdit()
		condition_edit.searchRequested.connect(self._search_model.refreshResults)
		search_button = QtGui.QPushButton(">>")
		search_button.clicked.connect(self._search_model.refreshResults)
		edit_layout = QtGui.QHBoxLayout()
		edit_layout.addWidget(condition_edit)
		edit_layout.addWidget(search_button)
		edit_widget.setLayout(edit_layout)

		splitter.addWidget(results_widget)
		splitter.addWidget(edit_widget)

		self.addWidget(splitter)

	def _setResultsHeader(self):
		results = app.translate("SearchWindow", "results")
		sec = app.translate("SearchWindow", "sec")

		if self._search_model.searchPerformed():
			self._results_header.setText("{count} {results}, {time} {sec}".format(
				count=self._search_model.rowCount(),
				results=results,
				time=self._search_model.searchTime(),
				sec=sec))
		else:
			self._results_header.setText(app.translate("SearchWindow", "Search results"))
