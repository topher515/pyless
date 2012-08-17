import unittest

from parser import Parser

class TestAST(unittest.TestCase):

    def setUp(self):
        self.p = Parser()

    def test_tree(self):
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
        print repr(self.p.root)