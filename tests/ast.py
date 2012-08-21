import unittest

from parser import Parser
from tree import *

class TestAST(unittest.TestCase):

    def setUp(self):
        self.p = Parser()

    def _test_tree1(self):
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


    def test_tree2(self):
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


