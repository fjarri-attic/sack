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



class _DynamicTranslator:

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


def dynamically_translated(qobj_class):

	class DynTrClass(qobj_class):

		def __init__(self, *args, **kwds):
			self.__dyntr = _DynamicTranslator()
			qobj_class.__init__(self, *args, **kwds)

		def dynTr(self, changer_func):
			return self.__dyntr.add(changer_func)

		def changeEvent(self, e):
			if e.type() == QtCore.QEvent.LanguageChange:
				self.__dyntr.refresh()
			qobj_class.changeEvent(self, e)

	DynTrClass.__name__ = qobj_class.__name__
	return DynTrClass


app = _GlobalsWrapper()
