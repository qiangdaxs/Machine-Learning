#!/usr/bin/env python3.3
'''test_simulate.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2013-06-23 21:10:42 -0400'
__version__ = '0.0'
__status__ = 'Prototype: not working'


import unittest


class TestCase(unittest.TestCase):
    '''Test Case'''

    def setUp(self):
        pass

    def test_(self):
        prices = pd.DataFrame([[pd.Timestamp('2015-2-11 20:47'), 124.8]], columns=['T', 'AAPL']).set_index('T')
        >>> do_transaction(pd.Timestamp('2015-2-11 20:47:15'), 'AAPL', 0.4, prices)
        (Timestamp('2015-02-11 20:47:00'), 'AAPL', 0.4, 124.8)


def main():
    unittest.main()


if __name__ == "__main__":
    main()


#!/usr/bin/env python3.3
'''test_simulation.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2013-06-23 21:10:42 -0400'
__version__ = '0.0'
__status__ = 'Prototype: not working'


import unittest
from simulate import *

#Tester = type('Tester', (unittest.TestCase, ), {})
#Tester.assertEqual(1,1)
#assert(1==9)
#Tester.assertEqual(1,1)
#dd = type('dd', (), {})
#dd()

def test_a(self):
    self.assertEqual(1, 2)


TestCase = type('Test', (unittest.TestCase, ), {'test_a': test_a})




def main():
    unittest.main()


if __name__ == "__main__":
    main()
