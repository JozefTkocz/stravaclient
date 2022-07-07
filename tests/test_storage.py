from stravaclient.storage.tokens import LocalTokenCache, DynamoDBCache
import os
from unittest.mock import MagicMock, patch
from typing import Dict


class TestLocalTokenCache:
    test_db_file = 'test_db_file'
    cache = LocalTokenCache(test_db_file)

    @classmethod
    def teardown_class(cls):
        cls.cache.database.close()
        os.remove(cls.test_db_file)

    def test_upsert_auth_token(self):
        authorisation = {'athlete': {'id': 123},
                         'expires_at': 1,
                         'access_token': 'abc',
                         'refresh_token': 'abc123'}

        self.cache.upsert_authorisation_token(authorisation=authorisation)
        document = self.cache.get_authorisation_token(athlete_id='123')
        assert document == {'access_token': 'abc', 'expires_at': 1, 'refresh_token': 'abc123'}

    def test_get_auth_token_for_non_existing_athlete_returns_none(self):
        document = self.cache.get_authorisation_token(athlete_id='non-existend-athlete')
        assert document is None


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
