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
			self._text = None

		def translate(self, context, text):
			self._context = context
			self._text = text
			self.refresh()

		def refresh(self):
			if self._text is None:
				self._changer_func()
			else:
				self._changer_func(app.translate(self._context, self._text))

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

def findTranslationFiles():

	# TODO: probably it is not the right place for this function,
	# but at the moment I cannot think of a better one

	translations_dir = QtCore.QDir(':/translations')
	file_names = translations_dir.entryList(['sack.*.qm'],
		QtCore.QDir.Files, QtCore.QDir.Name)

	translator = QtCore.QTranslator()

	translation_files = []
	for file_name in file_names:
		full_path = translations_dir.filePath(file_name)

		if not translator.load(full_path):
			QtCore.qWarning("Failed to load translation file " + full_path)
			continue

		full_name = translator.translate('Language', 'Full Name')
		if full_name is None:
			QtCore.qWarning("Translation file " + full_path +
				" does not contain full language name")
			continue

		short_name = translator.translate('Language', 'Short Name')
		if short_name is None:
			QtCore.qWarning("Translation file " + full_path +
				" does not contain short language name")
			continue

		translation_files.append((short_name, full_name, full_path))

	return translation_files

app = _GlobalsWrapper()
