

class ASTNode(object):
    @classmethod
    def ok(self):
        return True

    def eval(self):
        return self

    def __eq__(self,other):
        return repr(self) == repr(other)

    def __ne__(self,other):
        return not super(ASTNode,self).__eq__(other)


class Anonymous(ASTNode):
    def __init__(self,val):
        self.value = getattr(val,'value',val)
    def __repr__(self):
        return "Anonymous(%r)" % self.value

class Assignment(ASTNode): pass

class MixinDefinition(ASTNode):
    def __init__(self, name, params, rules, condition, variadic):
        self.name = name
        self.selectors = [Selector([Element(None,name)])]
        self.params = params
        self.condition = condition
        self.variadic = variadic
        self.arity = len(params)
        self.rules = rules
        self._lookups = {}
        self.required = 0
        # Count required parameters
        for p in params:
            if p.get('name') and not p.get('value') or \
                not p.get('name'):
                self.required += 1
        self.frames = []

    def __repr__(self):
        return "MixinDefinition(%r,%r,%r,%r,%r)" % (
                self.name, self.params, self.rules, self.condition, self.variadic
            )

class MixinCall(ASTNode):
    def __init__(self,elements, args, index, filename, important):
        self.elements = elements
        self.args = args
        self.index = index
        self.filename = filename
        self.important = important

    def __repr__(self):
        return "MixinCall(%r,%r,%r,%r,%r)" % (
                self.elements, self.args,
                self.index, self.filename, self.important
            )


class Combinator(ASTNode):
    def __init__(self,value):
        if value == ' ':
            self.value = ' '
        else:
            self.value = value.strip() if value else ""
    def __repr__(self):
        return "Combinator(%r)" % self.value


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


class Condition(ASTNode):
    def __init__(self, op, l, r, i, negate):
        self.op = op.strip()
        self.lvalue = l
        self.rvalue = r
        self.index = i
        self.negate = negate


class Dimension(ASTNode):
    def __init__(self, value, unit=None):
        self.value = float(value)
        self.unit = unit

    def __repr__(self):
        return "Dimension(%r,%r)" % (self.value,self.unit)

class Directive(ASTNode): pass

class Element(ASTNode):
    def __init__(self, combinator, value, index=None):
        self.combinator = combinator if isinstance(combinator,Combinator) \
            else Combinator(combinator)
        self.value = value
        self.index = index

    def __str__(self):
        return "<Element '%s %s'>" % (self.combinator.value, self.value)

    def __repr__(self):
        return "Element(%r, %r, %r)" % (
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
    def __repr__(self):
        return "Ratio(%r)" % self.value

class Rule(ASTNode):
    def __init__(self, name, value, important, memo):
        self.name = name
        self.value = value
        self.important = bool(important)
        self.memo = memo

    def __repr__(self):
        return "Rule(%r,%r,%r,%r)" % (
            self.name, self.value, self.important, self.memo
            )

class Ruleset(ASTNode):
    def __init__(self,selectors, rules, strict_import=False):
        self.selectors = selectors
        self.rules = rules
        self.strict_import = strict_import

    def __repr__(self):
        return "Ruleset(selectors=%r,rules=%r,strict_import=%r)" % (
            self.selectors, self.rules, self.strict_import
            )

class Selector(ASTNode):
    def __init__(self,elements):
        self.elements = elements

    def __str__(self):
        return " ".join([str(x) for x in self.elements])

    def __repr__(self):
        return "Selector(%r)" % self.elements


class URL(ASTNode):
    def __init__(self,value,paths):
        if hasattr(value,'data'):
            self.attrs = value
        else:
            self.value = value
            self.paths = paths
    def __repr__(self):
        return "URL(%r,%r)" % (self.value,self.paths)


class Value(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Value(%r)" % self.value

class Variable(ASTNode):
    def __init__(self, name, index, filename):
        self.name = name
        self.index = index
        self.filename = filename

    def __repr__(self):
        return "Variable(name=%r,index=%r,filename=%s)" % (
            self.name,self.index,self.filename)



