import base64
import time
import secrets
import string
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


class tools:
    @staticmethod
    def createNonceStr(length=32):
        """
        Generates a random alphanumeric string of specified length.
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def createTimeStamp():
        """
        Returns current Unix timestamp as a string.
        """
        return str(int(time.time()))

    @staticmethod
    def sign(params, private_key_pem):
        """
        Generates an RSA-SHA256 signature for Telebirr payload.
        
        :param params: dict or raw string to sign
        :param private_key_pem: RSA Private Key in PEM string format
        :return: Base64-encoded signature string
        """
        # 1. Format payload string: exclude 'sign' & 'sign_type', sort keys alphabetically
        if isinstance(params, dict):
            filtered_params = {
                k: v for k, v in params.items() 
                if k not in ["sign", "sign_type"] and v is not None and v != ""
            }
            sorted_keys = sorted(filtered_params.keys())
            string_a = "&".join([f"{k}={filtered_params[k]}" for k in sorted_keys])
        else:
            string_a = str(params)

        # 2. Format private key string
        key_str = private_key_pem.strip()
        if not key_str.startswith("-----BEGIN"):
            key_str = f"-----BEGIN PRIVATE KEY-----\n{key_str}\n-----END PRIVATE KEY-----"

        # 3. Sign using RSA-SHA256
        rsa_key = RSA.import_key(key_str)
        signer = pkcs1_15.new(rsa_key)
        digest = SHA256.new(string_a.encode('utf-8'))
        signature = signer.sign(digest)

        # 4. Return base64 encoded signature
        return base64.b64encode(signature).decode('utf-8')
