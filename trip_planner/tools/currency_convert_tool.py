import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

class CurrencyTool:
    """
    Tool to convert amounts between currencies using exchangerate.host API (paid, requires access_key).
    """

    def __init__(self):
        self.api_key = os.getenv("CURRENCY_API_KEY")  # Read from .env
        if not self.api_key:
            raise ValueError("CURRENCY_API_KEY not set in .env file")
        self.base_url = "https://api.exchangerate.host/convert"

    def convert(self, amount: float, from_currency: str, to_currency: str) -> dict:
        """
        Convert amount from one currency to another.
        """
        params = {
            "from": from_currency.upper(),
            "to": to_currency.upper(),
            "amount": amount,
            "access_key": self.api_key
        }

        response = requests.get(self.base_url, params=params)
        data = response.json()

        if not data.get("success", False):
            raise Exception(f"Currency API error: {data}")

        return {
            "amount": amount,
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "converted_amount": round(data["result"], 2),
            "rate": round(data["info"]["quote"], 4)
        }