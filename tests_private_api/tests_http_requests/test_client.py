"""
Fires off http requests to private api and tests return code
 
"""

from time import sleep
import requests
from requests.exceptions import Timeout
import unittest
import subprocess
import json 

from .test_config import api_key, secret_key

from security.hmac_sig_gen import generate_hmac_signature


def run_local_api():
    api = subprocess.Popen(["python", "api.py"])
    return api


def stop_local_api(api: subprocess.Popen):
    subprocess.run(["kill", str(api.pid)])


##
## Secured requests w/ hmac sig
##
def make_keyed_post_request(payload, url, timeout=5.0) -> requests.Response:
    hmac_msg = "We were living to run, and running to live"
    hmac_sig = generate_hmac_signature(hmac_msg, secret_key).hex()
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"X-Hmac-Signature": hmac_sig, "X-Hmac-Message": hmac_msg, "X-Is-Test-Request": 'True'},
            timeout=timeout
        )
    except Timeout:
        raise Timeout

    return response

## Meant to fail requests
def make_incorrect_key_post_request(payload, url, timeout=5.0) -> requests.Response:
    incorrect_secret_key = "thisisnothecorrectsecretkey"
    hmac_msg = "Til there was nothing left to burn, and nothing left to prove"
    hmac_sig = generate_hmac_signature(hmac_msg, incorrect_secret_key).hex()

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"X-Hmac-Signature": hmac_sig, "X-Hmac-Message": hmac_msg, "X-Is-Test-Request": 'True'},
            timeout=timeout
        )
    except Timeout:
        raise Timeout

    return response

def make_timedout_post_request(payload, url) -> requests.Response:
    miniscule_timeout = 0.0000001
    hmac_msg = "You can feel the eyes upon you, as you shake off the cold..."
    hmac_sig = generate_hmac_signature(hmac_msg, secret_key).hex()

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"X-Hmac-Signature": hmac_sig, "X-Hmac-Message": hmac_msg, "X-Is-Test-Request": 'True'},
            timeout=miniscule_timeout
        )
    except Timeout:
        raise Timeout

    return response

##
## Endpoints
##

## Local endpoints
USER_SUBMITTED_GENERIC_ITEM_LOCAL = "http://localhost:5000/usersubmittedgenericitemset"
USER_SUBMITTED_MATCHED_ITEM_LOCAL = "http://localhost:5000/usersubmittedmatcheditemset"
USER_UPDATED_GENERIC_ITEM_LOCAL = "http://localhost:5000/userupdatedgenericitemset"
## Remote endpoints
USER_SUBMITTED_GENERIC_ITEM_REMOTE = "https://syg-user-submitted.herokuapp.com/usersubmittedgenericitemset"
USER_SUBMITTED_MATCHED_ITEM_REMOTE = "https://syg-user-submitted.herokuapp.com/usersubmittedmatcheditemset"
USER_UPDATED_GENERIC_ITEM_REMOTE = "https://syg-user-submitted.herokuapp.com/userupdatedgenericitemset"


## HTTP Response Status codes
SUCCESS_CODE = 200
FORBIDDEN_CODE = 403 

