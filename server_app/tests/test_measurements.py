from unittest import TestCase, TestSuite, TextTestRunner, makeSuite
import unittest
import sys
sys.path.insert(0, './')
from measurements import Measurements

class MeasurementsTest(TestCase):
    #assertEquals(True, False)

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_nothing(self):
        self.fail("shouldn't happen")


# def suite():
#     suite = TestSuite()
#     suite.addTest(makeSuite(MeasurementsTest))
#     return suite
#
# runner = TextTestRunner(verbosity=3)
# result = runner.run(suite())

if __name__ == '__main__':
    unittest.main()
