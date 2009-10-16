"""
Module for application-wide convenience functions and classes.
"""

from PyQt4 import QtGui, QtCore


class _GlobalsWrapper:
	"""
	Wrapper for some global variables and functions.
	This way they do not spoil the global namespace.
	"""

	@property
	def inst(self):
		"""Returns application instance"""
		return QtGui.QApplication.instance()

	@property
	def translate(self):
		"""
		Returns global application translation function.
		Using the same name in order to make lupdate happy.
		"""
		return QtGui.QApplication.translate

	@property
	def settings(self):
		"""
		Returns global application settings object.
		Creating the new one each time to avoid cases when several
		threads use the same object.
		"""
		return QtCore.QSettings()


class _DynamicTranslator:
	"""Wrapper for dynamically translated strings"""

	class Changer:
		"""Class which wraps a single dynamically translated string"""

		def __init__(self, changer_func):
			self._changer_func = changer_func
			self._text = None

		def translate(self, context, text):
			"""
			Remember translation identifiers.
			Using this name so that it is parsed by lupdate.
			"""
			self._context = context
			self._text = text

			# Since it is used instead of actually translating something,
			# we need to pass initial translation to changer function.
			self.refresh()

		def refresh(self):
			if self._text is None:
			# Custom string builder (has translation functions inside)
				self._changer_func()
			else:
			# Just set translated string
				self._changer_func(app.translate(self._context, self._text))

	def __init__(self):
		self._changers = []

	def add(self, changer_func):
		"""Register function, which takes new translation as an argument"""
		c = self.Changer(changer_func)
		self._changers.append(c)
		return c

	def refresh(self):
		"""Refresh all translations and pass them to corresponding changer functions"""
		for changer in self._changers:
			changer.refresh()


def dynamically_translated(qwidget_class):
	"""
	Decorator which adds dynamic translation ability to class.
	Class should be a ancestor of QWidget (because it introduces
	changeEvent() method).
	"""

	class DynTrClass(qwidget_class):
		"""Wrapper for given class with dynamic translation mix-in"""

		def __init__(self, *args, **kwds):
			self.__dyntr = _DynamicTranslator()
			qwidget_class.__init__(self, *args, **kwds)

		def dynTr(self, changer_func):
			"""
			Register dynamical translation; returns Changer object
			(for which either translate() or refresh() should be called
			to set the initial translation)
			"""
			return self.__dyntr.add(changer_func)

		def changeEvent(self, e):
			"""React on language change event - refresh all translations"""
			if e.type() == QtCore.QEvent.LanguageChange:
				self.__dyntr.refresh()
			qwidget_class.changeEvent(self, e)

	# Preserve initial name of the class, to help in debugging
	DynTrClass.__name__ = qwidget_class.__name__
	return DynTrClass

def findTranslationFiles():
	"""
	Find all valid translation files and return list of tuples
	(short language name, full language name, full path to file).
	"""

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

# holder of different application-global objects and functions
app = _GlobalsWrapper()