class PrivateLocalAPITests(unittest.TestCase):
    def setUp(self) -> None:
        self.api = run_local_api()
        sleep(1)

    def test_user_submitted_generic_item_post(self):
        payload = {
            'Name': 'Random',
            'Category': 'Produce',
            'Subcategory': 'Fresh',
            'IsCut': False, 
            'DaysInFridge': 30.0,
            'DaysOnShelf': 30.0,
            'DaysInFreezer': 240.0,
            'Notes': '',
            'Links': ''
        }

        try: 
            response = make_keyed_post_request(payload, USER_SUBMITTED_GENERIC_ITEM_LOCAL)
        except Timeout: 
            self.fail("Request timed out")

        failure_msg = f"Request failed. Response: {response.content}"
        self.assertEqual(
            response.status_code,
            SUCCESS_CODE,
            msg=failure_msg,
        )

    def test_user_submitted_matched_item_post(self):
        payload = {
            'ScannedItemName': 'Not Random',
            'GenericItemName': 'Random',
        }
        
        try: 
            response = make_keyed_post_request(payload, USER_SUBMITTED_MATCHED_ITEM_LOCAL)
        except Timeout: 
            self.fail("Request timed out")

        failure_msg = f"Request failed. Response: {response.content}"
        self.assertEqual(
            response.status_code,
            SUCCESS_CODE,
            msg=failure_msg,
        )

    def test_user_updated_generic_item_post(self):
        payload = {
            'Original': {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': False, 
                'DaysInFridge': 30.0,
                'DaysOnShelf': 30.0,
                'DaysInFreezer': 240.0,
                'Notes': '',
                'Links': ''
            },
            'Updated': {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': False, 
                'DaysInFridge': 30.0,
                'DaysOnShelf': 35.0,
                'DaysInFreezer': 240.0,
                'Notes': '',
                'Links': ''
            }
        }

        try:
            response = make_keyed_post_request(payload, USER_UPDATED_GENERIC_ITEM_LOCAL)
        except Timeout: 
            self.fail("Request timed out")

        failure_msg = f"Request failed. Response: {response.content}"
        self.assertEqual(
            response.status_code,
            SUCCESS_CODE,
            msg=failure_msg,
        )

    def test_invalid_hmac_user_submitted_generic_item(self):
        payload = {
            'Name': 'Random',
            'Category': 'Produce',
            'Subcategory': 'Fresh',
            'IsCut': False, 
            'DaysInFridge': 30.0,
            'DaysOnShelf': 30.0,
            'DaysInFreezer': 240.0,
            'Notes': '',
            'Links': ''
        }

        url = USER_SUBMITTED_GENERIC_ITEM_LOCAL

        try: 
            response = make_incorrect_key_post_request(payload, url)
        except Timeout:
            self.fail("Request timed out")
        
        self.assertEqual(
            response.status_code,
            FORBIDDEN_CODE,
            msg="Incorrect status code")

        invalid_hmac_message = "Received HMAC signature could not be verified"
        response_message = json.loads(response.content)['message']

        self.assertEqual(
            response_message,
            invalid_hmac_message,
            msg="Aborted request due to reasons other than invalid hmac"
        )
    
    def test_invalid_hmac_user_submitted_matched_item(self):
        payload = {
            'ScannedItemName': 'Not Random',
            'GenericItemName': 'Random',
        }

        url = USER_SUBMITTED_MATCHED_ITEM_LOCAL

        try: 
            response = make_incorrect_key_post_request(payload, url)
        except Timeout:
            self.fail("Request timed out")
        
        self.assertEqual(
            response.status_code,
            FORBIDDEN_CODE,
            msg="Incorrect status code")

        invalid_hmac_message = "Received HMAC signature could not be verified"
        response_message = json.loads(response.content)['message']
        self.assertEqual(
            response_message,
            invalid_hmac_message,
            msg="Aborted request due to reasons other than invalid hmac"
        )
    
    def test_invalid_hmac_user_updated_generic_item(self):
        payload = {
            'Original': {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': False, 
                'DaysInFridge': 30.0,
                'DaysOnShelf': 30.0,
                'DaysInFreezer': 240.0,
                'Notes': '',
                'Links': ''
            },
            'Updated': {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': False, 
                'DaysInFridge': 30.0,
                'DaysOnShelf': 35.0,
                'DaysInFreezer': 240.0,
                'Notes': '',
                'Links': ''
            }
        }

        url = USER_UPDATED_GENERIC_ITEM_LOCAL

        try: 
            response = make_incorrect_key_post_request(payload, url)
        except Timeout:
            self.fail("Request timed out")
        
        self.assertEqual(
            response.status_code,
            FORBIDDEN_CODE,
            msg="Incorrect status code")

        invalid_hmac_message = "Received HMAC signature could not be verified"
        response_message = json.loads(response.content)['message']
        self.assertEqual(
            response_message,
            invalid_hmac_message,
            msg="Aborted request due to reasons other than invalid hmac"
        )
        
    def test_invalid_payloads_user_submitted_generic_item(self):
        payloads = [{}, {
            'Name': 'Random',
            'Category': 'Produce',
            'Subcategory': 'Fresh',
            }, {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': 'False', 
                'DaysInFridge': '30.0',
                'DaysOnShelf': '30.0',
                'DaysInFreezer': '240.0',
                'Notes': '',
                'Links': ''
            }, {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': False, 
                'DaysInFridge': 30,
                'DaysOnShelf': 30,
                'DaysInFreezer': 240,
                'Notes': '',
                'Links': ''
            }
        ]

        url = USER_SUBMITTED_GENERIC_ITEM_LOCAL

        for payload in payloads:
            try: 
                response = make_keyed_post_request(payload, url)
            except Timeout:
                self.fail("Request timed out")
            
            self.assertEqual(
                response.status_code,
                FORBIDDEN_CODE,
                msg="Incorrect status code")

            invalid_hmac_message = "Submitted json does not fit required format"
            response_message = json.loads(response.content)['message']

            self.assertEqual(
                response_message,
                invalid_hmac_message,
                msg="Aborted request due to reasons other than invalid json"
            )

    def test_invalid_payloads_user_submitted_matched_item(self):
        payloads = [
            {}, {
            'ScannedItemName': 'Not Random',
            }
        ]

        url = USER_SUBMITTED_MATCHED_ITEM_LOCAL

        for payload in payloads:
            try: 
                response = make_keyed_post_request(payload, url)
            except Timeout:
                self.fail("Request timed out")
            
            self.assertEqual(
                response.status_code,
                FORBIDDEN_CODE,
                msg="Incorrect status code")

            invalid_hmac_message = "Submitted json does not fit required format"
            response_message = json.loads(response.content)['message']

            self.assertEqual(
                response_message,
                invalid_hmac_message,
                msg="Aborted request due to reasons other than invalid json"
            )

    def test_invalid_payloads_user_updated_generic_item(self):
        payloads = [
            {}, {
                'Original': {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': False, 
                'DaysInFridge': 30.0,
                'DaysOnShelf': 30.0,
                'DaysInFreezer': 240.0,
                'Notes': '',
                'Links': ''
                },
            }
        ]

        url = USER_UPDATED_GENERIC_ITEM_LOCAL

        for payload in payloads:
            try: 
                response = make_keyed_post_request(payload, url)
            except Timeout:
                self.fail("Request timed out")
            
            self.assertEqual(
                response.status_code,
                FORBIDDEN_CODE,
                msg="Incorrect status code")

            invalid_hmac_message = "Submitted json does not fit required format"
            response_message = json.loads(response.content)['message']

            self.assertEqual(
                response_message,
                invalid_hmac_message,
                msg="Aborted request due to reasons other than invalid json"
            )
        

    def test_timedout_request(self):
        payload = {
            'Name': 'Random',
            'Category': 'Produce',
            'Subcategory': 'Fresh',
            'IsCut': False, 
            'DaysInFridge': 30.0,
            'DaysOnShelf': 30.0,
            'DaysInFreezer': 240.0,
            'Notes': '',
            'Links': ''
        }

        url = USER_SUBMITTED_GENERIC_ITEM_LOCAL

        try: 
            make_timedout_post_request(payload, url)
        except Timeout:
            return 
        
        self.fail("Request somehow did not time out...")
        
        
    def tearDown(self) -> None:
        print("TEARING DOWN")
        stop_local_api(self.api)
        print(self.api.poll())


