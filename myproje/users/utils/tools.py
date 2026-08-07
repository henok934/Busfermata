import time
import uuid
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

class Tools:
    @staticmethod
    def createNonceStr():
        return uuid.uuid4().hex

    @staticmethod
    def createTimeStamp():
        return str(int(time.time()))

    @staticmethod
    def createMerchantOrderId():
        return str(int(time.time() * 1000))

    @staticmethod
    def sign(data_dict, private_key_pem):
        """
        Sorts keys alphabetically, excludes empty/null parameters & 'sign'/'sign_type', 
        formats key=value pairs into a string, and generates RSA-SHA256 signature.
        """
        exclude_keys = ["sign", "sign_type"]
        filtered_items = []

        for k in sorted(data_dict.keys()):
            if k not in exclude_keys and data_dict[k] is not None and data_dict[k] != "":
                val = data_dict[k]
                if isinstance(val, (dict, list)):
                    val = json.dumps(val, separators=(',', ':'))
                filtered_items.append(f"{k}={val}")

        string_to_sign = "&".join(filtered_items)
        
        key = RSA.import_key(private_key_pem)
        h = SHA256.new(string_to_sign.encode('utf-8'))
        signature = pkcs1_15.new(key).sign(h)
        return base64.b64encode(signature).decode('utf-8')

tools = Tools()
