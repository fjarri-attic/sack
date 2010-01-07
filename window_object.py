from PyQt4 import QtGui, QtCore

import brain

from globals import *


class TreeItem(object):
	def __init__(self, name, value=None, parent=None):
		self.parent = parent
		self.name = name
		self.value = value
		self.children = []

	def appendChild(self, item):
		self.children.append(item)

	def child(self, row):
		return self.children[row]

	def childCount(self):
		return len(self.children)

	def columnCount(self):
		return 2

	def data(self, column):
		if column == 0:
			return self.name
		else:
			return self.value

	def row(self):
		if self.parent:
			return self.parent.children.index(self)
		else:
			return 0


def dataToItems(data, name):
	if isinstance(data, dict):
		root = TreeItem(name)
		for key in data:
			child = dataToItems(data[key], key)
			child.parent = root
			root.appendChild(child)
		return root
	elif isinstance(data, list):
		root = TreeItem(name)
		for index in range(len(data)):
			child = dataToItems(data[index], index)
			child.parent = root
			root.appendChild(child)
		return root
	else:
		return TreeItem(name, value=data)

class ObjectModel(QtCore.QAbstractItemModel):

	def __init__(self, db_model, obj_id):
		QtCore.QAbstractItemModel.__init__(self)
		self._db_model = db_model
		self._obj_id = obj_id

		tree = self._db_model.read(self._obj_id)
		self._tree = dataToItems(self._db_model, tree, None)

	def columnCount(self, parent):
		if parent.isValid():
			return parent.internalPointer().columnCount()
		else:
			return self._tree.columnCount()

	def data(self, index, role):
		if not index.isValid():
			return None

		if role != QtCore.Qt.DisplayRole:
			return None

		item = index.internalPointer()
		return item.data(index.column())

	def flags(self, index):
		if not index.isValid():
			return QtCore.Qt.NoItemFlags

		return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

	def headerData(self, section, orientation, role):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			return ['Name', 'Value'][section]

		return None

	def index(self, row, column, parent):
		if not self.hasIndex(row, column, parent):
			return QtCore.QModelIndex()

		if not parent.isValid():
			parentItem = self._tree
		else:
			parentItem = parent.internalPointer()

		childItem = parentItem.child(row)
		if childItem:
			return self.createIndex(row, column, childItem)
		else:
			return QtCore.QModelIndex()

	def parent(self, index):
		if not index.isValid():
			return QtCore.QModelIndex()

		childItem = index.internalPointer()
		parentItem = childItem.parent

		if parentItem == self._tree:
			return QtCore.QModelIndex()

		return self.createIndex(parentItem.row(), 0, parentItem)

	def rowCount(self, parent):
		if parent.column() > 0:
			return 0

		if not parent.isValid():
			parentItem = self._tree
		else:
			parentItem = parent.internalPointer()

		return parentItem.childCount()


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
