from typing import Protocol

import tinydb


class TokenCache(Protocol):
    def upsert_authorisation_token(self, authorisation):
        ...

    def get_authorisation_token(self, athlete_id):
        ...

    def from_config(self, config_file):
        ...


class LocalTokenCache:
    def __init__(self, filename):
        self.database = tinydb.TinyDB(filename)

    def upsert_authorisation_token(self, authorisation):
        athlete_id = authorisation['athlete']['id']
        auth_expiry = authorisation['expires_at']
        auth_access_token = authorisation['access_token']
        auth_refresh_token = authorisation['refresh_token']

        self.database.upsert(tinydb.database.Document(
            {'expires_at': auth_expiry,
             'access_token': auth_access_token,
             'refresh_token': auth_refresh_token},
            doc_id=athlete_id))

    def get_authorisation_token(self, athlete_id):
        return self.database.get(doc_id=athlete_id)

    def from_config(self):
        pass


class DynamoDBCache:
    def __init__(self):
        pass
