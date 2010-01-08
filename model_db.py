from PyQt4 import QtCore

import copy
from logging import warning

import brain
import brain.op as op

import parser

class DatabaseModel(QtCore.QObject):
	"""
	Wrapper for document database, implementing Sack DB structure
	(classes, tags, associations and so on)
	"""

	# Field names, used by system
	_CLASS = '_class' # contains ID of object's class
	_TAGS = '_tags' # contains list of IDs for object's tags
	_FIELDS_ORDER = 'fields_order' # contains structure with map keys order
	_ORDER = '_order' # contains list of keys for current level of structure
	_LIST = '_list' # map key which replaces list in current level of structure
	_NAME = 'name' # name field for different classes and objects
	_TITLE_TEMPLATE = 'title_template' # field which contains template for building title from object fields
	_DEFAULT_TEMPLATE = '${' + _NAME + '}' # default title template
	_DESCRIPTION = 'description' # field which contains object's description
	_BUILTIN_CLASSES = 'builtin_classes' # field which contains IDs of precreated classes
	_TITLE = 'title' # field of default class
	_DATA = 'data' # field of default class

	# Other string constants
	_METACLASS = 'Metaclass' # name of the metaclass
	_TAG_CLASS = 'Tag class' # name of tag class
	_DEFAULT_CLASS = 'Default class' # name of default class


	def __init__(self, file_name, new_file):
		QtCore.QObject.__init__(self)
		self._conn = brain.connect(None, file_name, open_existing=(0 if new_file else 1))
		self._db = brain.CachedConnection(self._conn)

		# for debug purposes
		objs = self._db.search()
		for obj in objs:
			self._db.delete(obj)

		self._metaclass_id = None
		self._default_class_id = None

		self._findRoot()
		self._testInit() # for debug purposes

	def _testInit(self):

		friends = self.createTag('Friends')
		coworkers = self.createTag('Coworkers')
		enemies = self.createTag('Enemies')

		human = self.createClass('Human', template='${name}',
			fields={
				'_order': ['name', 'age', 'friends'],
				'friends': {'_list': {'_order': ['name', 'age']}}
			})

		self.createObject({'name': 'Alex', 'age': 20}, tags=[friends], class_id=human)
		self.createObject({'name': 'Bob', 'age': 22, 'eyes': 'blue',
			'friends': [
				{'name': 'Alex', 'age': 20, 'eyes': 'gray'},
				{'name': 'Carl', 'age': 23}
			]}, tags=[coworkers, friends], class_id=human)
		self.createObject({'name': 'Carl'}, tags=[enemies], class_id=human)
		self.createObject({'name': 'Dick', 'age': 23}, tags=[coworkers, enemies], class_id=human)

	def getClass(self, obj_id):
		"""Get ID of object's class"""
		return self._db.read(obj_id, [self._CLASS])

	def setClass(self, obj_id, class_id):
		"""Set object's class"""
		self._db.modify(obj_id, [self._CLASS], class_id)

	def createObject(self, data, tags=None, class_id=None):
		"""Create new object with given class and tags"""
		to_add = copy.deepcopy(data)
		to_add[self._CLASS] = self._default_class_id if class_id is None else class_id
		to_add[self._TAGS] = [] if tags is None else tags
		return self._db.create(to_add)

	def createClass(self, name, template=None, fields=None):
		"""Create new class object"""
		to_add = {
			self._NAME: name,
			self._TITLE_TEMPLATE: self._DEFAULT_TEMPLATE if template is None else template
		}
		if fields is not None:
			to_add[self._FIELDS_ORDER] = fields
		return self.createObject(to_add, class_id=self._metaclass_id)

	def _createMetaclass(self):
		"""Create class object for classes"""
		self._metaclass_id = self.createClass(self._METACLASS,
			fields={self._ORDER: [self._NAME, self._TITLE_TEMPLATE, self._FIELDS_ORDER]})

		# class of the newly created metalcass object should point to self
		self.setClass(self._metaclass_id, self._metaclass_id)

	def createTag(self, name, description=None):
		"""Create tag object"""
		to_add = {self._NAME: name}
		if description is not None:
			to_add[self._DESCRIPTION] = description
		return self.createObject(to_add, class_id=self._tag_class)

	def _findRoot(self):
		"""
		Initialize database: find root object (or create the new one)
		and remember IDs of built-in classes
		"""

		# Search for root object - it is the starting point for
		# accessing the database
		result = self._db.search([self._CLASS], op.EQ, None)

		if result == []:

			self._createMetaclass()
			self._tag_class = self.createClass(self._TAG_CLASS,
				fields=[self._NAME, self._DESCRIPTION])
			self._default_class_id = self.createClass(self._DEFAULT_CLASS,
				template=self._DEFAULT_TEMPLATE,
				fields={self._ORDER: [self._TITLE, self._DATA]})

			self._root = self.createObject({
				self._BUILTIN_CLASSES: {
					'class': self._metaclass_id,
					'tag': self._tag_class,
					'default': self._default_class_id
				}
			})
			self.setClass(self._root, None)

		else:
			if len(result) > 1:
				warning("More than one root object found (" +
					repr(result) + "), using the first one")
			self._root = result[0]

			self._metaclass_id = self._db.read(self._root, [self._BUILTIN_CLASSES, 'class'])
			self._tag_class_id = self._db.read(self._root, [self._BUILTIN_CLASSES, 'tag'])
			self._default_class_id = self._db.read(self._root, [self._BUILTIN_CLASSES, 'default'])

	def getTitle(self, obj_id):
		"""Returns object title with necessary substitutions"""

		# get title template for object
		class_id = self.getClass(obj_id)
		title_template = self._db.read(class_id, [self._TITLE_TEMPLATE])

		# extract all field names mentioned in template
		template_obj = parser.TitleTemplate(title_template)
		field_names = template_obj.getFieldNames()

		# get values for field names
		field_values = {}
		for name in field_names:
			try:
				value = self._db.read(obj_id, name.split('.'))
			except brain.LogicError:
				pass

			field_values[name] = value

		return template_obj.substitute(field_values)

	def getTags(self, obj_ids):
		"""Returns list of tag objects for given list of objects"""
		tags_set = set()
		for obj_id in obj_ids:
			tag_ids = self.read(obj_id, [self._TAGS])
			for tag_id in tag_ids:
				tags_set.add(tag_id)
		return list(tags_set)

	def getFieldsOrder(self, obj_id, path):
		"""Returns fields order (list of fields) for given path of an object"""
		obj_class = self.getClass(obj_id)
		return self._db.read(obj_class, [self._FIELDS_ORDER] +
			[x if isinstance(x, str) and x != '' else '_list' for x in path] + [self._ORDER])

	def __getattr__(self, name):
		"""Passes all unknown method calls to DDB"""
		return getattr(self._db, name)
