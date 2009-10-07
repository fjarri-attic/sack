import unittest
import re

import brain.op as op

from errors import *

class _Token:
	"""Search condition token"""

	# token types
	SIMPLE = 0
	QUOTED = 1
	OPENING_PARENTHESIS = 2
	CLOSING_PARENTHESIS = 3

	def __init__(self, value=None, start=0, end=0, type=None):
		self.value = value
		self.start = start
		self.end = end
		self.type = type

	def __eq__(self, other):
		return self.value == other.value and self.start == other.start and \
			self.end == other.end and self.type == other.type

def _tokenize(condition):
	"""Transform a string with condition to a list of _Token objects"""

	# states
	INTERMEDIATE = 0
	READING_OPERATOR = 1
	READING_QUOTED_STRING = 2
	READING_UNQUOTED_STRING = 3
	READING_ESCAPED_CHARACTER = 4

	# symbol groups
	PARENTHESES = ['(', ')']
	OPERATOR_SYMBOLS = ['=', '<', '>', '~', '!']
	WHITESPACE = [' ', '\t']

	tokens = []
	state = INTERMEDIATE
	buffer = ""
	characters = list(reversed(condition))

	position = -1 # current cursor position in source string
	starting_position = 0 # position of current buffer's starting character in source string

	while len(characters) > 0:
		c = characters.pop()
		position += 1

		if state == INTERMEDIATE:
			if c in PARENTHESES:
				token_type = _Token.OPENING_PARENTHESIS if c == '(' \
					else _Token.CLOSING_PARENTHESIS
				tokens.append(_Token(c, position, position, token_type))
			elif c in OPERATOR_SYMBOLS:
				state = READING_OPERATOR
				starting_position = position
				buffer += c
			elif c in WHITESPACE:
				continue
			else:
				if c == '"':
					state = READING_QUOTED_STRING
					starting_position = position
				else:
					state = READING_UNQUOTED_STRING
					starting_position = position
					buffer += c
		elif state == READING_OPERATOR:
			if c in OPERATOR_SYMBOLS:
				buffer += c
			else:
				# symbol does not belong to operator, return it back to pool
				characters.append(c)
				position -= 1
			tokens.append(_Token(buffer, starting_position,
				position, _Token.SIMPLE))
			buffer = ""
			state = INTERMEDIATE
		elif state == READING_QUOTED_STRING:
			if c == '\\':
				state = READING_ESCAPED_CHARACTER
			elif c == '"':
				tokens.append(_Token(buffer, starting_position,
					position, _Token.QUOTED))
				buffer = ""
				state = INTERMEDIATE
			else:
				buffer += c
		elif state == READING_UNQUOTED_STRING:
			if c in WHITESPACE + PARENTHESES + OPERATOR_SYMBOLS:
				# string ended, return this symbol back to pool
				characters.append(c)
				position -= 1
				tokens.append(_Token(buffer, starting_position,
					position, _Token.SIMPLE))
				buffer = ""
				state = INTERMEDIATE
			else:
				buffer += c
		elif state == READING_ESCAPED_CHARACTER:
			buffer += c
			state = READING_QUOTED_STRING

	# collect the last part of condition
	if len(buffer) > 0:
		if state == READING_QUOTED_STRING or \
				state == READING_ESCAPED_CHARACTER:
			raise ParserError("Quoted string finished unexpectedly",
				starting_position, position)
		else:
			token_type = _Token.SIMPLE

		tokens.append(_Token(buffer, starting_position, position, token_type))

	return tokens

def _getFieldNameList(name):
	"""
	Check field name validity and return name list if the name is valid,
	None otherwise.
	"""

	# check symbol set
	if not re.search(r"^[\w\d_\-\.]+$", name):
		return None

	elements = name.split('.')

	name_list = []
	for element in elements:

		if len(element) == 0:
			name_list.append(None)
		elif element[0].isdigit():
			try:
				name_list.append(int(element))
			except ValueError:
				return None
		elif element[0].isalpha() or element[0] == '_':
			name_list.append(element)
		else:
			return None

	return name_list

def _deduceValueType(value):
	"""
	Try to deduce value type from value token string. Return this value on success
	or raise ValueError on error.
	"""

	if value.lower() == 'null':
		return None

	if value.startswith("0x"):
		return bytes.fromhex(value[2:])

	# If value can be an int, float() will not raise
	# exception too
	result = value
	try:
		result = float(value)
		result = int(value)
	except:
		pass

	return result

