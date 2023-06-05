from common_fetch_strategy import ResponseType, Strategy
import requests


class RequestsStrategy(Strategy):
    async def fetch(self, url, headers):
        response = requests.get(url, headers=headers)
        return response.json()
