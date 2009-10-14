from PyQt4 import QtGui, QtCore


class _GlobalsWrapper:

	@property
	def inst(self):
		return QtGui.QApplication.instance()

	@property
	def translate(self):
		return self.inst.translate

	@property
	def settings(self):
		return QtCore.QSettings()

app = _GlobalsWrapper()