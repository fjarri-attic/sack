from PyQt4 import QtCore, QtGui

import brain

class DatabaseCache:

	def __init__(self, file_name, new_file):
		self._conn = brain.connect(None, file_name,
			open_existing=(0 if new_file else 1))

	def __getattr__(self, name):
		return getattr(self._conn, name)


class DatabaseModel(QtCore.QObject):

	def __init__(self, file_name, new_file):
		self._db = DatabaseCache(file_name, new_file)


class TagListModel(QtCore.QObject):

	def __init__(self, db_model):
		pass


class ShelfModel(QtCore.QObject):

	def __init__(self, db_model):
		pass


class SearchResultsModel(QtCore.QObject):

	def __init__(self, db_model):
		pass
