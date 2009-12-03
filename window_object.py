from PyQt4 import QtGui, QtCore

import brain

from globals import *


@dynamically_translated
class ObjectWindow(QtGui.QLabel):

	titleChanged = QtCore.pyqtSignal(str)

	def __init__(self, parent, db_model, obj_wrapper):
		QtGui.QLabel.__init__(self, parent)
		self.setText(db_model.getTitle(obj_wrapper.id))

	def title(self):
		return "Object View"
