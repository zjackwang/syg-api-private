"""
Queries, adds, deletes, and updates collection(s) in MongoDB
    and checks if operations succeed and behaves as intended.
"""

from random import random
import unittest

from data import *

##
## Test User Submitted Generic Item Set Operations
##

class UserSubmittedGenericItemSetTests(unittest.TestCase):

    def test_insert_generic_item(self):
        random_item = {
            "Name": "Random",
            "Category": "Produce",
            "Subcategory": "Fresh",
            "IsCut": False,
            "DaysInFridge": 10.0,
            "DaysOnShelf": 0.0,
            "DaysInFreezer": 420.0,
            "Notes": "",
            "Links": "",
        }

        result = insert_generic_item(random_item)

        self.assertTrue(result.acknowledged)

        queried_item = user_submitted_generic_item_set.find_one_and_delete({"_id": result.inserted_id})

        self.assertEquals(queried_item, random_item)


class UserSubmittedMatchedItemDictTests(unittest.TestCase):

    def test_insert_matched_item(self):
        random_pair = {
            "ScannedItemName": "Random",
            "GenericItemName": "NotSoRandom"
        }

        result = insert_matched_item(random_pair)

        self.assertTrue(result.acknowledged)

        queried_item = user_submitted_matched_item_dict.find_one_and_delete({"_id": result.inserted_id})

        self.assertEquals(queried_item, random_pair)


class UserUpdatedMatchedItemSetTests(unittest.TestCase):

    def test_insert_generic_item_update(self):
        random_update = {
            "Original": {
                "Name": "Random",
                "Category": "Produce",
                "Subcategory": "Fresh",
                "IsCut": False,
                "DaysInFridge": 10.0,
                "DaysOnShelf": 0.0,
                "DaysInFreezer": 420.0,
                "Notes": "",
                "Links": "",
            },
            "Updated": {
                 "Name": "Random",
                "Category": "Produce",
                "Subcategory": "Fresh",
                "IsCut": False,
                "DaysInFridge": 10.0,
                "DaysOnShelf": 400.0,
                "DaysInFreezer": 420.0,
                "Notes": "",
                "Links": "",
            }        
        }

        result = insert_generic_item_update(random_update)

        self.assertTrue(result.acknowledged)

        queried_item = user_updated_generic_item_set.find_one_and_delete({"_id": result.inserted_id})

        self.assertEquals(queried_item, random_update)

def mongo_test_suite() -> unittest.TestSuite:
    suite = unittest.TestSuite()
    suite.addTest(UserSubmittedGenericItemSetTests("test_insert_generic_item"))
    suite.addTest(UserSubmittedMatchedItemDictTests("test_insert_matched_item"))
    suite.addTest(UserUpdatedMatchedItemSetTests("test_insert_generic_item_update"))
    return suite


def run_mongo_tests():
    runner = unittest.TextTestRunner()
    runner.run(mongo_test_suite())
