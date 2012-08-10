

class ASTNode(object):
	@classmethod
	def ok(self):
		return True

	def eval(self):
		return self


class Anonymous(ASTNode): pass

class MixinCall(ASTNode): pass

class Combinator(ASTNode):
	def __init__(self,value):
		if value == ' ':
			self.value = ' '
		else:
			self.value = value.strip() if value else ""
	def __repr__(self):
		return "Combinator(value=%r)" % self.value

class Comment(ASTNode):
	def __init__(self,value,silent):
		self.value = value
		self.silent = silent

	def __repr__(self):
		return "Comment(value=%r,silent=%s)" % (self.value,self.silent)

	def to_css(self):
		if self.silent:
			return ''
		else:
			return this.value


class Condition(ASTNode): pass
class Dimension(ASTNode): pass
class Directive(ASTNode): pass

class Element(ASTNode):
	def __init__(self, combinator, value, index):
		self.combinator = cominbinator if isinstance(combinator,Combinator) \
			else Combinator(combinator)
		self.value = value
		self.index = index

	def __str__(self):
		return "<Element '%r%r'>" % (self.combinator, self.value)

	def __repr__(self):
		return "Element(combinator=%r, value=%r, index=%r)" % (
			self.combinator, self.value, self.index)


class Expression(ASTNode):
	def __init__(self,value):
		self.value = value


class Import(ASTNode): pass
class Javascript(ASTNode): pass

class Media(ASTNode): pass
class Mixin(ASTNode): pass
class Operation(ASTNode): pass
class Paren(ASTNode):
	def __init__(self,node):
		self.value = node

class Quoted(ASTNode): pass
class Ratio(ASTNode):

	@classmethod
	def ok(cls,strn):
		try:
			int(strn[0])
			return True
		except ValueError:
			return False

class Rule(ASTNode):
	def __init__(self, name, value, important, memo):
		self.name = name
		self.value = value
		self.important = important
		self.memo = memo

	def __repr__(self):
		return "Rule(name=%r,value=%r,important=%r,memo=%r)" % (
			self.name, self.value, self.important, self.memo
			)

class Ruleset(ASTNode):
	def __init__(self,selectors, rules, strict_import):
		self.selectors = selectors
		self.rules = rules
		self.strict_import = strict_import

	def __str__(self):
		return "<Ruleset selectors=%s>" % self.selectors

	def __repr__(self):
		return "Ruleset(selectors=%r,rules=%r,strict_import=%r" % (
			self.selectors, self.rules, self.strict_import
			)

class Selector(ASTNode):
	def __init__(self,elements):
		self.elements = elements

	def __str__(self):
		return " ".join(elements)

	def __repr__(self):
		return "Selector(elements=%r" % self.elements

class Value(ASTNode): pass
class Variable(ASTNode):
	def __init__(self, name, index, filename):
		self.name = name
		self.index = index
		self.filename = filename
	def __repr__(self):
		return "Variable(name=%r,index=%r,filename=%s" % (
			self.name,self.index,self.filename)



class Keyword(ASTNode):

	def __init__(self,value):
		self.value = value

	def to_css(self):
		return this.value


class Assignment(ASTNode): pass

class URL(ASTNode): pass