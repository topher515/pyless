import unittest

from parser import Parser, compile
from tree import *

import glob
import os


class TestUpstream(unittest.TestCase):
	def __init__(self,cssfile,lessfile,*args,**kwargs):
		self.cssfile = cssfile
		self.lessfile = lessfile
		super(TestUpstream,self).__init__(*args,**kwargs)

	def test_compilation(self):
		self.assertEquals(
			compile(open(self.cssfile,'r').read()),
			open(self.lessfile,'r').read()
			)




def main():
	suite = unittest.TestSuite()

	for path in glob.glob('tests/upstream/test/css/*'):
		dirname = os.path.dirname(path)
		filename = os.path.basename(path)
		name = filename[:-4]
		testcase = TestUpstream(path,'tests/upstream/test/less/'+name+'.less','test_compilation')
		suite.addTest(testcase)

	unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
	main()