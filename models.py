from PyQt4 import QtCore, QtGui

from logging import warning
import re

import brain
import brain.op as op

import parser

class DatabaseCache:

	def __init__(self, file_name, new_file):
		self._conn = brain.connect(None, file_name,
			open_existing=(0 if new_file else 1))

	def __getattr__(self, name):
		return getattr(self._conn, name)


class Template:

	delimiter = '$'
	idpattern = r'[_a-z][_a-z0-9\.\-]*'

	pattern = r"""
	%(delim)s(?:
		(?P<escaped>%(delim)s) |   # Escape sequence of two delimiters
		(?P<named>%(id)s)      |   # delimiter and a Python identifier
		{(?P<braced>%(id)s)}   |   # delimiter and a braced identifier
		(?P<invalid>)              # Other ill-formed delimiter exprs
	)
	"""

	pattern = pattern % {
		'delim' : re.escape(delimiter),
		'id' : idpattern,
	}

	pattern = re.compile(pattern, re.IGNORECASE | re.VERBOSE)

	def __init__(self, template):
		self._template = template

	def getFieldNames(self):

		names = set()

		def convert(mo):
			named = mo.group('named') or mo.group('braced')
			if named is not None:
				names.add(named)

		self.pattern.sub(convert, self._template)
		return names

	def substitute(self, field_values):

		def convert(mo):
			named = mo.group('named')
			if named is not None:
				if named in field_values:
					return str(field_values[named])
				else:
					return self.delimiter + named

			braced = mo.group('braced')
			if braced is not None:
				if braced in field_values:
					return str(field_values[braced])
				else:
					return self.delimiter + '{' + braced + '}'

			if mo.group('escaped') is not None:
				return self.delimiter

			return self.delimiter + mo.group('invalid')

		return self.pattern.sub(convert, self._template)


class DatabaseModel(QtCore.QObject):

	def __init__(self, file_name, new_file):
		QtCore.QObject.__init__(self)
		self._db = DatabaseCache(file_name, new_file)

		self._findRoot()

	def _findRoot(self):

		# Search for root object - it is the starting point for
		# accessing the database
		result = self._db.search(['_Class'], op.EQ, None)

		if result == []:

			self._class_class = self._db.create({
				'Name': 'Metaclass',
				'TitleTemplate': '$Name',
				'FieldsOrder': ['Name', 'TitleTemplate', 'FieldsOrder']
			})
			self._db.modify(self._class_class, ['_Class'], self._class_class)

			self._tag_class = self._db.create({
				'Name': 'Tag class',
				'TitleTemplate': '$Name',
				'_Class': self._class_class,
				'FieldsOrder': ['Name', 'Description']
			})

			self._default_class = self._db.create({
				'Name': 'Default class',
				'TitleTemplate': '$Title',
				'_Class': self._class_class,
				'FieldsOrder': ['Title', 'Data']
			})

			self._root = self._db.create({
				'_Tags': [],
				'_Class': None,
				'BuiltinClasses': {
					'Class': self._class_class,
					'Tag': self._tag_class,
					'Default': self._default_class
				}
			})
		else:
			if len(result) > 1:
				warning("More than one root object found (" +
					repr(result) + "), using the first one")
			self._root = result[0]

			self._class_class = self._db.read(self._root, ['BuiltinClasses', 'Class'])
			self._tag_class = self._db.read(self._root, ['BuiltinClasses', 'Tag'])
			self._default_class = self._db.read(self._root, ['BuiltinClasses', 'Default'])

	def getTitle(self, id):
		obj_class = self._db.read(id, ['_Class'])
		title_template = self._db.read(obj_class, ['TitleTemplate'])
		template_obj = Template(title_template)

		field_names = template_obj.getFieldNames()
		field_values = {}
		for name in field_names:
			try:
				value = self._db.read(id, name.split('.'))
			except brain.LogicError:
				pass

			field_values[name] = value

		return template_obj.substitute(field_values)

	def __getattr__(self, name):
		return getattr(self._db, name)


class SearchResultsModel(QtCore.QAbstractListModel):

	def __init__(self, parent, db_model):
		QtCore.QAbstractListModel.__init__(self, parent)
		self._results = []
		self._db_model = db_model

	def rowCount(self, parent):
		return len(self._results)

	def data(self, index, role=QtCore.Qt.DisplayRole):
		if not index.isValid():
			return None
		elif index.row() < 0 or index.row() >= len(self._results):
			return None
		elif role == QtCore.Qt.DisplayRole:
			return self._db_model.getTitle(self._results[index.row()])

	def refreshResults(self, condition_str):
		self._condition_str = condition_str
		condition = parser.parseSearchCondition(condition_str)
		self._results = self._db_model.search(condition)
		self.reset()
