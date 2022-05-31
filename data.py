from nis import match
from xmlrpc.client import Boolean
from pymongo import MongoClient

from typing import Any, Dict, List

from config import mongo_key

client = MongoClient(
    f"mongodb+srv://zjackwang:{mongo_key}@cluster0.5ocd6.mongodb.net/test?authSource=admin&replicaSet=atlas-q2c9r8-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true"
)

## Database
syg_data = client["syg_data"]


## Helper
def format_returned_items(mongo_db_cursor):
    items = [item for item in mongo_db_cursor]
    # ObjectID is not JSON Serializable
    return items


## Typings
MongoObject = Dict[str, Any]

###
## Collection References
##

user_submitted_generic_item_set = syg_data["UserSubmittedGenericItemSet"]
user_submitted_matched_item_dict = syg_data["UserSubmittedMatchedItemDict"]
user_updated_generic_item_set = syg_data["UserUpdatedGenericItemSet"]


## User Submitted Generic Item Set

"""
Input: Dict generic item format 
Output: Bool result of insert call 
"""
def insert_generic_item(generic_item: MongoObject) -> bool:
    result = user_submitted_generic_item_set.insert_one(generic_item)
    return result 


## User Submitted Matched Item Dict 

"""
Input: Dict matched item format 
Output: Bool result of insert call 
"""
def insert_matched_item(matched_item: MongoObject) -> bool:
    result = user_submitted_matched_item_dict.insert_one(matched_item)
    return result 


## User Updated Generic Item Set

"""
Input: List of len 2, each a Dict generic item format 
Output: Bool result of insert call 
"""
def insert_generic_item_update(generic_item_update: MongoObject) -> bool:
    result = user_updated_generic_item_set.insert_one(generic_item_update)
    return result 