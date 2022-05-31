import hmac
import hashlib
import json 

def generate_hmac_signature(message, key):
    str_message = json.dumps(message)
    hmc = hmac.new(key=key.encode(), msg=str_message.encode(), digestmod=hashlib.sha256)
    message_digest = hmc.digest()

    return message_digest


def compare_hmac_signatures(a, b):
    return hmac.compare_digest(a, b)