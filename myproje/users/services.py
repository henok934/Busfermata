import requests


class TelebirrService:
    @staticmethod
    def generate_token():
        url = "http://192.168.251.39:8010/api/operators/generatetoken"
        headers = {
            "x-api-key": "4F10EF34-DE37-4240-B1BF-A8FEAD615AE3",
            "Content-Type": "application/json"
        }
        payload = {
            "username": "61F4AF42-25FF-4B3B-8092-356321979E08"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            # Debug prints to inspect what Telebirr returns in the server terminal
            print(f"[Telebirr Token Status]: {response.status_code}")
            print(f"[Telebirr Token Body]: {response.text}")
            
            if response.status_code == 200:
                try:
                    res_data = response.json()
                    # Safely handles different token locations (top-level, nested, or string response)
                    if isinstance(res_data, dict):
                        token = res_data.get("token") or res_data.get("data", {}).get("token") or res_data.get("accessToken")
                        if token:
                            return token
                    elif isinstance(res_data, str):
                        return res_data
                except ValueError:
                    # If response is plain text token instead of JSON
                    if response.text:
                        return response.text.strip('"')
                        
        except requests.exceptions.RequestException as e:
            print(f"[Telebirr Token Exception]: {e}")
            
        return None

    @staticmethod
    def save_ticket(data, token):
        url = "http://192.168.251.39:8010/api/tickets/savetickets"
        
        # Clean token formatting in case Bearer prefix is already present or needed
        auth_header = token if token.startswith("Bearer ") else f"Bearer {token}"
        
        headers = {
            "Authorization": auth_header,
            "x-api-key": "4F10EF34-DE37-4240-B1BF-A8FEAD615AE3",
            "Content-Type": "application/json"
        }
        
        # Transform local keys into Telebirr's expected API schema
        payload = {
            "operator": data.get("operator_id"),
            "routeSchedule": data.get("route_schedule_id"),
            "routeScheduleDate": data.get("travel_date"),
            "paymentMethod": 1,
            "paymentProcessor": 1,
            "paymentAmount": data.get("amount"),
            "paymentStatus": 1,
            "maturityDate": data.get("travel_date"),
            "paymentIssueDate": data.get("travel_date"),
            "appId": 5,
            "ticketDetail": [
                {
                    "pnr": data.get("pnr"),
                    "firstName": data.get("first_name"),
                    "lastName": data.get("last_name"),
                    "phoneNumber": data.get("phone_number"),
                    "gender": 1,
                    "seatLayout": data.get("seat_no"),
                    "isAutoAssigned": False,
                    "subTotal": data.get("amount"),
                    "discount": 0.0,
                    "additionalCharge": 0.0,
                    "grandTotal": data.get("amount")
                }
            ]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            print(f"[Telebirr Save Ticket Status]: {response.status_code}")
            print(f"[Telebirr Save Ticket Body]: {response.text}")
            
            try:
                return response.status_code, response.json()
            except ValueError:
                return response.status_code, response.text
                
        except requests.exceptions.RequestException as e:
            return 500, {"error": str(e)}