class PrivateRemoteAPITests(unittest.TestCase):
    def test_user_submitted_generic_item_post(self):
        payload = {
            'Name': 'Random',
            'Category': 'Produce',
            'Subcategory': 'Fresh',
            'IsCut': False, 
            'DaysInFridge': 30.0,
            'DaysOnShelf': 30.0,
            'DaysInFreezer': 240.0,
            'Notes': '',
            'Links': ''
        }

        try:
            response = make_keyed_post_request(payload, USER_SUBMITTED_GENERIC_ITEM_REMOTE)
        except Timeout: 
            self.fail("Request timed out")

        failure_msg = f"Request failed. Response: {response.content}"
        self.assertEqual(
            response.status_code,
            SUCCESS_CODE,
            msg=failure_msg,
        )

    def test_user_submitted_matched_item_post(self):
        payload = {
            'ScannedItemName': 'Not Random',
            'GenericItemName': 'Random',
        }

        try:
            response = make_keyed_post_request(payload, USER_SUBMITTED_MATCHED_ITEM_REMOTE)
        except Timeout: 
            self.fail("Request timed out")

        failure_msg = f"Request failed. Response: {response.content}"
        self.assertEqual(
            response.status_code,
            SUCCESS_CODE,
            msg=failure_msg,
        )

    def test_user_updated_generic_item_post(self):
        payload = {
            'Original': {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': False, 
                'DaysInFridge': 30.0,
                'DaysOnShelf': 30.0,
                'DaysInFreezer': 240.0,
                'Notes': '',
                'Links': ''
            },
            'Updated': {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': False, 
                'DaysInFridge': 30.0,
                'DaysOnShelf': 35.0,
                'DaysInFreezer': 240.0,
                'Notes': '',
                'Links': ''
            }
        }
        
        try:
            response = make_keyed_post_request(payload, USER_UPDATED_GENERIC_ITEM_REMOTE, timeout=7.5)
        except Timeout: 
            self.fail("Request timed out")

        failure_msg = f"Request failed. Response: {response.content}"
        self.assertEqual(
            response.status_code,
            SUCCESS_CODE,
            msg=failure_msg,
        )
    

    def test_invalid_hmac_user_submitted_generic_item(self):
        payload = {
            'Name': 'Random',
            'Category': 'Produce',
            'Subcategory': 'Fresh',
            'IsCut': False, 
            'DaysInFridge': 30.0,
            'DaysOnShelf': 30.0,
            'DaysInFreezer': 240.0,
            'Notes': '',
            'Links': ''
        }

        url = USER_SUBMITTED_GENERIC_ITEM_REMOTE

        try: 
            response = make_incorrect_key_post_request(payload, url)
        except Timeout:
            self.fail("Request timed out")
        
        self.assertEqual(
            response.status_code,
            FORBIDDEN_CODE,
            msg="Incorrect status code")

        invalid_hmac_message = "Received HMAC signature could not be verified"
        response_message = json.loads(response.content)['message']

        self.assertEqual(
            response_message,
            invalid_hmac_message,
            msg="Aborted request due to reasons other than invalid hmac"
        )
    
    def test_invalid_hmac_user_submitted_matched_item(self):
        payload = {
            'ScannedItemName': 'Not Random',
            'GenericItemName': 'Random',
        }

        url = USER_SUBMITTED_MATCHED_ITEM_REMOTE

        try: 
            response = make_incorrect_key_post_request(payload, url)
        except Timeout:
            self.fail("Request timed out")
        
        self.assertEqual(
            response.status_code,
            FORBIDDEN_CODE,
            msg="Incorrect status code")

        invalid_hmac_message = "Received HMAC signature could not be verified"
        response_message = json.loads(response.content)['message']
        self.assertEqual(
            response_message,
            invalid_hmac_message,
            msg="Aborted request due to reasons other than invalid hmac"
        )
    
    def test_invalid_hmac_user_updated_generic_item(self):
        payload = {
            'Original': {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': False, 
                'DaysInFridge': 30.0,
                'DaysOnShelf': 30.0,
                'DaysInFreezer': 240.0,
                'Notes': '',
                'Links': ''
            },
            'Updated': {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': False, 
                'DaysInFridge': 30.0,
                'DaysOnShelf': 35.0,
                'DaysInFreezer': 240.0,
                'Notes': '',
                'Links': ''
            }
        }

        url = USER_UPDATED_GENERIC_ITEM_REMOTE

        try: 
            response = make_incorrect_key_post_request(payload, url)
        except Timeout:
            self.fail("Request timed out")
        
        self.assertEqual(
            response.status_code,
            FORBIDDEN_CODE,
            msg="Incorrect status code")

        invalid_hmac_message = "Received HMAC signature could not be verified"
        response_message = json.loads(response.content)['message']
        self.assertEqual(
            response_message,
            invalid_hmac_message,
            msg="Aborted request due to reasons other than invalid hmac"
        )
        
    def test_invalid_payloads_user_submitted_generic_item(self):
        payloads = [{}, {
            'Name': 'Random',
            'Category': 'Produce',
            'Subcategory': 'Fresh',
            }, {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': 'False', 
                'DaysInFridge': '30.0',
                'DaysOnShelf': '30.0',
                'DaysInFreezer': '240.0',
                'Notes': '',
                'Links': ''
            }, {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': False, 
                'DaysInFridge': 30,
                'DaysOnShelf': 30,
                'DaysInFreezer': 240,
                'Notes': '',
                'Links': ''
            }
        ]

        url = USER_SUBMITTED_GENERIC_ITEM_REMOTE

        for payload in payloads:
            try: 
                response = make_keyed_post_request(payload, url)
            except Timeout:
                self.fail("Request timed out")
            
            self.assertEqual(
                response.status_code,
                FORBIDDEN_CODE,
                msg="Incorrect status code")

            invalid_hmac_message = "Submitted json does not fit required format"
            response_message = json.loads(response.content)['message']

            self.assertEqual(
                response_message,
                invalid_hmac_message,
                msg="Aborted request due to reasons other than invalid json"
            )

    def test_invalid_payloads_user_submitted_matched_item(self):
        payloads = [
            {}, {
            'ScannedItemName': 'Not Random',
            }
        ]

        url = USER_SUBMITTED_MATCHED_ITEM_REMOTE

        for payload in payloads:
            try: 
                response = make_keyed_post_request(payload, url)
            except Timeout:
                self.fail("Request timed out")
            
            self.assertEqual(
                response.status_code,
                FORBIDDEN_CODE,
                msg="Incorrect status code")

            invalid_hmac_message = "Submitted json does not fit required format"
            response_message = json.loads(response.content)['message']

            self.assertEqual(
                response_message,
                invalid_hmac_message,
                msg="Aborted request due to reasons other than invalid json"
            )

    def test_invalid_payloads_user_updated_generic_item(self):
        payloads = [
            {}, {
                'Original': {
                'Name': 'Random',
                'Category': 'Produce',
                'Subcategory': 'Fresh',
                'IsCut': False, 
                'DaysInFridge': 30.0,
                'DaysOnShelf': 30.0,
                'DaysInFreezer': 240.0,
                'Notes': '',
                'Links': ''
                },
            }
        ]

        url = USER_UPDATED_GENERIC_ITEM_REMOTE

        for payload in payloads:
            try: 
                response = make_keyed_post_request(payload, url)
            except Timeout:
                self.fail("Request timed out")
            
            self.assertEqual(
                response.status_code,
                FORBIDDEN_CODE,
                msg="Incorrect status code")

            invalid_hmac_message = "Submitted json does not fit required format"
            response_message = json.loads(response.content)['message']

            self.assertEqual(
                response_message,
                invalid_hmac_message,
                msg="Aborted request due to reasons other than invalid json"
            )
        
    def test_timedout_request(self):
        payload = {
            'Name': 'Random',
            'Category': 'Produce',
            'Subcategory': 'Fresh',
            'IsCut': False, 
            'DaysInFridge': 30.0,
            'DaysOnShelf': 30.0,
            'DaysInFreezer': 240.0,
            'Notes': '',
            'Links': ''
        }

        url = USER_SUBMITTED_GENERIC_ITEM_REMOTE

        try: 
            make_timedout_post_request(payload, url)
        except Timeout:
            return 
        
        self.fail("Request somehow did not time out...")

