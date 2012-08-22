from pyless import parser

def run_doc_tests():
    import doctest
    doctest.testmod(parser, verbose=False)

if __name__ == "__main__":
	print "Running doc tests..."
	run_doc_tests()