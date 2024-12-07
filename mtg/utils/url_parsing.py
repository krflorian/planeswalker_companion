import requests
from urllib.parse import urljoin


def parse_card_names(text, url, endpoint):
    request = {"text": text}
    response = requests.post(urljoin(url, endpoint), json=request)
    if response.status_code == 200:
        response = response.json()
        return response["text"]
    return text
