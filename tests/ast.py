import unittest

from parser import Parser
from tree import *

class TestAST(unittest.TestCase):

    def setUp(self):
        self.p = Parser()

    def test_simple(self):
        self.p.parse("""

            //   LESS

            @color: #01926F;

            #header {
              color: @color;
            }
            h2 {
              color: @color;
            }
            """)

        r = Ruleset(selectors=[],rules=[
            Comment(value='//   LESS',silent=True), 
            Rule('@color',Value(value=[Expression([Color((1, 146, 111),1.0)])]),important=False,memo=''), 
            Ruleset(selectors=[Selector(elements=[
                    Element(combinator=Combinator(value=' '), value='#header', index=67)
                ])],
                rules=[Rule('color',Value(value=[Expression([Variable(name='@color',index=98,filename=None)])]),important=False,memo='')],
                strict_import=False),
            Ruleset(selectors=[Selector(elements=[
                    Element(combinator=Combinator(value=' '), value='h2', index=132)
                ])],
                rules=[Rule('color',Value(value=[Expression([Variable(name='@color',index=158,filename=None)])]),important=False,memo='')],
                strict_import=False)],
            strict_import=False)
        
        self.assertEquals(r, self.p.root)


    def test_mixins(self):
        self.p.parse("""
            .rounded-corners (@radius: 5px) {
              border-radius: @radius;
              -webkit-border-radius: @radius;
              -moz-border-radius: @radius;
            }

            #header {
              .rounded-corners;
            }
            #footer {
              .rounded-corners(10px);
            }
            """)


    def test_nested_rules(self):
        self.p.parse("""
            #header {
              h1 {
                font-size: 26px;
                font-weight: bold;
              }
              p { font-size: 12px;
                a { text-decoration: none;
                  &:hover { border-width: 1px }
                }
              }
            }
            """)

    def test_functions_and_operations(self):
        self.p.parse("""
            @the-border: 1px;
            @base-color: #111;
            @red:        #842210;

            #header {
              color: @base-color * 3;
              border-left: @the-border;
              border-right: @the-border * 2;
            }
            #footer { 
              color: @base-color + #003300;
              border-color: desaturate(@red, 10%);
            }
            """)


    def test_mixin_definition(self):
        self.p.parse("""
            @base: #f938ab;

            .box-shadow(@style, @c) {
              box-shadow:         @style @c;
              -webkit-box-shadow: @style @c;
              -moz-box-shadow:    @style @c;
            }
            .box { 
              color: saturate(@base, 5%);
              border-color: lighten(@base, 30%);
              div { .box-shadow(0 0 5px, 30%) }
            }
            """)
        r = Ruleset(selectors=[],rules=[Rule('@base',Value([Expression([Color((249, 56, 171),1.0)])]),False,''), MixinDefinition('.box-shadow',[{'name': '@style'}, {'name': '@c'}],[Rule('box-shadow',Value([Expression([Variable(name='@style',index=102,filename=None), Variable(name='@c',index=109,filename=None)])]),False,''), Rule('-webkit-box-shadow',Value([Expression([Variable(name='@style',index=147,filename=None), Variable(name='@c',index=154,filename=None)])]),False,''), Rule('-moz-box-shadow',Value([Expression([Variable(name='@style',index=192,filename=None), Variable(name='@c',index=199,filename=None)])]),False,'')],None,False)],strict_import=False)
        self.assertEquals(r,self.p.root)


    def _test_mixin_definition_conditions(self):

        self.p.parse("""
            @base: #f938ab;

            .box-shadow(@style, @c) when (iscolor(@c)) {
              box-shadow:         @style @c;
              -webkit-box-shadow: @style @c;
              -moz-box-shadow:    @style @c;
            }
            .box-shadow(@style, @alpha: 50%) when (isnumber(@alpha)) {
              .box-shadow(@style, rgba(0, 0, 0, @alpha));
            }
            .box { 
              color: saturate(@base, 5%);
              border-color: lighten(@base, 30%);
              div { .box-shadow(0 0 5px, 30%) }
            }
            """)


