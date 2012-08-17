

class ASTNode(object):
	@classmethod
	def ok(self):
		return True

	def eval(self):
		return self


class Anonymous(ASTNode): pass
class Assignment(ASTNode): pass

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
class Dimension(ASTNode):
	def __init__(self, value, unit=None):
		self.value = float(value)
		self.unit = unit

	def __repr__(self):
		return "Dimension(%r,%r)" % (self.value,self.unit)

class Directive(ASTNode): pass

class Element(ASTNode):
	def __init__(self, combinator, value, index):
		self.combinator = combinator if isinstance(combinator,Combinator) \
			else Combinator(combinator)
		self.value = value
		self.index = index

	def __str__(self):
		return "<Element '%s %s'>" % (self.combinator.value, self.value)

	def __repr__(self):
		return "Element(combinator=%r, value=%r, index=%r)" % (
			self.combinator, self.value, self.index)


class Expression(ASTNode):
	def __init__(self,value):
		self.value = value

	def __repr__(self):
		return "Expression(%r)" % self.value

class Import(ASTNode): pass
class Javascript(ASTNode): pass

class Keyword(ASTNode):
	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return "Keyword(%r)" % self.value

	def to_css(self):
		return this.value


class Media(ASTNode): pass
class Mixin(ASTNode): pass
class Operation(ASTNode):
	def __init__(self,op,operands):
		self.op = op
		self.operands = operands

	def __repr__(self):
		return "Operation(%r,%r)" % (self.op, self.operands)

class Paren(ASTNode):
	def __init__(self,node):
		self.value = node

class Quoted(ASTNode):
	def __init__(self, strn, content, escaped, i):
		self.escaped = escaped
		self.value = content or ''
		self.quote = srtn[0]
		self.index = i

	def __repr__(self):
		return "Quoted(%s,%s,%s,%s)" % (self.quote, self.value, self.escaped, self.index)


class Ratio(ASTNode):
	def __init__(self,value):
		self.value = value

class Rule(ASTNode):
	def __init__(self, name, value, important, memo):
		self.name = name
		self.value = value
		self.important = bool(important)
		self.memo = memo

	def __repr__(self):
		return "Rule(%r,%r,important=%r,memo=%r)" % (
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
		return " ".join([str(x) for x in self.elements])

	def __repr__(self):
		return "Selector(elements=%r)" % self.elements


class URL(ASTNode): pass


class Value(ASTNode):
	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return "Value(value=%r)" % self.value

class Variable(ASTNode):
	def __init__(self, name, index, filename):
		self.name = name
		self.index = index
		self.filename = filename

	def __repr__(self):
		return "Variable(name=%r,index=%r,filename=%s" % (
			self.name,self.index,self.filename)



