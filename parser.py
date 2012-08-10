import re
from tree import *


class ParseError(Exception):
    pass


class Parser(object):


    def __init__(self,input=None):
        self.i = 0
        #self.last_length = None
        self.input = self.input
        self.re_cache = {}
        self.strict_imports = False

    c = @property(lambda self: self.input[self.i])


    @property
    def parsers(self):
        return [x for x in dir(self) if x.startswith('parse_')]

    def _get_context(self):
        return self.i, self._, self._r

    def _rec(self, strn):
        try:
            return self._rec_cache[strn]
        except KeyError:
            self._rec_cache[strn] = re.compile(strn)
            return self._rec_cache[strn]

    def _r(self, tok_re):
        return self._(self._rec(strn))

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
            if isinstance(match,basestring)
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




    def parse_arguments(self):
        raise NotImplementedError


    def parse_assignment(self):
        _ = self._
        key = _(rec("^\w+(?=\s?=)/i"))
        if key and self._('='):
            value = _(self.entity)
            if value:
                return Assignment(key,value)

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

    def parse_comment(self):
        i,_,_r = self._get_context()
        if self.input[i] != '/': return
        if self.input[i + 1] == '/':
            return Comment(_r(r"^// .*"))


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
            e = _r("^[#.](?:[\w-]|\\(?:[A-Fa-f0-9]{1,6} ?|[^A-Fa-f0-9]))+")
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


    def parse_mixin_definition(self):
        """
        A Mixin definition, with a list of parameters
        >>> p = Parser(".rounded (@radius: 2px, @color) { .. }")
        >>> p.parse_mixin_definition()
        """
        i,_,_r = self._get_context()


    def parse_operand(self):



    def parse_primary(self):
        i,_,_r = self._get_context()
        root = []

        def push_into_root():
            node = _(self.parse_mixin_definition) or _(self.rule) or \
                _(self.ruleset) or _(self.parse_mixin_call) or _(self.comment)
            if not node:
                return None
            root.append(node)
            return True

        while push_into_root()
        return root


    def parse_property(self):
        name = self._r(r"^(\*?-?[_a-z0-9-]+)\s*:")
        return Property(name[1])

    def parse_ratio(self):
        if not Ratio.ok(self.input[self.i]):
            return
        value = _(Ratio.REGEX)
        if value:
            return Ratio(value[1])


    def parse_ruleset(self):
        """
        >>> p = Parser("div, .class, body > p {...}")
        >>> p.parse_ruleset()
        <Ruleset selectors=["div",".class","body > p"]>
        """
        selectors = []
        def push_selectors():
            s = self._(self.parse_selectors)
            selectors.append(s)
            self._(self.parse_comment)
            if not self._(","):
                return None
            self._(self.parse_comment)
            return s
        while push_selectors()
        if selectors:
            rules = self._(self.parse_block)
            return Ruleset(selectors, rules, self.strict_imports)


    def parse_rule(self):
        """
        >>> p = Parser("@foobar;")
        >>> p.parse_rule()
        <Rule value="@foobar">
        """
        i,_,_r = self._get_context()
        if self.c in ['.','#','&']: return

        name = _(self.parse_variable_def) or _(self.parse_property):
        if not name: 
            return

        if name[0] != '@':
            match = self.rec(r"^([^@+\/'"*`(;{}-]*);").match(self.input)
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


    def parse_url(self):
        _ = self._
        if self.input[i] != 'u' or not self._(URL.REGEX_START):
            return

        value = _(self.parse_quoted) or _(self.parse_variable) \
            or _(self.parse_data_uri) or _(URL.REGEX_UNQUOTED_URI) or ""

        self.expect(URL.REGEX_END)

        return URL() # TODO: Implement this


    def parse_variable_def(self):
        """
        Used by `parse_rule` to parse the rule's name

        >>> p = Parser("@fink: 2px")
        >>> p.parse_variable_def()
        "fink"
        """
        if self.c == "@":
            name = self._r("^(@[\w-]+)\s*:"):
            if name:
                return name[1]


    def parse_variable(self):
        """
        A Variable entity.
        
        Note that we use a different parser (`parse_variable_def`) to
        parse variable definiations

        >>> p = Parser("@fink")
        >>> p.parse_variable()
        <Variable name=fink
        """

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

