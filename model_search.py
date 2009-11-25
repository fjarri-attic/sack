from PyQt4 import QtCore, QtGui

from logging import warning
import time

import parser


class ResultsModel(QtCore.QAbstractListModel):

	def __init__(self, parent, db_model):
		QtCore.QAbstractListModel.__init__(self, parent)
		self._results = []
		self._filtered_results = []
		self._db_model = db_model

	def rowCount(self, parent):
		return len(self._filtered_results)

	def data(self, index, role=QtCore.Qt.DisplayRole):
		if not index.isValid():
			return None
		elif index.row() < 0 or index.row() >= len(self._filtered_results):
			return None
		elif role == QtCore.Qt.DisplayRole:
			return self._db_model.getTitle(self._filtered_results[index.row()])

	searchFinished = QtCore.pyqtSignal(list, float)

	def refreshResults(self, condition_str):
		self._condition_str = condition_str
		condition = parser.parseSearchCondition(condition_str)

		time_start = time.time()
		self._results = self._db_model.search(condition)
		self._filtered_results = self._results
		search_time = time.time() - time_start

		self.reset()
		self.searchFinished.emit(self._results, search_time)

	resultsFiltered = QtCore.pyqtSignal(list)

	def filterResults(self, tags):
		self._filtered_results = []
		for obj in self._results:
			obj_tags = self._db_model.getTags([obj])

			match = True
			for tag in tags:
				if tag not in obj_tags:
					match = False
					break

			if match:
				self._filtered_results.append(obj)

		self.reset()
		self.resultsFiltered.emit(self._filtered_results)


class TagsListModel(QtCore.QAbstractListModel):

	def __init__(self, parent, db_model):
		QtCore.QAbstractListModel.__init__(self, parent)
		self._db_model = db_model
		self._objects = []
		self._tags = []
		self.selectionChanged.connect(self._processSelection)

	def rowCount(self, parent):
		return len(self._tags)

	def data(self, index, role=QtCore.Qt.DisplayRole):
		if not index.isValid():
			return None
		elif index.row() < 0 or index.row() >= len(self._tags):
			return None
		elif role == QtCore.Qt.DisplayRole:
			return self._db_model.getTitle(self._tags[index.row()])

	def refreshTags(self, objects, _):
		self._objects = objects
		self._tags = self._db_model.getTags(objects)
		self.reset()

	selectionChanged = QtCore.pyqtSignal(QtGui.QItemSelection, QtGui.QItemSelection)
	filterChanged = QtCore.pyqtSignal(list)

	def _processSelection(self, selected, unselected):
		tags = []
		for index in selected.indexes():
			tags.append(self._tags[index.row()])
		self.filterChanged.emit(tags)

def generateModels(parent, db_model):
	results_model = ResultsModel(parent, db_model)
	tags_model = TagsListModel(parent, db_model)
	tags_model.filterChanged.connect(results_model.filterResults)
	results_model.searchFinished.connect(tags_model.refreshTags)
	return results_model, tags_model
