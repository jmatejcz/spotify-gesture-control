import requests
import base64
import datetime
from urllib.parse import urlencode
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyApi:
    def __init__(self):
        self.client_id = '' # put your spotify app client id
        self.client_secret = '' # put your spotify app client secret
        self.token_url = "https://accounts.spotify.com/api/token"
        self.token_data = {"grant_type": "client_credentials"}
        self.access_token = None
        self.access_token_expires = datetime.datetime.now()
        self.did_access_token_expire = True
        self.base_url = "https://api.spotify.com/v1/"

    def get_client_cred_b64(self):
        client_credentials = f"{self.client_id}:{self.client_secret}"
        client_credentials_b64 = base64.b64encode(client_credentials.encode())
        return client_credentials_b64.decode()

    def get_token_headers(self):
        client_credentials_b64 = self.get_client_cred_b64()
        return {"Authorization": f"Basic {client_credentials_b64}"}

    def authenticate(self):
        scope = "user-modify-playback-state"

        # sp = spotipy.Spotify(auth_manager=SpotifyOAuth(self.client_id, self.client_secret, redirect_uri='https://example.com', scope=scope))
        # sp = spotipy.Spotify()
        # sp.start_playback()

        # auth_code = requests.get('https://accounts.spotify.com/authorize', {
        # 'client_id': self.client_id,
        # 'response_type': 'code',
        # 'redirect_uri': 'https://example.com',
        # 'scope': scope,
        # })
        # print(auth_code)

        # print(r)
        r = requests.post(self.token_url, data=self.token_data, headers=self.get_token_headers())
        print(r.json())
        if r.status_code not in range(200, 299):
            return False
        token_response_data = r.json()
        self.access_token = token_response_data['access_token']
        now = datetime.datetime.now()
        token_expires_in = token_response_data['expires_in']
        self.access_token_expires = now + datetime.timedelta(seconds=token_expires_in)
        self.did_access_token_expire = self.access_token_expires < now
        return True

    def get_access_token(self):
        if self.did_access_token_expire:
            self.authenticate()
        elif self.access_token is None:
            self.authenticate()
        print(self.access_token)
        return self.access_token

    def get_authorization_headers(self):
        return {"Authorization": f"Bearer {self.get_access_token()}"}

    def resume(self):
        # data = urlencode({"q": "Toss a coin to your witcher", "type": "track"})
        # endpoint = self.base_url + "search"
        # lookup_url = f"{endpoint}?{data}"
        # print(lookup_url)
        # r = requests.get(lookup_url, headers=self.get_authorization_headers())
        # r.json()
        # print(r.json())

        endpoint = self.base_url + "me/player/play"
        headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {self.get_access_token()}'}
        response = requests.put(endpoint, headers=headers)
        print(response)


    def pause(self):
        pass

    def skip_left(self):
        pass

    def skip_right(self):
        pass
