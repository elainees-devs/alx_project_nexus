import requests
from django.conf import settings


class ChapaAPI:
    def __init__(self):
        self.base_url = settings.CHAPA_BASE_URL
        self.secret_key = settings.CHAPA_SECRET_KEY
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    def initialize_payment(self, amount, currency, email, first_name, last_name, phone_number, tx_ref, callback_url, return_url, customization=None):
        url = f"{self.base_url}transaction/initialize"
        payload = {
            "amount": str(amount),
            "currency": currency,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "tx_ref": tx_ref,
            "callback_url": callback_url,
            "return_url": return_url,
            "customization": customization
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def verify_payment(self, tx_ref):
        url = f"{self.base_url}transaction/verify/{tx_ref}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
