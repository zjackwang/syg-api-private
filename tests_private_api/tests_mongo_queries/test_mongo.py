"""
Queries, adds, deletes, and updates collection(s) in MongoDB
    and checks if operations succeed and behaves as intended.
"""

from random import random
import unittest

from data import *

##
## Test Generic Item Set Operations
##

## TODO
def mongo_test_suite() -> unittest.TestSuite:
    suite = unittest.TestSuite()
    
    return suite


def run_mongo_tests():
    runner = unittest.TextTestRunner()
    runner.run(mongo_test_suite())
