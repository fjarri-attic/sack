from PyQt4 import QtCore

import copy
from logging import warning

import brain
import brain.op as op

import parser

class DatabaseModel(QtCore.QObject):

	def __init__(self, file_name, new_file):
		QtCore.QObject.__init__(self)
		self._conn = brain.connect(None, file_name, open_existing=(0 if new_file else 1))
		self._db = brain.CachedConnection(self._conn)

		# for debug purposes
		objs = self._db.search()
		for obj in objs:
			self._db.delete(obj)

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

		self.createObject({'name': 'Alex', 'age': 20}, tags=[friends], cls=human)
		self.createObject({'name': 'Bob', 'age': 22, 'eyes': 'blue',
			'friends': [
				{'name': 'Alex', 'age': 20, 'eyes': 'gray'},
				{'name': 'Carl', 'age': 23}
			]}, tags=[coworkers, friends], cls=human)
		self.createObject({'name': 'Carl'}, tags=[enemies], cls=human)
		self.createObject({'name': 'Dick', 'age': 23}, tags=[coworkers, enemies], cls=human)

	def createObject(self, data, tags=None, cls=None):
		to_add = copy.deepcopy(data)

		to_add['_class'] = self._default_class if cls is None else cls
		to_add['_tags'] = [] if tags is None else tags

		return self._db.create(to_add)

	def createClass(self, name, template=None, fields=None):
		to_add = {'name': name, 'title_template': '${name}' if template is None else template}
		if fields is not None:
			to_add['fields_order'] = fields
		return self.createObject(to_add, cls=self._class_class)

	def _createMetaclass(self):
		self._default_class = None # stub for createObject()
		self._class_class = None # stub for createClass()
		self._class_class = self.createClass('Metaclass',
			fields={'_order': ['name', 'title_template', 'fields_order']})
		self.setClass(self._class_class, self._class_class)

	def setClass(self, obj, cls):
		self._db.modify(obj, ['_class'], cls)

	def createTag(self, name, description=None):
		to_add = {'name': name}
		if description is not None:
			to_add['description'] = description
		return self.createObject(to_add, cls=self._tag_class)

	def _findRoot(self):

		# Search for root object - it is the starting point for
		# accessing the database
		result = self._db.search(['_class'], op.EQ, None)

		if result == []:

			self._createMetaclass()
			self._tag_class = self.createClass('Tag class', fields=['name', 'description'])
			self._default_class = self.createClass('Default class',
				template='${title}', fields={'_order': ['title', 'data']})

			self._root = self.createObject({
				'builtin_classes': {
					'class': self._class_class,
					'tag': self._tag_class,
					'default': self._default_class
				}
			})
			self.setClass(self._root, None)

		else:
			if len(result) > 1:
				warning("More than one root object found (" +
					repr(result) + "), using the first one")
			self._root = result[0]

			self._class_class = self._db.read(self._root, ['builtin_classes', 'class'])
			self._tag_class = self._db.read(self._root, ['builtin_classes', 'tag'])
			self._default_class = self._db.read(self._root, ['builtin_classes', 'default'])

	def getClass(self, id):
		return self._db.read(id, ['_class'])

	def getTitle(self, id):
		obj_class = self.getClass(id)
		title_template = self._db.read(obj_class, ['title_template'])
		template_obj = parser.TitleTemplate(title_template)

		field_names = template_obj.getFieldNames()
		field_values = {}
		for name in field_names:
			try:
				value = self._db.read(id, name.split('.'))
			except brain.LogicError:
				pass

			field_values[name] = value

		return template_obj.substitute(field_values)

	def getTags(self, objects):
		tags_set = set()
		for object in objects:
			tags = self.read(object, ['_tags'])
			for tag in tags:
				tags_set.add(tag)
		return list(tags_set)

	def getFieldsOrder(self, id, path):
		obj_class = self.getClass(id)
		return self._db.read(obj_class, ['fields_order'] +
			[x if isinstance(x, str) and x != '' else '_list' for x in path] + ['_order'])

	def __getattr__(self, name):
		return getattr(self._db, name)
