import json
import requests
import urllib3
from django.conf import settings

# Disable SSL warnings for testing with 196.188.120.3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_fabric_token():
    config = settings.TELEBIRR_CONFIG
    url = f"{config['base_url']}/payment/v1/token"
    
    headers = {
        "Content-Type": "application/json",
        "X-APP-Key": config["fabric_app_id"]
    }
    
    payload = {
        "appSecret": config["app_secret"]
    }
    
    response = requests.post(
        url, 
        headers=headers, 
        data=json.dumps(payload), 
        verify=False
    )
    if response.status_code == 200:
        res_data = response.json()
        # Returns {"token": "Bearer 94cc...", "effectiveDate": "...", "expirationDate": "..."}
        return res_data.get("token")
    else:
        raise Exception(f"Failed to get Fabric token: {response.status_code} - {response.text}")
