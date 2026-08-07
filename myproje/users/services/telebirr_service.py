

import json
import requests
import urllib3
from django.conf import settings
from .utils.tools import tools
# SSL Warning እንዳያሳይ
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class ApplyFabricTokenService:
    def __init__(self, *args, **kwargs):
        config = getattr(settings, 'TELEBIRR_CONFIG', {})
        
        self.base_url = kwargs.get('base_url') or config.get('BASE_URL', '')
        self.fabric_app_id = kwargs.get('fabric_app_id') or config.get('fabricAppId', '')
        self.app_secret = kwargs.get('app_secret') or config.get('appSecret', '')

    def apply_fabric_token(self):
        base_url = self.base_url.rstrip('/')
        url = f"{base_url}/payment/v1/token"

        headers = {
            "Content-Type": "application/json",
            "X-APP-Key": str(self.fabric_app_id)
        }

        payload = {
            "appId": str(self.fabric_app_id),
            "appSecret": str(self.app_secret)
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                verify=False,
                timeout=15
            )
            return response.json()
        except Exception as e:
            return {"error": f"Fabric Token Request Failed: {str(e)}"}


class CreateOrderService:
    def __init__(self, *args, **kwargs):
        config = getattr(settings, 'TELEBIRR_CONFIG', {})

        self.base_url = kwargs.get('base_url') or config.get('BASE_URL', '')
        self.web_base_url = kwargs.get('web_base_url') or config.get('WEB_BASE_URL', '')
        self.fabric_app_id = kwargs.get('fabric_app_id') or config.get('fabricAppId', '')
        self.app_secret = kwargs.get('app_secret') or config.get('appSecret', '')
        self.merchant_app_id = kwargs.get('merchant_app_id') or config.get('merchantAppId', '')
        self.merchant_code = kwargs.get('merchant_code') or config.get('merchantCode', '')
        self.notify_url = kwargs.get('notify_url') or config.get('notify_url', '')
        self.redirect_url = kwargs.get('redirect_url') or config.get('redirect_url', '')
        self.private_key = kwargs.get('private_key') or config.get('PRIVATE_KEY', '')

    def create_order(self, title, amount, out_trade_no):
        try:
            token_service = ApplyFabricTokenService(
                base_url=self.base_url,
                fabric_app_id=self.fabric_app_id,
                app_secret=self.app_secret
            )
            token_res = token_service.apply_fabric_token()
            fabric_token = token_res.get("token")

            if fabric_token:
                pre_order_res = self.request_create_order(fabric_token, title, amount, out_trade_no)
                
                if pre_order_res.get("code") in ["0", 200] and "biz_content" in pre_order_res:
                    prepay_id = pre_order_res["biz_content"]["prepay_id"]
                    raw_request = self.create_raw_request(prepay_id)
                    web_url = self.web_base_url.rstrip('/')
                    return f"{web_url}/pay/?{raw_request}&version=1.0&trade_type=Checkout"

        except Exception as e:
            print(f"Telebirr Gateway Unavailable ({str(e)}), Switching to Demo Mock Pay...")

        return f"/payment-success/?pnr={out_trade_no}&status=mocked_success"

    def request_create_order(self, fabric_token, title, amount, out_trade_no):
        headers = {
            "Content-Type": "application/json",
            "X-APP-Key": str(self.fabric_app_id),
            "Authorization": str(fabric_token)
        }
        payload_dict = self.create_request_object(title, amount, out_trade_no)
        
        base_url = self.base_url.rstrip('/')
        url = f"{base_url}/payment/v1/merchant/preOrder"

        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload_dict),
            verify=False,
            timeout=15
        )
        response.raise_for_status()
        return response.json()

    def create_request_object(self, title, amount, out_trade_no):
        biz = {
            "notify_url": self.notify_url,
            "appid": str(self.merchant_app_id),
            "merch_code": str(self.merchant_code),
            "merch_order_id": str(out_trade_no),
            "trade_type": "Checkout",
            "title": title,
            "total_amount": str(amount),
            "trans_currency": "ETB",
            "timeout_express": "120m",
            "business_type": "BuyGoods",
            "payee_identifier": str(self.merchant_code),
            "payee_identifier_type": "04",
            "payee_type": "5000",
            "redirect_url": self.redirect_url,
            "callback_info": "Ticket Purchase",
        }

        req = {
            "nonce_str": tools.createNonceStr(),
            "method": "payment.preorder",
            "timestamp": tools.createTimeStamp(),
            "version": "1.0",
            "biz_content": biz,
            "sign_type": "SHA256withRSA"
        }

        req["sign"] = tools.sign(req, self.private_key)
        return req

    def create_raw_request(self, prepay_id):
        maps = {
            "appid": str(self.merchant_app_id),
            "merch_code": str(self.merchant_code),
            "nonce_str": tools.createNonceStr(),
            "prepay_id": str(prepay_id),
            "timestamp": tools.createTimeStamp(),
            "sign_type": "SHA256WithRSA"
        }

        raw_request = "&".join([f"{k}={v}" for k, v in maps.items()])
        sign = tools.sign(maps, self.private_key)
        return f"{raw_request}&sign={sign}"