def test_suite_local_api():
    suite = unittest.TestSuite()
    suite.addTest(PrivateLocalAPITests("test_user_submitted_generic_item_post"))
    suite.addTest(PrivateLocalAPITests("test_user_submitted_matched_item_post"))
    suite.addTest(PrivateLocalAPITests("test_user_updated_generic_item_post"))
    suite.addTest(PrivateLocalAPITests("test_invalid_hmac_user_submitted_generic_item"))
    suite.addTest(PrivateLocalAPITests("test_invalid_hmac_user_submitted_matched_item"))
    suite.addTest(PrivateLocalAPITests("test_invalid_hmac_user_updated_generic_item"))
    suite.addTest(PrivateLocalAPITests("test_invalid_payloads_user_submitted_generic_item"))
    suite.addTest(PrivateLocalAPITests("test_invalid_payloads_user_submitted_matched_item"))
    suite.addTest(PrivateLocalAPITests("test_invalid_payloads_user_updated_generic_item"))
    suite.addTest(PrivateLocalAPITests("test_timedout_request"))
    return suite


def test_suite_remote_api():
    suite = unittest.TestSuite()
    suite.addTest(PrivateRemoteAPITests("test_user_submitted_generic_item_post"))
    suite.addTest(PrivateRemoteAPITests("test_user_submitted_matched_item_post"))
    suite.addTest(PrivateRemoteAPITests("test_user_updated_generic_item_post"))
    suite.addTest(PrivateRemoteAPITests("test_invalid_hmac_user_submitted_generic_item"))
    suite.addTest(PrivateRemoteAPITests("test_invalid_hmac_user_submitted_matched_item"))
    suite.addTest(PrivateRemoteAPITests("test_invalid_hmac_user_updated_generic_item"))
    suite.addTest(PrivateRemoteAPITests("test_invalid_payloads_user_submitted_generic_item"))
    suite.addTest(PrivateRemoteAPITests("test_invalid_payloads_user_submitted_matched_item"))
    suite.addTest(PrivateRemoteAPITests("test_invalid_payloads_user_updated_generic_item"))
    suite.addTest(PrivateRemoteAPITests("test_timedout_request"))
    return suite


def run_local_api_tests():
    runner = unittest.TextTestRunner()
    runner.run(test_suite_local_api())


def run_remote_api_tests():
    runner = unittest.TextTestRunner()
    runner.run(test_suite_remote_api())
