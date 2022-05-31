"""
Fires off http requests to private api and tests return code
 
"""

from time import sleep
import requests
import unittest
import subprocess

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
def make_keyed_post_request(payload, url) -> requests.Response:
    # print(payload)
    # print(secret_key)
    hmac_sig = str(generate_hmac_signature(payload, secret_key))
    # print(hmac_sig)
    return requests.post(
        url,
        json=payload,
        headers={"X-Syg-Api-Key": api_key, "X-HMAC-Signature": hmac_sig, "X-Is-Test-Request": 'True'},
        timeout=3.0
    )

##
## Endpoints
##

## Local endpoints
USER_SUBMITTED_GENERIC_ITEM_LOCAL = "http://localhost:5000/usersubmittedgenericitemset"
USER_SUBMITTED_MATCHED_ITEM_LOCAL = "http://localhost:5000/usersubmittedmatcheditemset"
USER_UPDATED_GENERIC_ITEM_LOCAL = "http://localhost:5000/userupdatedgenericitemset"
## Remote endpoints

### TODO: NEGATIVE TESTS 
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

        response = make_keyed_post_request(payload, USER_SUBMITTED_GENERIC_ITEM_LOCAL)

        failure_msg = f"Request failed. Response: {response.content}"
        self.assertEqual(
            response.status_code,
            200,
            msg=failure_msg,
        )

    def test_user_submitted_matched_item_post(self):
        payload = {
            'ScannedItemName': 'Not Random',
            'GenericItemName': 'Random',
        }

        response = make_keyed_post_request(payload, USER_SUBMITTED_MATCHED_ITEM_LOCAL)

        failure_msg = f"Request failed. Response: {response.content}"
        self.assertEqual(
            response.status_code,
            200,
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

        response = make_keyed_post_request(payload, USER_UPDATED_GENERIC_ITEM_LOCAL)

        failure_msg = f"Request failed. Response: {response.content}"
        self.assertEqual(
            response.status_code,
            200,
            msg=failure_msg,
        )
        
    def tearDown(self) -> None:
        print("TEARING DOWN")
        stop_local_api(self.api)
        print(self.api.poll())

def test_suite_local_api():
    suite = unittest.TestSuite()
    suite.addTest(PrivateLocalAPITests("test_user_submitted_generic_item_post"))
    suite.addTest(PrivateLocalAPITests("test_user_submitted_matched_item_post"))
    suite.addTest(PrivateLocalAPITests("test_user_updated_generic_item_post"))
    return suite


def test_suite_remote_api():
    suite = unittest.TestSuite()
    return suite


def run_local_api_tests():
    runner = unittest.TextTestRunner()
    runner.run(test_suite_local_api())


def run_remote_api_tests():
    runner = unittest.TextTestRunner()
    runner.run(test_suite_remote_api())
