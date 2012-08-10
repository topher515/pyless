class ASTNode(object):
	@classmethod
	def ok(self):
		return True

	def eval(self):
		return self


class Anonymous(ASTNode): pass

class MixinCall(ASTNode): pass
class Combinator(ASTNode): pass
class Comment(ASTNode):
	def to_css(self):
		if self.silent:
			return ''
		else:
			return this.value

	def __init__(self,value,silent):
		self.value = value
		self.silent = silent


class Condition(ASTNode): pass
class Dimension(ASTNode): pass
class Directive(ASTNode): pass

class Element(ASTNode):
	def __init__(self,combinator, value, index):
		self.combinator = cominbinator if isinstance(combinator,Combinator) \
			else Combinator(combinator)
		self.value = value
		self.index = index

class Expression(ASTNode):
	def __init__(self,value):
		self.value = value


class Import(ASTNode): pass
class Javascript(ASTNode): pass

class Media(ASTNode): pass
class Mixin(ASTNode): pass
class Operation(ASTNode): pass
class Paren(ASTNode): pass
class Property(ASTNode): pass
class Quoted(ASTNode): pass
class Ratio(ASTNode):

	REGEX = re.compile(r"^(\d+\/\d+)")

	@classmethod
	def ok(cls,strn):
		try:
			int(strn[0])
			return True
		except ValueError:
			return False

class Rule(ASTNode): pass
class Ruleset(ASTNode):
	def __init__(self,selectors, rules, strict_import):
		self.selectors = selectors
	def __str__(self):
		return "<Ruleset selectors=%s>" % self.selectors
class Value(ASTNode): pass
class Variable(ASTNode): pass



class Keyword(ASTNode):

	def __init__(self,value):
		self.value = value

	def to_css(self):
		return this.value

	REGEX = re.compile(r"/^[_A-Za-z-][_A-Za-z0-9-]*/")


class Assignment(ASTNode): pass

class URL(ASTNode):

	REGEX_START = re.compile(r"/^url\(/")
	REGEX_UNQUOTED_URI = re.compile(r"^[-\w%@$\/.&=:;#+?~]+")
	REGEX_END = re.compile(r")")