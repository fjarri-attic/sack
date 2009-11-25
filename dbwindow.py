"""
Main class for Database window
"""

from PyQt4 import QtGui, QtCore

import brain

from globals import *
import model_db
import model_search


@dynamically_translated
class DBWindow(QtGui.QMainWindow):

	def __init__(self, file_name, new_file):
		QtGui.QMainWindow.__init__(self)

		self.setWindowTitle(file_name)
		self._db_model = model_db.DatabaseModel(file_name, new_file)

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

	def __init__(self, model, parent=None):
		QtGui.QListView.__init__(self, parent)
		self.setModel(model)


class TagsListView(QtGui.QListView):

	def __init__(self, model, parent=None):
		QtGui.QListView.__init__(self, parent)
		self.setModel(model)
		self.selectionModel().selectionChanged.connect(model.selectionChanged)
		self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)


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

	def onButtonClick(self, _):
		self.searchRequested.emit(self.toPlainText())

	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Return:
			self.searchRequested.emit(self.toPlainText())
		else:
			QtGui.QPlainTextEdit.keyPressEvent(self, event)


@dynamically_translated
class ResultsHeader(QtGui.QLabel):

	def __init__(self, results_model, parent=None):
		QtGui.QLabel.__init__(self, parent)
		self._search_performed = False
		self.dynTr(self._refreshHeader).refresh()
		results_model.searchFinished.connect(self._refreshSearchInfo)
		results_model.resultsFiltered.connect(self._refreshFilteringInfo)

	def _refreshSearchInfo(self, results, search_time):
		self._results_num = len(results)
		self._filtered_results_num = self._results_num
		self._search_performed = True
		self._results_filtered = False
		self._search_time = search_time
		self._refreshHeader()

	def _refreshFilteringInfo(self, filtered_results):
		self._filtered_results_num = len(filtered_results)
		if(self._filtered_results_num == self._results_num):
			self._results_filtered = False
		else:
			self._results_filtered = True
		self._refreshHeader()

	def _refreshHeader(self):
		results = app.translate("ResultsHeader", "results")
		sec = app.translate("ResultsHeader", "sec")
		total = app.translate("ResultsHeader", "total")

		if self._search_performed:
			self.setText(("{count} {results}" +
				(" ({tot_count} {total})" if self._results_filtered else "") +
				", {time} {sec}").format(
				count=self._filtered_results_num,
				results=results,
				time=self._search_time,
				sec=sec,
				tot_count=self._results_num,
				total=total))
		else:
			self.setText(app.translate("ResultsHeader", "Search results"))


@dynamically_translated
class SearchWindow(QtGui.QSplitter):

	def __init__(self, parent, db_model):
		QtGui.QSplitter.__init__(self, QtCore.Qt.Horizontal, parent)

		results_model, tags_model = model_search.generateModels(self, db_model)

		splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self)

		# create tags panel
		tags_widget = QtGui.QWidget(self)
		tags_header = QtGui.QLabel()
		self.dynTr(tags_header.setText).translate('SearchWindow', 'Tags')
		tags_view = TagsListView(tags_model)
		tags_layout = QtGui.QVBoxLayout()
		tags_layout.addWidget(tags_header)
		tags_layout.addWidget(tags_view)
		tags_widget.setLayout(tags_layout)

		self.addWidget(tags_widget)

		# create results view panel
		results_widget = QtGui.QWidget(self)
		results_header = ResultsHeader(results_model)
		results_view = SearchResultsView(results_model)
		results_layout = QtGui.QVBoxLayout()
		results_layout.addWidget(results_header)
		results_layout.addWidget(results_view)
		results_widget.setLayout(results_layout)

		# create search edit panel
		edit_widget = QtGui.QWidget(self)
		condition_edit = SearchConditionEdit()
		condition_edit.searchRequested.connect(results_model.refreshResults)
		search_button = QtGui.QPushButton(">>")
		search_button.clicked.connect(condition_edit.onButtonClick)
		edit_layout = QtGui.QHBoxLayout()
		edit_layout.addWidget(condition_edit)
		edit_layout.addWidget(search_button)
		edit_widget.setLayout(edit_layout)

		splitter.addWidget(results_widget)
		splitter.addWidget(edit_widget)

		self.addWidget(splitter)
