import re
from tree import *
import sys
import string

import pdb


digits = set(string.digits)

stack = []


def log(msg):
    #sys.stderr.write(msg)
    #sys.stderr.flush()
    print msg

def trace(func):
    def wrapped(self, *args, **kwargs):
        stack.append(" ")
        s = "".join(stack)
        log("%s%s \t\t\t\t%s: %r..." % (s,func.__name__ ,self.i,self.next[:10]))
        r = func(self, *args, **kwargs)
        if r:
            log((s + repr(r)))
        stack.pop()
        return r
    # So doctests still work...
    wrapped.__module__ = func.__module__
    wrapped.__doc__ = func.__doc__
    wrapped.__name__ = func.__name__
    return wrapped


class ParseError(Exception):
    pass



class ParseInput(str):
    def __getitem__(self,key):
        try:
            return super(ParseInput,self).__getitem__(key)
        except IndexError:
            return ''



class Parser(object):

    def __init__(self,input="",filename=None):
        self.i = 0
        #self.last_length = None
        self.input = ParseInput(input)
        self._re_cache = {}
        self.strict_imports = False
        self.filename = filename

        # TODO: Implement importing
        self.imports = {
            "paths": []
        }

    @property
    def c(self):
        try:
            return self.input[self.i]
        except IndexError:
            return ''
        #return self.input[self.i]

    @property
    def next(self):
        return self.input[self.i:]  # TODO: Will this be slow?

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
        r = self._rec(tok_re)
        x = self._(r)
        return x

    def _(self, tok):
        """
        Parse from a token, regex, or string. Move forward if found.
        If no match is found return `None`; if a match is found on a
        non-parenthetical regex then return a string of that expression;
        if a match is found on a parenthetical regex then return a tuple
        with the first element the string of that expression and 
        additional parenthetical matches as strings following.
        """

        #print "Using %s to check `%s`" % (tok,self.input[self.i:self.i+15])

        # Handle function
        if hasattr(tok,'__call__'):
            # 
            return tok()

        # Handle string
        elif isinstance(tok, basestring):
            match = tok if self.next[:len(tok)] == tok else None
            length = len(tok)
            #sync()

        # Handle regex
        elif hasattr(tok,'match'):
            #sync()
            match = tok.match(self.next)
            if match:
                length = len(match.group(0))
            else:
                return None

        # If we have a match, advance pointer and 
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
            return bool(tok.match(self.next))


    def expect(self,arg,msg=None):
        res = self._(arg)
        if res:
            return res
        else:
            msg = msg or \
                "expected '%s' got '%s'" % (arg,self.c) or \
                "unexpected token"
            raise ParseError(msg)


    @trace
    def parse_addition(self):
        i,_,_r = self._get_context()
        m = _(self.parse_multiplication)
        operation = None

        if m:
            while True:
                op = _r(r"^[-+]\s+") or \
                    (self.input[self.i-1] != ' ' and (_('+') or _('-')))
                if not op: break
                a = _(self.parse_multiplication)
                if not a: break
                operation = Operation(op, [operation or m, a])
            return operation or m


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
    def parse_conditions(self):
        i,_,_r = self._get_context()
        index = i
        a = _(self.parse_condition)

        if a:
            while True:
                if not _(","): break
                b = _(self.parse_condition)
                if not b: break
                condition = Condition("or",condition or a, b, index)
            return condition or a



    @trace
    def parse_condition(self):
        negate = False
        i,_,_r = self._get_context()
        index = i
        if _r(r"^not"):
            negate = True

        self.expect('(');
        a = _(self.parse_addition) or _(self.parse_keyword) or _(self.parse_quoted)
        if a:
            op = _r(r"^(?:>=|=<|[<=>])")
            if op:
                b = _(self.parse_addition) or _(self.parse_keyword) or _(self.parse_quoted)
                if b:
                    c = Condition(op, a, b, index, negate)
                else:
                    raise ParseError("Expected expression")
            else:
                c = Condition('=', a, Keyword('true'), index, negate)
            self.expect(")")
            return Condition("and", c, (self.parse_condition)) if _r(r"^and") else c


    @trace
    def parse_cssfunc_call(self):
        # TODO: Implement!
        return None


    @trace
    def parse_color(self):
        """
        >>> Parser('#fff').parse_color()
        Color((255, 255, 255),1.0)
        >>> Parser('#34DF02').parse_color()
        Color((52, 223, 2),1.0)
        """
        if not self.c == '#': return
        rgb = self._r(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})")
        if rgb:
            return Color(rgb[1])


    @trace        
    def parse_combinator(self):
        c = self.c
        if c in [">","+","~"]:
            self.i += 1
            while self.c == ' ':
                self.i += 1
            return Combinator(c)
        elif self.input[self.i - 1] == ' ':
            return Combinator(" ")
        else:
            return Combinator(None)

    @trace    
    def parse_comment(self):
        i,_,_r = self._get_context()
        if self.c != '/': return
        if self.input[i + 1] == '/':
            return Comment(_r(r"^// .*"), True)
        else:
            comment = _r(r"^\/\*(?:[^*]|\*+[^\/*])*\*+\/\n?")
            if comment:
                return Comment(comment)


    @trace
    def parse_dimension(self):
        """
        A number and a unit

        e.g.,
            0.5em
            95%

        >>> Parser("198.5px").parse_dimension()
        Dimension(198.5,'px')
        >>> Parser("-14em").parse_dimension()
        Dimension(-14.0,'em')
        """
        i,_,_r = self._get_context()

        #if self.input[i] in digits: return

        value = _r(r"^(-?\d*\.?\d+)(px|%|em|pc|ex|in|deg|s|ms|pt|cm|mm|rad|grad|turn|dpi|dpcm|dppx|rem|vw|vh|vmin|vm|ch)?")
        if value:
            return Dimension(value[1],value[2])


    @trace
    def parse_directive(self):
        # TODO: Implement!
        return None


    @trace
    def parse_entity(self):
        for func in [
                self.parse_literal, self.parse_variable,
                self.parse_url, self.parse_cssfunc_call, 
                self.parse_keyword, self.parse_javascript,
                self.parse_comment
            ]:
            result = self._(func)
            if result: return result


    @trace    
    def parse_expression(self):
        """Expressions either represent mathematical operations,
        or white-space delimited Entities.

        """
        entities = []
        while True:
            e = self._(self.parse_addition) or self._(self.parse_entity)
            if not e: break
            entities.append(e)
            self._r(r'\s*')
        if entities:
            return Expression(entities)


    @trace
    def parse_important(self):
        if self.c == '|':
            return self._r(r'^! *important')


    @trace
    def parse_javascript(self):
        # TODO: Implement
        return None


    @trace
    def parse_keyword(self):
        """

        """
        k = self._r(r"^[_A-Za-z-][_A-Za-z0-9-]*")
        if not k: return
        if k in Color.COLORS:
            return Color(Color.COLORS[k][1:])
        else:
            return Keyword(k)


    @trace
    def parse_literal(self):
        _ = self._
        return _(self.parse_ratio) or _(self.parse_dimension) or \
                _(self.parse_color) or _(self.parse_quoted)


    @trace    
    def parse_mixin_call(self):
        """
        A Mixin call, with an optional argument list

        e.g.,
            #mixins > .square(#fff);
            .rounded(4px, black);
            .button;
        

        >>> Parser('#mixins > .square(#fff);').parse_mixin_call()
        """
        i,_,_r = self._get_context()
        j = i
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
        if _("("):
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

        if elements and (_(";") or self.peek("}")):
            return MixinCall(elements, args, j, self.filename, important)



    @trace    
    def parse_mixin_definition(self):
        """

        A Mixin definition, with a list of parameters

        >>> p = Parser(".rounded (@radius: 2px) { width:@radius; }")
        >>> p.parse_mixin_definition()
        MixinDefinition('.rounded',[{'name': '@radius', 'value': Expression([Dimension(2.0,'px')])}],[Rule('width',Value([Expression([Variable(name='@radius',index=32,filename=None)])]),False,'')],None,False)
        >>> p = Parser(".rounded (@radius: 2px, @color) { color:@color; }")
        >>> p.parse_mixin_definition()
        MixinDefinition('.rounded',[{'name': '@radius', 'value': Expression([Dimension(2.0,'px')])}, {'name': '@color'}],[Rule('color',Value([Expression([Variable(name='@color',index=40,filename=None)])]),False,'')],None,False)
        """
        i,_,_r = self._get_context()
        variadic = False
        cond = None
        params = []
        if (self.c != '.' and self.c != '#') or \
            self.peek(self._rec(r"^[^{]*(;|})")):
            return

        match = _r(r"^([#.](?:[\w-]|\\(?:[A-Fa-f0-9]{1,6} ?|[^A-Fa-f0-9]))+)\s*\(")
        if match:
            name = match[1]


            while True:
                if self.c == '.' and _r(r"^\.{3}"):
                    # TODO: CKW: Huh? I dont understand variadic
                    variadic = True
                    break
                
                param = _(self.parse_variable) or _(self.parse_literal) or \
                            _(self.parse_keyword)
                if param:
                    if isinstance(param,Variable):
                        if _r(r':\s*'):
                            value = self.expect(self.parse_expression, 'expected expression')
                            params.append({"name": param.name, "value":value})
                        elif _(r"^\.{3}"):
                            params.append({"name":param.name, "value":value})
                        else:
                            params.append({"name":param.name})
                    else:
                        params.append({"value":param})

                else:
                    break


                if not _r(r",\s*"):
                    break

            _r(r"\)\s*")

            if _r(r"^when\s*"):
                cond = self.expect(self.parse_conditions, 'expected condition')

            ruleset = _(self.parse_block)

            if ruleset:
                return MixinDefinition(name,params,ruleset,cond,variadic)

    @trace
    def parse_multiplication(self):
        _ = self._
        m = _(self.parse_operand)
        operation = None
        while True:
            if self.peek(r"^\/\*"): break
            op = _('/') or _('*')
            if not op: break
            a = _(self.parse_operand)
            if not a: break
            operation = Operation(op, [operation or m, a])
        return operation or m


    @trace
    def parse_operand(self):
        _ = self._
        p = self.input[self.i+1]
        negate = None
        if self.c == '-' and (p == '@' or p == '('):
            negate = _('-')
        o = _(self.parse_sub) or _(self.parse_dimension) or \
            _(self.parse_color) or _(self.parse_variable) or \
            _(self.parse_cssfunc_call)
        return Operation('*', [Dimension(-1, o)]) if negate else o


    @trace
    def parse_primary(self):
        i,_,_r = self._get_context()
        root = []

        while True:
            node = _(self.parse_mixin_definition) or _(self.parse_rule) or \
                _(self.parse_ruleset) or _(self.parse_mixin_call) or \
                _(self.parse_comment) or _(self.parse_directive)
            
            if node:
                root.append(node)
            else:
                if not _r(r"^[\s\n]+"):
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
    def parse_quoted(self):
        """
        A string, which supports escaping " and '

        e.g.,
            "milky way" 'he\'s the one!'

        >>> Parser('"milky way"').parse_quoted()
        #Quoted("milky way")
        """
        i,_,_r = self._get_context()
        j = i
        e = None

        if self.input[j] == '~':
            j+=1
            e = True
        if self.input[j] != '"' and self.input[j] != "'": return

        if e: _('~')

        # TODO: Is this regex is broken?
        strn = _r(r'^"((?:[^"\\\r\n]|\\.)*)"|\'((?:[^\'\\\r\n]|\\.)*)\'')
        if strn:
            return Quoted(strn[0], strn[1] or strn[2], e)

    @trace
    def parse_ratio(self):
        """
        Parse a ratio. e.g.,

            `16/9`

        >>> Parser("16/9").parse_ratio()
        Ratio('16/9')
        """
        if self.c not in digits: return
        value = self._r(r"^(\d+\/\d+)")
        if value:
            return Ratio(value[1])

    @trace    
    def parse_ruleset(self):
        """

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
        A rule is either a variable definition or a property definition.

        >>> p = Parser("@foobar:18px;width:@foobar;")
        >>> p.parse_rule()
        Rule('@foobar',Value([Expression([Dimension(18.0,'px')])]),False,'')
        >>> p.parse_rule()
        Rule('width',Value([Expression([Variable(name='@foobar',index=19,filename=None)])]),False,'')
        """
        if self.c in ['.','#','&']: return
        i,_,_r = self._get_context()
        value = None

        name = _(self.parse_variable_def) or _(self.parse_property)
        if not name: 
            return

        _r(r"\s*")

        match = self._rec(r'^([^@+\/\'"*`(;{}-]*);').match(self.next)
        if name[0] != '@' and match:
            self.i += len(match.group(0)) - 1
            value = Anonymous(match.group(1))

        elif name == 'font':
            value = _(self.parse_font)
        else:
            value = _(self.parse_value)
        important = _(self.parse_important)

        if value and _(self.parse_end):
            return Rule(name, value, important, memo="")

    @trace    
    def parse_selector(self):
        """
        A CSS selector. e.g.,

            `.class > div + h1`
            `li a:hover`

        Selectors are made of one or more Elements.


        >>> Parser(".class > div + h1").parse_selector()
        Selector([Element(Combinator(''), '.class', 0), Element(Combinator('>'), 'div', 9), Element(Combinator('+'), 'h1', 15)])
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
    def parse_sub(self):
        _ = self._
        if not _("("): return
        e = _(self.parse_expression)
        if e and _(")"):
            return e


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
        j = self.i
        e = _r(r"^(?:\d+\.\d+|\d+)%") or \
            _r(r"^(?:[.#]?|:*)(?:[\w-]|\\(?:[A-Fa-f0-9]{1,6} ?|[^A-Fa-f0-9]))+") or \
            _("*") or _("&") or _(self.parse_attribute) or _r(r"^\([^)@]+\)")

        if not e:
            if _("("):
                v = _(self.parse_variable)
                if v and _(")"):
                    e = Paren(v)

        if e:
            # TODO: Confirm this is reasonable
            _r(r"\s*")
            return Element(c,e,j)


    @trace    
    def parse_end(self):
        """
        A Rule terminator. Note that we use `peek()` to check for '}',
        because the `block` rule will be expecting it, but we still need to make sure
        it's there, if ';' was ommitted.

        >>> bool(Parser(";").parse_end())
        True
        >>> bool(Parser("}").parse_end())
        True
        """
        return self._(";") or self.peek("}")


    @trace
    def parse_url(self):
        """
        >>> Parser("url(https://google.com/foobar.gif)").parse_url()
        URL(Anonymous('https://google.com/foobar.gif'),[])
        """
        _ = self._
        if self.c != 'u' or not self._r(r"^url\("):
            return

        value = _(self.parse_quoted) or _(self.parse_variable) \
            or _(self.parse_data_uri) or self._r(r"^[-\w%@$\/.&=:;#+?~]+") or ""
        self.expect(")")

        if hasattr(value,'value') or hasattr(value,'data') or isinstance(value, Variable):
            return URL(value)
        else:
            return URL(Anonymous(value), self.imports['paths'])


    @trace
    def parse_value(self):
        """A Value is a comma-delimited list of Expressions
        
            `font-family: Baskerville, Georgia, serif;`
        
        In a Rule, a Value represents everything after the `:`,
        and before the `;`.

        >>> p = Parser("Baskerville, Georgia, serif;")
        >>> p.parse_value()
        Value([Expression([Keyword('Baskerville')]), Expression([Keyword('Georgia')]), Expression([Keyword('serif')])])
        """
        expressions = []

        while True:
            e = self._(self.parse_expression)
            expressions.append(e)
            self._r(r"\s*")
            if not self._(","): break
            self._r(r"\s*")

        if len(expressions) > 0:
            return Value(expressions)

    @trace
    def parse_variable_def(self):
        """
        Used by `parse_rule` to parse the rule's name

        >>> p = Parser("@fink: 2px")
        >>> p.parse_variable_def()
        '@fink'
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
        Variable(name='@fink',index=0,filename=None)
        """
        j = self.i
        if self.c == '@':
            name = self._r(r'^@@?[\w-]+')
            if name:
                return Variable(name, j, self.filename)

    @trace        
    def parse_data_uri(self):
        if self._r(r"^data:"):
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
        self.input = ParseInput(strn.replace("\r\n","\n")) # Use 'normal' newlines
        self.root = Ruleset([], self._(self.parse_primary))


    def compile(self, strn):
        self.parse(strn)

        return ""


def compile(strn):
    return Parser().compile(strn)