def _tokensToSearchCondition(tokens, position=0):
	"""
	Transform list of tokens to nested lists of conditions for brain.search()
	The function is recursive, but the same token list is used throughout function calls.
	"""

	result = []

	# states
	CONDITION_START = 0
	FIELD_NAME = 1
	COMPARISON = 2
	VALUE = 3

	state = CONDITION_START

	COMPARISONS = {'==': op.EQ, '>': op.GT, '<': op.LT,
		'~': op.REGEXP, '<=': op.LTE, '>=': op.GTE}
	INVERSED_COMPARISONS = {'!=': op.EQ, '!~': op.REGEXP}
	OPERATORS = {'and': op.AND, 'or': op.OR, 'not': op.NOT}

	i = position
	while i < len(tokens):
		if tokens[i].type == _Token.OPENING_PARENTHESIS:
			new_position, subcondition = _tokensToSearchCondition(tokens, i + 1)
			result.append(subcondition)
			i = new_position
		elif tokens[i].type == _Token.CLOSING_PARENTHESIS:
			return i + 1, result
		elif state == CONDITION_START:
		# intermediate state; there can be either operator or field name here
		# if token looks like operator and the next token is not a comparison -
		# we consider this token to be an operator, otherwise it is a field name
			if tokens[i].type == _Token.SIMPLE and tokens[i].value.lower() in OPERATORS and \
				i < len(tokens) - 1 and tokens[i + 1].value not in COMPARISONS:
					result.append(OPERATORS[tokens[i].value.lower()])
					i += 1
			else:
				state = FIELD_NAME
		elif state == FIELD_NAME:
		# field name should be valid and token type should be simple
		# (no quoted value names)
			name_list = _getFieldNameList(tokens[i].value)
			if tokens[i].type != _Token.SIMPLE or name_list is None:
				raise ParserError("Wrong field name", tokens[i].start, tokens[i].end)
			result.append(name_list)
			i += 1
			state = COMPARISON
		elif state == COMPARISON:
			# no quoted comparisons
			if tokens[i].type != _Token.SIMPLE or (tokens[i].value not in COMPARISONS and \
					tokens[i].value not in INVERSED_COMPARISONS):
				raise ParserError("Wrong comparison operator", tokens[i].start, tokens[i].end)

			if tokens[i].value in COMPARISONS:
				result.append(COMPARISONS[tokens[i].value])
			else:
			# when processing inversed operator, we replace it by non-inverted one
			# and invert op.NOT before the condition
				if len(result) > 1 and result[-2] == op.NOT:
					del result[-2]
				else:
					result.insert(-2, op.NOT)

				result.append(INVERSED_COMPARISONS[tokens[i].value])
			i += 1
			state = VALUE
		elif state == VALUE:
			value = tokens[i].value

			# if the token is simple, value type should be deduced
			# if not, it is definitely a string
			if tokens[i].type == _Token.SIMPLE:
				try:
					value = _deduceValueType(value)
				except ValueError:
					raise ParserError("Unknown value format",
						tokens[i].start, tokens[i].end)

			result.append(value)
			i += 1
			state = CONDITION_START

	return result, i

def _checkParentheses(tokens):
	"""
	Check token list for non-matching parenthesis (this will simplify
	further transformation to search condition)
	"""

	parentheses_counter = 0
	for token in tokens:
		if token.type == _Token.OPENING_PARENTHESIS:
			parentheses_counter += 1
		elif token.type == _Token.CLOSING_PARENTHESIS:
			parentheses_counter -= 1

		if parentheses_counter < 0:
			raise ParserError("Unmatching closing parenthesis", token.start, token.end)

	if parentheses_counter > 0:
		raise ParserError("Missing closing parenthesis", tokens[-1].start, tokens[-1].end)

def parseSearchCondition(condition):
	"""Transform string to search condition"""

	tokens = _tokenize(condition)

	if len(tokens) == 0:
		return None

	_checkParentheses(tokens)

	result, unused = _tokensToSearchCondition(tokens)
	return result


