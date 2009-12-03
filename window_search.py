from PyQt4 import QtGui, QtCore

import brain

from globals import *
import model_search


class SearchResultsView(QtGui.QListView):

	doubleClickedOnObject = QtCore.pyqtSignal(ObjectIdWrapper)

	def __init__(self, model, parent=None):
		QtGui.QListView.__init__(self, parent)
		self.setModel(model)
		self.doubleClicked.connect(self._processDoubleClick)

	def _processDoubleClick(self, index):
		self.doubleClickedOnObject.emit(ObjectIdWrapper(self.model().objectId(index)))


class TagsListView(QtGui.QListView):

	def __init__(self, model, parent=None):
		QtGui.QListView.__init__(self, parent)
		self.setModel(model)

		# FIXME: initiate connection from model, not from view
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

	titleChanged = QtCore.pyqtSignal()

	def __init__(self, results_model, parent=None):
		QtGui.QLabel.__init__(self, parent)
		self._search_performed = False
		self.dynTr(self._refreshTitle).refresh()
		results_model.searchFinished.connect(self._refreshSearchInfo)
		results_model.resultsFiltered.connect(self._refreshFilteringInfo)

	def _refreshSearchInfo(self, results, search_time):
		self._results_num = len(results)
		self._filtered_results_num = self._results_num
		self._search_performed = True
		self._results_filtered = False
		self._search_time = search_time
		self._refreshTitle()

	def _refreshFilteringInfo(self, filtered_results):
		self._filtered_results_num = len(filtered_results)
		if(self._filtered_results_num == self._results_num):
			self._results_filtered = False
		else:
			self._results_filtered = True
		self._refreshTitle()

	def shortTitle(self):
		if self._search_performed:
			return app.translate("ResultsHeader", "%n result(s)", None,
				QtCore.QCoreApplication.CodecForTr, self._results_num)
		else:
			return app.translate("ResultsHeader", "Search")

	def longTitle(self):
		if self._search_performed:
			results = app.translate("ResultsHeader", "%n result(s)", None,
				QtCore.QCoreApplication.CodecForTr, self._filtered_results_num)
			sec = app.translate("ResultsHeader", "sec")
			total = app.translate("ResultsHeader", "%n total", None,
				QtCore.QCoreApplication.CodecForTr, self._results_num)

			return ("{results}" +
				(" ({total})" if self._results_filtered else "") +
				", {time} {sec}").format(
				results=results,
				time=self._search_time,
				sec=sec,
				total=total)
		else:
			return app.translate("ResultsHeader", "Search results")

	def _refreshTitle(self):
		self.setText(self.longTitle())
		self.titleChanged.emit()


@dynamically_translated
class SearchWindow(QtGui.QSplitter):

	titleChanged = QtCore.pyqtSignal(str)
	objectWindowRequested = QtCore.pyqtSignal(ObjectIdWrapper)

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
		self._results_header = ResultsHeader(results_model)
		self._results_header.titleChanged.connect(
			lambda: self.titleChanged.emit(self.title()))
		results_view = SearchResultsView(results_model)
		results_view.doubleClickedOnObject.connect(self.objectWindowRequested)
		results_layout = QtGui.QVBoxLayout()
		results_layout.addWidget(self._results_header)
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

	def title(self):
		return self._results_header.shortTitle()
