from PyQt4 import QtGui, QtCore


class _GlobalsWrapper:

	@property
	def inst(self):
		return QtGui.QApplication.instance()

	@property
	def translate(self):
		return QtGui.QApplication.translate

	@property
	def settings(self):
		return QtCore.QSettings()



class DynamicTranslator:

	class Changer:
		def __init__(self, changer_func):
			self._changer_func = changer_func
			self._context = None
			self._text = None

		def translate(self, context, text):
			self._context = context
			self._text = text
			self.refresh()

		def refresh(self):
			if self._text is not None:
				self._changer_func(app.translate(self._context, self._text))
			else:
				self._changer_func()

	def __init__(self):
		self._changers = []

	def add(self, changer_func):
		c = self.Changer(changer_func)
		self._changers.append(c)
		return c

	def refresh(self):
		for changer in self._changers:
			changer.refresh()


app = _GlobalsWrapper()
