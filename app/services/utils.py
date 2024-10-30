import requests

def handle_http_errors(request_function):
    try:
        response = request_function()
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        print(f"An error occurred: {err}")
        raise

import re
from models import Track, Artist

def remove_non_alphabetic(text):
    return re.sub(r'[^A-Za-z]', '', text)