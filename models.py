from PyQt4 import QtCore, QtGui

import brain

class DatabaseCache:

	def __init__(self, file_name, new_file):
		self._conn = brain.connect(None, file_name,
			open_existing=(0 if new_file else 1))

	def __getattr__(self, name):
		return getattr(self._conn, name)


class DatabaseModel(QtCore.QAbstractItemModel):

	def __init__(self, file_name, new_file):
		QtCore.QAbstractItemModel.__init__(self)
		self._db = DatabaseCache(file_name, new_file)


class SearchResultsModel(QtCore.QAbstractListModel):

	def __init__(self, db_model):
		QtCore.QAbstractListModel.__init__(self)
		self._results = []

	def rowCount(self, parent):
		return len(self._results)
