from flask import Flask, request
from flask_restful import abort, Api, Resource

import hmac
import hashlib

from data import insert_generic_item, insert_matched_item, insert_generic_item_update
from security.hmac_sig_gen import generate_hmac_signature
from config import secret_key

app = Flask(__name__)
api = Api(app)


##
## Abort conditions
##

def abort_invalid_json():
    abort(403, message="Submitted json does not fit required format") 

def abort_invalid_hmac_signature():
    abort(403, message="Received HMAC signature could not be verified")


##
## Validation
##


def validate_headers():
    headers = request.headers

    ## Validate hmac signature. Must use stored secret key
    received_hmac_sig = headers["X-Hmac-Signature"]
    received_hmac_message = headers["X-Hmac-Message"]
    generated_hmac_sig = generate_hmac_signature(received_hmac_message, secret_key).hex()
    # print(f"GENERATED HMAC: {generated_hmac_sig}")

    if not hmac.compare_digest(received_hmac_sig, generated_hmac_sig):
        abort_invalid_hmac_signature()

GENERIC_ITEM_KEYS_AND_TYPES = {'Name': str, 'Category': str, 'Subcategory': str, 'IsCut': bool, 'DaysInFridge': float, 'DaysOnShelf': float, 'DaysInFreezer': float, 'Notes': str, 'Links': str}

MATCHED_ITEM_KEYS_AND_TYPES = {'ScannedItemName': str, 'GenericItemName': str}

UPDATE_GENERIC_ITEM_KEYS_AND_TYPES = {'Original': dict, 'Updated': dict}

def validate_generic_item_json(rec_json):
    keys_to_validate = set(rec_json.keys())
    if len(set(GENERIC_ITEM_KEYS_AND_TYPES.keys()).difference(keys_to_validate)) > 0 :
        abort_invalid_json()
    
    for k in keys_to_validate:
        if type(rec_json[k]) != GENERIC_ITEM_KEYS_AND_TYPES[k]:
            abort_invalid_json()

def validate_matched_item_json(rec_json):
    keys_to_validate = set(rec_json.keys())
    if len(set(MATCHED_ITEM_KEYS_AND_TYPES.keys()).difference(keys_to_validate)) > 0 :
        abort_invalid_json()
    
    for k in keys_to_validate:
        if type(rec_json[k]) != MATCHED_ITEM_KEYS_AND_TYPES[k]:
            abort_invalid_json()

def validate_updated_generic_item_json(rec_json):
    keys_to_validate = set(rec_json.keys())
    if len(set(UPDATE_GENERIC_ITEM_KEYS_AND_TYPES.keys()).difference(keys_to_validate)) > 0 :
        abort_invalid_json()
    for k in keys_to_validate:
        if type(rec_json[k]) != UPDATE_GENERIC_ITEM_KEYS_AND_TYPES[k]:
            abort_invalid_json()
        validate_generic_item_json(rec_json[k])

def is_test_request():
    headers = request.headers 
    return headers["X-Is-Test-Request"] == 'True'


##
## Api resource routing
##  - expects content-type of application/json 
##

class UserSubmittedGenericItemSet(Resource):
    def post(self):
        rec_json = request.get_json()
        validate_headers()

        validate_generic_item_json(rec_json) 

        if is_test_request():
            return "success"
        
        insert_generic_item(rec_json) 

class UserSubmittedMatchedItemSet(Resource):
    def post(self):
        rec_json = request.get_json()
        validate_headers()

        validate_matched_item_json(rec_json) 

        if is_test_request():
            return "success"
        
        insert_matched_item(rec_json) 

class UserUpdatedGenericItemSet(Resource):
    def post(self):
        rec_json = request.get_json()
        validate_headers()

        validate_updated_generic_item_json(rec_json) 

        if is_test_request():
            return "success"
        
        insert_generic_item_update(rec_json) 

api.add_resource(UserSubmittedGenericItemSet, "/usersubmittedgenericitemset")
api.add_resource(UserSubmittedMatchedItemSet, "/usersubmittedmatcheditemset")
api.add_resource(UserUpdatedGenericItemSet, "/userupdatedgenericitemset")

if __name__ == "__main__":
    app.run()
