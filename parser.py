import re
from tree import *

rec = re.compile

class ParseError(Exception):
	pass


class Parser(object):


	def __init__(self):
		self.i = 0
		#self.last_length = None
		self.input = None

	@property
	def parsers(self):
		return [x for x in dir(self) if x.startswith('parse_')]


	def _(self, tok):
		"""
		Parse from a token, regex, or string. Move forward if found.
		If no match is found return `None`; if a match is found on a
		non-parenthetical regex then return a string of that expression;
		if a match is found on a parenthetical regex then return a tuple
		with the first element the string of that expression and 
		additional parenthetical matches as strings following.
		"""

		# Handle function
		if hasattr(tok,'__call__'):
			# 
			return tok()

		# Handle string
		elif isinstance(tok, basestring):
			match = tok if self.input[i] == tok else None
			length = 1
			#sync()

		# Handle regex
		else:
			#sync()
			match = tok.match(self.input)
			if match:
				length = len(match.group(0))
			else:
				return None

		# If we have a match advance pointer and 
		# return match
		if match:
			self.i += length
			if isinstance(match,basestring)
				return match
			else:
				match_list = match.groups()
				if len(match_list) == 0:
					return match.group(0)
				else:
					return (match.group(0),) + match_list
				



	def expect(self,arg,msg=None):
		res = self._(arg)
		if res:
			return res
		else:
			msg = msg or \
				"expected '%s' got '%s'" % (arg,self.input[i]) or \
				"unexpected token"
			raise ParseError(msg)


	def parse_primary(self):
		_ = self._
		root = []

		def push_into_root():
			node = _(self.mixin.definition) or _(self.rule) or \
				_(self.ruleset) or _(self.mixin.call) or _(self.comment)
			if not node:
				return None
			root.append(node)
			return True

		while push_into_root()
		return root

	def parse_comment(self):
		if self.input[self.i] != '/': return
		if self.input[self.i + 1] == '/':
			return Comment(self._(r"^// .*"))

	def parse_arguments(self):
		raise NotImplementedError

	def parse_assignment(self):
		_ = self._
		key = _(Assignment.REGEX)
		if key and self._('='):
			value = _(self.entity)
			if value:
				return Assignment(key,value)

	RE_PROPERTY = re.compile()

	def parse_property(self):
		name = _(rec(r"^(\*?-?[_a-z0-9-]+)\s*:"))
		return 

	def parse_ratio(self):
		if not Ratio.ok(self.input[self.i]):
			return
		value = _(Ratio.REGEX)
		if value:
			return Ratio(value[1])

	RE_RULE = re.compile(r"^([^@+\/'"*`(;{}-]*);")

	def parse_rule(self):
		c = self.input[i]
		if c in ['.','#','&']: return
		_ = self._

		name = _(self.parse_variable) or _(self.parse_property):
		if not name: 
			return

		if name[0] != '@':
			match = 

		elif name == 'font':
			value = _(self.parse_font)
		else:
			value = _(self.parse_value)
		important = _(self.important)

		if value and _(this.end):
			return Rule(name, value, important, memo)

	def parse_url(self):
		_ = self._
		if self.input[i] != 'u' or not self._(URL.REGEX_START):
			return

		value = _(self.parse_quoted) or _(self.parse_variable) \
			or _(self.parse_data_uri) or _(URL.REGEX_UNQUOTED_URI) or ""

		self.expect(URL.REGEX_END)

		return URL() # TODO: Implement this

	def parse_data_uri(self):
		raise NotImplementedError



	entities = [('parse_'+p, getattr(Parser,'parse_'+p)) for p in \
		['quoted','keyword','call','arguments','literal',
		'assignment','url','data_uri', 'variable','color','dimension',
		'ratio','javascript']]


	def parse(strn):
		"""
		Parse an input string into an abstract syntax tree
		"""
		self.i = 0
		self.input = strn.replace()

