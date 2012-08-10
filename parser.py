import re
from tree import *
import sys

stack = []

def trace(func):
    def wrapped(*args,**kwargs):
        stack.append(" ")
        print ("".join(stack) + func.__name__)
        r = func(*args,**kwargs)
        if r:
            print ("".join(stack) + str(r))
        stack.pop()
        return r
    return wrapped


class ParseError(Exception):
    pass


class Parser(object):


    def __init__(self,input=None):
        self.i = 0
        #self.last_length = None
        self.input = input
        self._re_cache = {}
        self.strict_imports = False

    c = property(lambda self: self.input[self.i])


    @property
    def parsers(self):
        return [x for x in dir(self) if x.startswith('parse_')]

    def _get_context(self):
        return self.i, self._, self._r

    def _rec(self, strn):
        try:
            return self._re_cache[strn]
        except KeyError:
            self._re_cache[strn] = re.compile(strn)
            return self._re_cache[strn]

    def _r(self, tok_re):
        return self._(self._rec(tok_re))

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
            match = tok if self.input[self.i] == tok else None
            length = 1
            #sync()

        # Handle regex
        elif hasattr(tok,'match'):

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
            if isinstance(match,basestring):
                return match
            else:
                match_list = match.groups()
                if len(match_list) == 0:
                    return match.group(0)
                else:
                    return (match.group(0),) + match_list
                

    def peek(self,tok):
        if isinstance(tok, basestring):
            return self.c == tok
        else:
            return bool(tok.match(self.input))


    def expect(self,arg,msg=None):
        res = self._(arg)
        if res:
            return res
        else:
            msg = msg or \
                "expected '%s' got '%s'" % (arg,self.input[i]) or \
                "unexpected token"
            raise ParseError(msg)



    @trace    
    def parse_arguments(self):
        raise NotImplementedError

    @trace
    def parse_assignment(self):
        _ = self._
        key = _(rec("^\w+(?=\s?=)/i"))
        if key and self._('='):
            value = _(self.entity)
            if value:
                return Assignment(key,value)

    @trace        
    def parse_attribute(self):
        i,_,_r = self._get_context()
        attr = ''
        if not _("["): return

        key = _r(r"^[_A-Za-z0-9-]+") or _(self.parse_quoted)
        if key:
            op = _r(r"^[|~*$^]?=")
            val = _(self.parse_quoted)
            if op and val or _r(r"^[\w-]+"):
                attr = ''.join([key, op, val.to_css() if hasattr(val,'to_css') else val])
            else:
                attr = key

        if not _("["): return
        if attr: return "[" + attr + "]"

    @trace
    def parse_block(self):
        """
        The `block` rule is used by `ruleset` and `mixin.definition`.
        It's a wrapper around the `primary` rule, with added `{}`.

        >>> p = Parser("{ ... }")
        >>> p.parse_block()
        """
        _ = self._
        if _("{"):
            content = _(self.parse_primary)
            if content and _("}"):
                return content
    @trace        
    def parse_combinator(self):
        c = self.input[self.i]
        if c in [">","+","~"]:
            self.i += 1
            while self.input[self.i] == ' ':
                self.i += 1
            return Combinator(c)
        elif self.input[self.i - 1] == ' ':
            return Combinator(" ")
        else:
            return Combinator(None)

    @trace    
    def parse_comment(self):
        i,_,_r = self._get_context()
        if self.input[i] != '/': return
        if self.input[i + 1] == '/':
            return Comment(_r(r"^// .*"), True)
        else:
            comment = _(r"^\/\*(?:[^*]|\*+[^\/*])*\*+\/\n?")
            if comment:
                return Comment(comment)

    @trace    
    def parse_expression(self):
        """
        Expressions either represent mathematical operations,
        or white-space delimited Entities.

        >>> Parser("1px solid black").parse_expression()
        <Expression value="1px solid black">
        """
        entities = []
        while True:
            e = _(self.parse_addition) or _(parse_entity)
            entities.append(e)
        if entities:
            return Expression(entities)

    @trace
    def parse_important(self):
        if self.c == '|':
            return self._r(r'^! *important')

    @trace    
    def parse_mixin_call(self):
        """
        A Mixin call, with an optional argument list
        
        >>> p = Parser('''
            #mixins > .square(#fff);
            .rounded(4px, black);
            .button;
        ''')
        >>> p.parse_mixin_call()
        <MixinCall>
        """
        i,_,_r = self._get_context()
        elements = []
        args = []
        important = False

        # Parse the initial elements of the mixin call
        c = None
        while True:
            e = _r(r"^[#.](?:[\w-]|\(?:[A-Fa-f0-9]{1,6} ?|[^A-Fa-f0-9]\))+")
            if not e: break
            elements.append(Element(c,e,self.i))
            c = _(">")

        # Parse the arguments to the mixin call
        if self._("("):
            while True:
                arg = _(self.parse_expression)
                value = arg
                name = None

                # Variable
                if len(arg.value) == 1:
                    val = arg.value[0]
                    if isinstance(val, Variable):
                        if _(":"):
                            value = _(self.parse_expression)
                            if value:
                                name = val.name
                            else:
                                raise ParseError("Expected value") 

                args.append({"name":name,"value":value})
                if not _(","): break
            self.expect(")")

        # Parse the !important declaration
        if _(self.parse_important):
            important = True

        if elements and _(";") or self.peek("}"):
            return MixinCall(elements, args, index, self.filename, important)

    @trace    
    def parse_mixin_definition(self):
        """
        A Mixin definition, with a list of parameters
        >>> p = Parser(".rounded (@radius: 2px, @color) { .. }")
        >>> p.parse_mixin_definition()
        """
        i,_,_r = self._get_context()

    @trace
    def parse_operand(self):
        raise NotImplementedError

    @trace
    def parse_primary(self):
        i,_,_r = self._get_context()
        root = []

        while True:
            node = _(self.parse_mixin_definition) or _(self.parse_rule) or \
                _(self.parse_ruleset) or _(self.parse_mixin_call) or _(self.parse_comment)
            if node:
                root.append(node)
            else:
                break

        return root

    @trace
    def parse_property(self):
        """
        Parse a property. e.g.,

            `color:`


        """
        name = self._r(r"^(\*?-?[_a-z0-9-]+)\s*:")
        return name[1] if name else None

    @trace
    def parse_ratio(self):
        """
        Parse a ratio. e.g.,

            `16/9`

        """
        if not Ratio.ok(self.input[self.i]):
            return
        value = _(Ratio.REGEX)
        if value:
            return Ratio(value[1])

    @trace    
    def parse_ruleset(self):
        """
        >>> p = Parser("div, .class, body > p {...}")
        >>> p.parse_ruleset()
        <Ruleset selectors=["div",".class","body > p"]>
        """
        selectors = []

        while True:
            s = self._(self.parse_selector)
            if not s:
                break
            selectors.append(s)
            self._(self.parse_comment)
            if not self._(","): break
            self._(self.parse_comment)

        if selectors:
            rules = self._(self.parse_block)
            if rules:
                return Ruleset(selectors, rules, self.strict_imports)

    @trace    
    def parse_rule(self):
        """
        >>> p = Parser("@foobar;")
        >>> p.parse_rule()
        <Rule value="@foobar">
        """
        i,_,_r = self._get_context()
        if self.c in ['.','#','&']: return

        name = _(self.parse_variable_def) or _(self.parse_property)
        if not name: 
            return

        if name[0] != '@':
            match = self.rec(r'^([^@+\/\'"*`(;{}-]*);').match(self.input)
            if match:
                self.i += len(match.group(0))
                value = Anonymous(match.group(1))

        elif name == 'font':
            value = _(self.parse_font)
        else:
            value = _(self.parse_value)
        important = _(self.important)

        if value and _(this.end):
            return Rule(name, value, important, memo)

    @trace    
    def parse_selector(self):
        """
        A CSS selector. e.g.,

            `.class > div + h1`
            `li a:hover`

        Selectors are made of one or more Elements.
        """
        _ = self._
        elements = []

        if _("("):
            # CKW??? Why arent we using parse-element here
            sel = _(self.parse_entity)
            expect(")")
            return Selector([Element("",sel,i)])

        while True:
            e = _(self.parse_element)
            if not e: break
            elements.append(e)
            if self.input[self.i] in ["{","}",";",","]:
                break

        if elements:
            return Selector(elements)

    @trace    
    def parse_element(self):
        """
        Parse a selector element. e.g.,

            `div`
            `+ h1`
            `#socks`
            `input[type="text"]`

        """
        i,_,_r = self._get_context()
        c = _(self.parse_combinator)
        e = _r(r"^(?:\d+\.\d+|\d+)%") or \
            _r(r"^(?:[.#]?|:*)(?:[\w-]|\\(?:[A-Fa-f0-9]{1,6} ?|[^A-Fa-f0-9]))+") or \
            _("*") or _("&") or _(self.parse_attribute) or _r(r"^\([^)@]+\)")

        if not e:
            if _("("):
                v = _(self.parse_variable)
                if v and _(")"):
                    e = Paren(v)

        if e:
            return 
    @trace    
    def parse_end(self):
        """
        A Rule terminator. Note that we use `peek()` to check for '}',
        because the `block` rule will be expecting it, but we still need to make sure
        it's there, if ';' was ommitted.

        >>> p = Parser()
        >>> bool(p.parse_end(";"))
        True
        >>> bool(p.parse_end("}"))
        True
        """
        return self._(";") or self.peek("}")


    @trace
    def parse_url(self):
        _ = self._
        if self.input[i] != 'u' or not self._r(r"/^url\(/"):
            return

        value = _(self.parse_quoted) or _(self.parse_variable) \
            or _(self.parse_data_uri) or _r(r"^[-\w%@$\/.&=:;#+?~]+") or ""

        self.expect(")")

        return URL() # TODO: Implement this

    @trace
    def parse_variable_def(self):
        """
        Used by `parse_rule` to parse the rule's name

        >>> p = Parser("@fink: 2px")
        >>> p.parse_variable_def()
        "fink"
        """
        if self.c == "@":
            name = self._r(r"^(@[\w-]+)\s*:")
            if name:
                return name[1]

    @trace        
    def parse_variable(self):
        """
        A Variable entity.
        
        Note that we use a different parser (`parse_variable_def`) to
        parse variable definiations

        >>> p = Parser("@fink")
        >>> p.parse_variable()
        <Variable name=fink>
        """
        if self.c == '@':
            name = self._r(r'^@@?[\w-]+')
            if name:
                return Variable(name, index, self.filename)

    @trace        
    def parse_data_uri(self):
        raise NotImplementedError



    #entities = [('parse_'+p, getattr(Parser,'parse_'+p)) for p in \
    #    ['quoted','keyword','call','arguments','literal',
    #    'assignment','url','data_uri', 'variable','color','dimension',
    #    'ratio','javascript']]


    def parse(self, strn):
        """
        Parse an input string into an abstract syntax tree
        """
        self.i = 0 # Position of scanning in input reset to 0
        self.input = strn.replace("\r\n","\n").strip() # Use 'normal' newlines
        self.root = self._(self.parse_primary)

