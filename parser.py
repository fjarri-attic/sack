import unittest
import re

import brain.op as op

from errors import *

class _Token:

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
	"""
	Transform a string with condition to a list of tokens:
	(string, starting position, ending position, quoted)
	'quoted' is a boolean parameter, equal to True if the source of the token
	was a quoted string.
	"""

	# states
	INTERMEDIATE = 0
	READING_OPERATOR = 1
	READING_QUOTED_STRING = 2
	READING_UNQUOTED_STRING = 3
	READING_ESCAPED_CHARACTER = 4

	# symbol groups
	PARENTHESES = ['(', ')']
	OPERATOR_SYMBOLS = ['=', '<', '>', '~']
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

	if len(buffer) > 0:
		if state == READING_QUOTED_STRING or \
				state == READING_ESCAPED_CHARACTER:
			token_type = _Token.QUOTED
		else:
			token_type = _Token.SIMPLE

		tokens.append(_Token(buffer, starting_position, position, token_type))

	return tokens

def _isFieldNameValid(name):
	"""Check if string is a valid field name"""

	# check symbol set
	if not re.search(r"^[\w\d_\-\.]+$", name):
		return False

	elements = name.split('.')

	for element in elements:

		if len(element) == 0:
			return False

		# first symbol must be a letter or an underscore
		if not element[0].isalpha() and element[0] != '_':
			return False

	return True

def _deduceValueType(value):
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
	result = []

	# states
	CONDITION_START = 0
	FIELD_NAME = 1
	OPERATOR = 2
	VALUE = 3

	state = CONDITION_START

	OPERATORS = {'==': op.EQ, '>': op.GT, '<': op.LT,
		'~': op.REGEXP, '<=': op.LTE, '>=': op.GTE,
		'and': op.AND, 'or': op.OR, 'not': op.NOT}

	i = position
	while i < len(tokens):
		if tokens[i].type == _Token.OPENING_PARENTHESIS:
			new_position, subcondition = _tokensToSearchCondition(tokens, i + 1)
			result.append(subcondition)
			i = new_position
		elif tokens[i].type == _Token.CLOSING_PARENTHESIS:
			return i + 1, result
		elif state == CONDITION_START:
			if tokens[i].type == _Token.SIMPLE and tokens[i].value.lower() == 'not':
				result.append(op.NOT)
				i += 1
			state = FIELD_NAME
		elif state == FIELD_NAME:
			if tokens[i].type != _Token.SIMPLE or not _isFieldNameValid(tokens[i].value):
				raise ParserError("Wrong field name", tokens[i].start, tokens[i].end)
			result.append(tokens[i].value.split('.'))
			i += 1
			state = OPERATOR
		elif state == OPERATOR:
			if tokens[i].type != _Token.SIMPLE or tokens[i].value.lower() not in OPERATORS:
				raise ParserError("Wrong operator", tokens[i].start, tokens[i].end)
			result.append(OPERATORS[tokens[i].value.lower()])
			i += 1
			state = VALUE
		elif state == VALUE:
			value = tokens[i].value

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

		for s in tests:
			self.assertEqual(tests[s], _tokenize(s))

	def testValidNames(self):
		tests = ['name', 'name1', 'name_.a1_name', '_n.am.e', '_-_']

		for test in tests:
			self.assertEqual(_isFieldNameValid(test), True)

	def testInvalidNames(self):
		tests = ['1name', 'name..name', '.name', 'name.1name','name$name']

		for test in tests:
			self.assertEqual(_isFieldNameValid(test), False)

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
		    "0xFAfb": b"\xfa\xfb", "123a": "123a"
		}

		for test in tests:
			self.assertEqual(tests[test], _deduceValueType(test))

	def testWrongValueFormat(self):
		tests = ["0x123", "0xABCDEFGH"]
		for test in tests:
			self.assertRaises(ValueError, _deduceValueType, test)

	def testConditionBuilder(self):
		tests = {
			r'elem==1': [['elem'], op.EQ, 1]
		}

		for test in tests:
			self.assertEqual(tests[test], parseSearchCondition(test))


def suite():
	res = unittest.TestSuite()
	res.addTests(unittest.TestLoader().loadTestsFromTestCase(ParserTests))
	return res

if __name__ == "__main__":
	unittest.TextTestRunner().run(suite())
