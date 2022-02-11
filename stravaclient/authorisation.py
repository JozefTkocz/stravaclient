import configparser
import time

import requests

import stravaclient.constants.endpoints as endpoints
from stravaclient.storage.tokens import TokenCache, TokenCacheFactory


class OAuthHandler:
    def __init__(self, client_id: int, client_secret: str, token_cache: TokenCache):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_cache = token_cache

        self.current_token = None
        self.current_token_expiry = None
        self.current_refresh_token = None

    @classmethod
    def from_config(cls, filepath):
        config_parser = configparser.ConfigParser()
        auth_config = config_parser.read(filepath)

        token_cache_type = config_parser['TokenCache']['type']

        token_cache = TokenCacheFactory.build(token_cache_type, **config_parser['TokenCache'])

        return cls(int(config_parser['Credentials']['client_id']),
                   config_parser['Credentials']['client_secret'],
                   token_cache)

    def prompt_user_authorisation(self):
        scope = 'read_all,activity:read_all,activity:write'
        # prompt the user to provide access
        print('Retrieve Auth code from URL:')
        code_request_url = f'{endpoints.oauth_authorisation}?client_id={self.client_id}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope={scope}'
        print(code_request_url)
        authorisation_code = input('Enter authorisation code: ')

        params = {'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'code': authorisation_code,
                  'grant_type': 'authorization_code'}

        response = requests.post(endpoints.oauth_token, data=params)

        authorisation = response.json()
        self.token_cache.upsert_authorisation_token(authorisation)

    def refresh_access_token(self, athlete_id: int, refresh_token: str):
        params = {'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'grant_type': 'refresh_token',
                  'refresh_token': refresh_token}
        authorisation = requests.post(endpoints.oauth_token, data=params).json()
        authorisation.update({'athlete': {'id': athlete_id}})
        self.token_cache.upsert_authorisation_token(authorisation)

        self.current_token = authorisation['access_token']
        self.current_token_expiry = authorisation['expires_at']
        self.current_refresh_token = authorisation['refresh_token']

    def generate_authorisation_header(self, athlete_id: int):
        if self.current_token is None:
            self.pull_token_data_from_cache(athlete_id)

        # auth_data = self.token_cache.get_authorisation_token(athlete_id)

        # token_expires_at = auth_data['expires_at']
        current_epoch_time = int(time.time())

        if current_epoch_time > self.current_token_expiry:
            refresh_token = self.current_refresh_token
            self.refresh_access_token(athlete_id, refresh_token)
            # auth_data = self.token_cache.get_authorisation_token(athlete_id)

        # token = auth_data['access_token']
        return {'Authorization': f'Bearer {self.current_token}'}

    def pull_token_data_from_cache(self, athlete_id):
        auth_data = self.token_cache.get_authorisation_token(athlete_id)
        self.current_token = auth_data['access_token']
        self.current_token_expiry = auth_data['expires_at']
        self.current_refresh_token = auth_data['refresh_token']
