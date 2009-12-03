from PyQt4 import QtGui, QtCore

import brain

from globals import *


class ObjectModel(QtCore.QAbstractItemModel):

	def __init__(self, db_model, obj_id):
		QtCore.QAbstractItemModel.__init__(self)
		self._db_model = db_model
		self._obj_id = obj_id


class ObjectView(QtGui.QTreeView):

	def __init__(self, db_model, obj_id):
		QtGui.QTreeView.__init__(self)
		self.setModel(ObjectModel(db_model, obj_id))


@dynamically_translated
class ObjectWindow(QtGui.QSplitter):

	titleChanged = QtCore.pyqtSignal(str)

	def __init__(self, parent, db_model, obj_wrapper):
		QtGui.QSplitter.__init__(self, QtCore.Qt.Vertical, parent)
		self._db_model = db_model
		self._obj_id = obj_wrapper.id

		obj_view = ObjectView(self._db_model, self._obj_id)
		self.addWidget(obj_view)

	def title(self):
		return self._db_model.getTitle(self._obj_id)
