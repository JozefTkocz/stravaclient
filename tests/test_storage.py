import sre_constants

from stravaclient.storage.tokens import LocalTokenCache, DynamoDBCache
import os
from unittest.mock import MagicMock, patch
from typing import Dict


class TestLocalTokenCache:
    test_db_file = 'test_db_file'

    def teardown_db(cls, cache):
        cache.database.close()
        os.remove(cls.test_db_file)

    def test_total_tokens_returns_zero_when_no_tokens(self):
        cache = LocalTokenCache(self.test_db_file)
        assert cache.total_tokens == 0
        self.teardown_db(cache)

    def test_upsert_auth_token(self):
        authorisation = {'athlete': {'id': 123},
                         'expires_at': 1,
                         'access_token': 'abc',
                         'refresh_token': 'abc123'}

        cache = LocalTokenCache(self.test_db_file)
        cache.upsert_authorisation_token(authorisation=authorisation)
        document = cache.get_authorisation_token(athlete_id='123')
        self.teardown_db(cache)
        assert document == {'access_token': 'abc', 'expires_at': 1, 'refresh_token': 'abc123'}

    def test_get_auth_token_for_non_existing_athlete_returns_none(self):
        cache = LocalTokenCache(self.test_db_file)
        document = cache.get_authorisation_token(athlete_id='non-existend-athlete')
        self.teardown_db(cache)
        assert document is None

    def test_total_tokens_returns_one_when_one_token(self):
        cache = LocalTokenCache(self.test_db_file)
        authorisation = {'athlete': {'id': 123},
                         'expires_at': 1,
                         'access_token': 'abc',
                         'refresh_token': 'abc123'}
        cache.upsert_authorisation_token(authorisation=authorisation)
        assert cache.total_tokens == 1
        self.teardown_db(cache)


class TestDynamoDBCache:
    class MockDynamoTable:
        def __init__(self):
            self.last_item = {}

        def put_item(self, Item: Dict) -> Dict:
            self.last_item = Item
            return {'status': '200'}

        def get_item(self, Key: Dict[str, str]) -> Dict:
            return {'Item': self.last_item}

    class MockBotoResource:
        def __init__(self, *args, **kwargs):
            def mock_table(*args, **kwargs):
                return None

            self.Table = mock_table

    with patch('boto3.resource', new=MockBotoResource):
        cache = DynamoDBCache(aws_access_key_id='mock_access_key',
                              aws_secret_access_key='mock_secret_access_key',
                              region_name='mock_region_name',
                              table_name='mock_table_name')

    cache.table = MockDynamoTable()
    cache.dynamodb_client = MagicMock()

    def test_upsert_auth_token(self):
        authorisation = {'athlete': {'id': 123},
                         'expires_at': 1,
                         'access_token': 'abc',
                         'refresh_token': 'abc123'}

        self.cache.upsert_authorisation_token(authorisation=authorisation)
        document = self.cache.get_authorisation_token(athlete_id='123')
        assert document == {'athlete_id': 123, 'access_token': 'abc', 'expires_at': 1, 'refresh_token': 'abc123'}