class ParserTests(unittest.TestCase):

	def testTokenizer(self):
		tests = {
			r'elem==1': [_Token('elem', 0, 3, _Token.SIMPLE),
				_Token('==', 4, 5, _Token.SIMPLE),
				_Token('1', 6, 6, _Token.SIMPLE)],
			r'elem=="value"': [_Token('elem', 0, 3, _Token.SIMPLE),
				_Token('==', 4, 5, _Token.SIMPLE),
				_Token('value', 6, 12, _Token.QUOTED)],
			r'elem <= "va\"\\lue"': [_Token('elem', 0, 3, _Token.SIMPLE),
				_Token('<=', 5, 6, _Token.SIMPLE),
				_Token('va"\\lue', 8, 18, _Token.QUOTED)],
			r'(elem ~"va lue") && (elem2 >= 3.456)':
				[_Token('(', 0, 0, _Token.OPENING_PARENTHESIS),
				_Token('elem', 1, 4, _Token.SIMPLE),
				_Token('~', 6, 6, _Token.SIMPLE),
				_Token('va lue', 7, 14, _Token.QUOTED),
				_Token(')', 15, 15, _Token.CLOSING_PARENTHESIS),
				_Token('&&', 17, 18, False),
				_Token('(', 20, 20, _Token.OPENING_PARENTHESIS),
				_Token('elem2', 21, 25, _Token.SIMPLE),
				_Token('>=', 27, 28, _Token.SIMPLE),
				_Token('3.456', 30, 34, _Token.SIMPLE),
				_Token(')', 35, 35, _Token.CLOSING_PARENTHESIS)]
		}

		for test in tests:
			self.assertEqual(tests[test], _tokenize(test))

	def testTokenizerErrors(self):
		tests = [r'elem=="aaa', r'elem=="aaa\\']

		for test in tests:
			self.assertRaises(ParserError, _tokenize, test)

	def testValidNames(self):
		tests = {'name': ['name'],
			'name1': ['name1'],
			'name_.a1_name': ['name_', 'a1_name'],
			'_n.am.e': ['_n', 'am', 'e'],
			'_-_': ['_-_'],
			'name.2.name2': ['name', 2, 'name2'],
			'name..name': ['name', None, 'name'],
			'...': [None, None, None, None]}

		for test in tests:
			self.assertEqual(_getFieldNameList(test), tests[test])

	def testInvalidNames(self):
		tests = ['1name', 'name.2name', '#name', 'name$name', 'name.-name']

		for test in tests:
			self.assertEqual(_getFieldNameList(test), None)

	def testWrongParentheses(self):
		opening = _Token(type=_Token.OPENING_PARENTHESIS)
		closing = _Token(type=_Token.CLOSING_PARENTHESIS)
		tests = [
		    [opening, closing, opening, opening, closing],
		    [opening, closing, opening, closing, closing]
		]

		for test in tests:
			self.assertRaises(ParserError, _checkParentheses, test)

	def testValueTypeDeduction(self):
		tests = {
			"1": 1, "-2": -2, "3.0": 3.0, "-5.678": -5.678,
			"0xFAfb": b"\xfa\xfb", "123a": "123a",
			"NULL": None, "null": None
		}

		for test in tests:
			self.assertEqual(tests[test], _deduceValueType(test))

	def testWrongValueFormat(self):
		tests = ["0x123", "0xABCDEFGH"]
		for test in tests:
			self.assertRaises(ValueError, _deduceValueType, test)

	def testConditionBuilder(self):
		"""Not exactly a unit test, but when it looks like this it is way easier to debug"""
		tests = {
			r'elem==1': [['elem'], op.EQ, 1],
			r'(elem==2)': [[['elem'], op.EQ, 2]],
			r'elem > 1 and elem2 < 5.54':
				[['elem'], op.GT, 1, op.AND, ['elem2'], op.LT, 5.54],
			r'not elem <= "aaa" and not elem2 ~ "zzz"':
				[op.NOT, ['elem'], op.LTE, "aaa", op.AND, op.NOT,
				['elem2'], op.REGEXP, "zzz"],
			r'not (elem.abc.def == 0xabcd) and (elem2 < 3)':
				[op.NOT, [['elem', 'abc', 'def'], op.EQ, b"\xab\xcd"],
				op.AND, [['elem2'], op.LT, 3]],
			r'not (elem.2 != 4) or (not key.2.3 != 1) and not key.1 !~ "abc"':
				[op.NOT, [op.NOT, ['elem', 2], op.EQ, 4], op.OR,
				[['key', 2, 3], op.EQ, 1], op.AND,
				['key', 1], op.REGEXP, 'abc'],
			r'and == 2': [['and'], op.EQ, 2],
			r'': None
		}

		for test in tests:
			self.assertEqual(tests[test], parseSearchCondition(test))

	def testConditionBuilderErrors(self):
		"""Not exactly a unit test, but when it looks like this it is way easier to debug"""
		tests = [r'2elem==1', r'elem=<3', r'elem == 0xXY']

		for test in tests:
			self.assertRaises(ParserError, parseSearchCondition, test)


def suite():
	res = unittest.TestSuite()
	res.addTests(unittest.TestLoader().loadTestsFromTestCase(ParserTests))
	return res

if __name__ == "__main__":
	unittest.TextTestRunner().run(suite())
