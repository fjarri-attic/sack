from PyQt4 import QtCore, QtGui

import brain

import parser

class DatabaseCache:

	def __init__(self, file_name, new_file):
		self._conn = brain.connect(None, file_name,
			open_existing=(0 if new_file else 1))

	def __getattr__(self, name):
		return getattr(self._conn, name)


class DatabaseModel(QtCore.QObject):

	def __init__(self, file_name, new_file):
		QtCore.QObject.__init__(self)
		self._db = DatabaseCache(file_name, new_file)

	def getTitle(self, id):
		title = self._db.read(id, ['_Title'])

		# TODO: add expandable titles (like "%(Track)-%(Name)")

		return title

	def __getattr__(self, name):
		return getattr(self._db, name)


class SearchResultsModel(QtCore.QAbstractListModel):

	def __init__(self, parent, db_model):
		QtCore.QAbstractListModel.__init__(self, parent)
		self._results = []
		self._db_model = db_model

	def rowCount(self, parent):
		return len(self._results)

	def data(self, index, role=QtCore.Qt.DisplayRole):
		if not index.isValid():
			return None
		elif index.row() < 0 or index.row() >= len(self._results):
			return None
		elif role == QtCore.Qt.DisplayRole:
			return self._db_model.getTitle(self._results[index.row()])

	def refreshResults(self, condition_str):
		self._condition_str = condition_str
		condition = parser.parseSearchCondition(condition_str)
		self._results = self._db_model.search(condition)
		self.reset()
