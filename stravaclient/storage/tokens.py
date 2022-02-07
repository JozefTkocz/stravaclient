from typing import Protocol

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
    def upsert_authorisation_token(self, authorisation):
        ...

    def get_authorisation_token(self, athlete_id):
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


class DynamoDBCache:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name, table_name):
        self.dynamodb_client = boto3.resource('dynamodb',
                                              region_name=region_name,
                                              aws_access_key_id=aws_access_key_id,
                                              aws_secret_access_key=aws_secret_access_key)
        self.table = self.dynamodb_client.Table(table_name)

    def upsert_authorisation_token(self, authorisation):
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

    def get_authorisation_token(self, athlete_id):
        try:
            response = self.table.get_item(Key={'athlete_id': str(athlete_id)})
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            data = response['Item']
            expires_at = int(data['expires_at'])
            athlete_id = int(data['athlete_id'])

            data.update({'expires_at': expires_at,
                         'athlete_id': athlete_id})

            return data
