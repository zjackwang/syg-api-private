import hmac
import hashlib

def generate_hmac_signature(message, key):
    hmc = hmac.new(key=key.encode(), msg=message.encode(), digestmod=hashlib.sha256)
    message_digest = hmc.digest()

    return message_digest


def compare_hmac_signatures(a, b):
    return hmac.compare_digest(a, b)