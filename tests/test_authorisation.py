from stravaclient.authorisation import OAuthHandler
from unittest.mock import MagicMock


class MockTokenCache:
    def __init__(self):
        self.authorisation = None

    def upsert_authorisation_token(self, authorisation):
        return None

    def get_authorisation_token(self, athlete_id):
        return self.authorisation


def test_refresh_access_token_updates_refresh_token():
    mock_token_cache = MockTokenCache()
    mock_token_cache.upsert_authorisation_token(authorisation={'athlete': {'id': 123},
                                                               'expires_at': 1,
                                                               'access_token': 'abc',
                                                               'refresh_token': 'abc123'})
    auth_handler = OAuthHandler(client_id=123, client_secret='mock_secret', token_cache=mock_token_cache)
    auth_handler._get_authorisation_token = MagicMock(return_value={'athlete': {'id': 123},
                                                                    'expires_at': 10,
                                                                    'access_token': 'abc',
                                                                    'refresh_token': 'xyz'})

    auth_handler.refresh_access_token(athlete_id=123, refresh_token='abc123')
    assert auth_handler.current_refresh_token == 'xyz'


def test_pull_token_data_from_cache():
    pass


def test_generate_authorisation_header():
    pass
