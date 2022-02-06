import time
import configparser
import requests
import tinydb

import stravaclient.constants.endpoints as endpoints


class OAuthHandler:
    def __init__(self, client_id, client_secret, database_location):
        self.client_id = client_id
        self.client_secret = client_secret
        self.database = tinydb.TinyDB(database_location)

    @classmethod
    def from_config(cls, filepath):
        config_parser = configparser.ConfigParser()
        auth_config = config_parser.read(filepath)
        return cls(int(config_parser['Authentication']['client_id']),
                   config_parser['Authentication']['client_secret'],
                   config_parser['Authentication']['database'])

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
        self.upsert_authorisation_database(authorisation)

    def upsert_authorisation_database(self, authorisation):
        athlete_id = authorisation['athlete']['id']
        auth_expiry = authorisation['expires_at']
        auth_access_token = authorisation['access_token']
        auth_refresh_token = authorisation['refresh_token']

        self.database.upsert(tinydb.database.Document(
            {'expires_at': auth_expiry,
             'access_token': auth_access_token,
             'refresh_token': auth_refresh_token},
            doc_id=athlete_id))

    def refresh_access_token(self, athlete_id: int, refresh_token: str):
        params = {'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'grant_type': 'refresh_token',
                  'refresh_token': refresh_token}
        authorisation = requests.post(endpoints.oauth_token, data=params).json()
        authorisation.update({'athlete': {'id': athlete_id}})
        self.upsert_authorisation_database(authorisation)

    def generate_authorisation_header(self, athlete_id: int):
        auth_db = tinydb.TinyDB('authorisation.json')
        auth_data = auth_db.get(doc_id=athlete_id)

        token_expires_at = auth_data['expires_at']
        current_epoch_time = int(time.time())

        if current_epoch_time > token_expires_at:
            refresh_token = auth_data['refresh_token']
            self.refresh_access_token(athlete_id, refresh_token)
            auth_data = auth_db.get(doc_id=athlete_id)

        token = auth_data['access_token']
        return {'Authorization': f'Bearer {token}'}
