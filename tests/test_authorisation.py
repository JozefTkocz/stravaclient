from stravaclient.authorisation import OAuthHandler
from unittest.mock import MagicMock


class MockTokenCache:
    def __init__(self):
        self.authorisation = None

    def upsert_authorisation_token(self, authorisation):
        self.authorisation = authorisation
        return None

    def get_authorisation_token(self, athlete_id):
        return self.authorisation


def test_refresh_access_token_updates_refresh_token():
    # Instantiate a token store
    mock_token_cache = MockTokenCache()
    mock_token_cache.upsert_authorisation_token(authorisation={'athlete': {'id': 123},
                                                               'expires_at': 1,
                                                               'access_token': 'abc',
                                                               'refresh_token': 'abc123'})
    auth_handler = OAuthHandler(client_id=123, client_secret='mock_secret', token_cache=mock_token_cache)

    # Mock out a request for a refreshed token
    auth_handler._get_authorisation_token = MagicMock(return_value={'athlete': {'id': 123},
                                                                    'expires_at': 10,
                                                                    'access_token': 'abc',
                                                                    'refresh_token': 'xyz'})

    # check that the refreshed token is used, not the older one
    auth_handler.refresh_access_token(athlete_id=123, refresh_token='abc123')
    assert auth_handler.current_refresh_token == 'xyz'


def test_pull_token_data_from_cache_returns_cache_data():
    mock_token_cache = MockTokenCache()
    mock_token_cache.upsert_authorisation_token(authorisation={'athlete': {'id': 123},
                                                               'expires_at': 1,
                                                               'access_token': 'abc',
                                                               'refresh_token': 'abc123'})
    auth_handler = OAuthHandler(client_id=123, client_secret='mock_secret', token_cache=mock_token_cache)
    auth_handler.pull_token_data_from_cache(athlete_id=123)

    assert auth_handler.current_token == 'abc'
    assert auth_handler.current_token_expiry == 1
    assert auth_handler.current_refresh_token == 'abc123'


def test_generate_authorisation_header_when_token_expired():
    # Instantiate a token store
    mock_token_cache = MockTokenCache()
    mock_token_cache.upsert_authorisation_token(authorisation={'athlete': {'id': 123},
                                                               'expires_at': 1,
                                                               'access_token': 'abc',
                                                               'refresh_token': 'abc123'})

    auth_handler = OAuthHandler(client_id=123, client_secret='mock_secret', token_cache=mock_token_cache)

    # Mock out the refresh token request
    auth_handler._get_authorisation_token = MagicMock(return_value={'athlete': {'id': 123},
                                                                    'expires_at': 10,
                                                                    'access_token': 'abc_refreshed',
                                                                    'refresh_token': 'abc123_refreshed'})

    # 2 is later than the initial current time of 1, so the token is expired and must be refreshed
    auth_handler._current_time = MagicMock(return_value=2)

    # Check that a correct header is generated, and that it reflects the refreshed token
    header = auth_handler.generate_authorisation_header(athlete_id=123)
    assert header == {'Authorization': f'Bearer abc_refreshed'}


def test_generate_authorisation_header_when_token_not_expired():
    # Instantiate a token store
    mock_token_cache = MockTokenCache()
    mock_token_cache.upsert_authorisation_token(authorisation={'athlete': {'id': 123},
                                                               'expires_at': 1,
                                                               'access_token': 'abc',
                                                               'refresh_token': 'abc123'})

    auth_handler = OAuthHandler(client_id=123, client_secret='mock_secret', token_cache=mock_token_cache)

    # Mock out the refresh token request
    auth_handler._get_authorisation_token = MagicMock(return_value={'athlete': {'id': 123},
                                                                    'expires_at': 10,
                                                                    'access_token': 'abc_refreshed',
                                                                    'refresh_token': 'abc123_refreshed'})

    # 1 is the same as the current expiry time, so the current token is valid and no refresh is needed
    auth_handler._current_time = MagicMock(return_value=1)

    # Check that a correct header is generated, and that it reflects the refreshed token
    header = auth_handler.generate_authorisation_header(athlete_id=123)
    assert header == {'Authorization': f'Bearer abc'}
