import logging
from typing import Protocol, Dict
import boto3
import tinydb
from botocore.exceptions import ClientError


def build_local_db_token_cache(filename, **_ignored):
    return LocalTokenCache(filename=filename)


def build_dynamodb_token_cache(aws_access_key_id, aws_secret_access_key, region_name, table_name, **_ignored):
    return DynamoDBCache(aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name=region_name,
                         table_name=table_name)


class TokenCacheFactory:
    def build(self, type: str, **kwargs):
        construction_method = {
            'dynamodb': build_dynamodb_token_cache,
            'local': build_local_db_token_cache
        }.get(type)

        return construction_method(**kwargs)


class TokenCache(Protocol):
    def upsert_authorisation_token(self, authorisation: Dict):
        ...

    def get_authorisation_token(self, athlete_id: int) -> Dict:
        ...

    def delete_authorisation_token(self, athlete_id: int):
        ...

    def total_tokens(self) -> int:
        ...


class LocalTokenCache:
    def __init__(self, filename: str):
        self.database = tinydb.TinyDB(filename)

    def upsert_authorisation_token(self, authorisation: Dict):
        athlete_id = authorisation['athlete']['id']
        auth_expiry = authorisation['expires_at']
        auth_access_token = authorisation['access_token']
        auth_refresh_token = authorisation['refresh_token']

        self.database.upsert(tinydb.database.Document(
            {'expires_at': auth_expiry,
             'access_token': auth_access_token,
             'refresh_token': auth_refresh_token},
            doc_id=athlete_id))

    def get_authorisation_token(self, athlete_id: int) -> Dict:
        return self.database.get(doc_id=athlete_id)

    def delete_authorisation_token(self, athlete_id: int):
        self.database.remove(doc_ids=[athlete_id])

    @property
    def total_tokens(self) -> int:
        return len(self.database)


class DynamoDBCache:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name, table_name):
        self.dynamodb_client = boto3.resource('dynamodb',
                                              region_name=region_name,
                                              aws_access_key_id=aws_access_key_id,
                                              aws_secret_access_key=aws_secret_access_key)
        self.table = self.dynamodb_client.Table(table_name)

    def upsert_authorisation_token(self, authorisation: Dict):
        athlete_id = authorisation['athlete']['id']
        auth_expiry = authorisation['expires_at']
        auth_access_token = authorisation['access_token']
        auth_refresh_token = authorisation['refresh_token']

        response = self.table.put_item(
            Item={
                'athlete_id': str(athlete_id),
                'access_token': auth_access_token,
                'expires_at': str(auth_expiry),
                'refresh_token': auth_refresh_token
            }
        )

    def get_authorisation_token(self, athlete_id: int) -> Dict:
        try:
            response = self.table.get_item(Key={'athlete_id': str(athlete_id)})
        except ClientError as e:
            logging.error('Failed to retrieve access token')
            logging.error(e.response['Error']['Message'])
        else:
            data = response['Item']
            expires_at = int(data['expires_at'])
            athlete_id = int(data['athlete_id'])

            data.update({'expires_at': expires_at,
                         'athlete_id': athlete_id})

            return data

    def delete_authorisation_token(self, athlete_id: int):
        try:
            self.table.delete_item(Key={'athlete_id': str(athlete_id)})
        except ClientError as e:
            logging.error(f'Failed to remove athlete {athlete_id}')
            logging.error(e.response['Error']['Message'])

    @property
    def total_tokens(self) -> int:
        return self.table.item_count
