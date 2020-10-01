import base64
from dotenv import load_dotenv
import os
from request_funcs import post_request

load_dotenv()
BASE_URL = 'https://accounts.spotify.com/api/token'
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')


def get_bearer_token():
    # Return bearer token for Spotify api
    auth_str = f'{CLIENT_ID}:{CLIENT_SECRET}'
    b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()

    headers = {'Authorization': f'Basic {b64_auth_str}'}
    body = {'grant_type': 'client_credentials'}

    r = post_request(BASE_URL, headers=headers, body=body)
    return r.json()['access_token']


if __name__ == "__main__":
    print(get_bearer_token())
