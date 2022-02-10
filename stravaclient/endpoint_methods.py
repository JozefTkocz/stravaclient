import requests

import stravaclient.constants.endpoints as endpoints
from stravaclient.authorisation import OAuthHandler
from stravaclient.models.activity import UpdatableActivity


class StravaClient:
    def __init__(self, authorisation: OAuthHandler):
        self.authorisation = authorisation

    def get_athlete_info(self, athlete_id):
        auth_header = self.authorisation.generate_authorisation_header(athlete_id)
        response = requests.get(endpoints.athlete_info, headers=auth_header)
        return response.json()

    def list_activities(self, athlete_id):
        auth_header = self.authorisation.generate_authorisation_header(athlete_id)
        response = requests.get(endpoints.athlete_activities, headers=auth_header)
        return response.json()

    def get_activity(self, athlete_id, activity_id):
        auth_header = self.authorisation.generate_authorisation_header(athlete_id)
        response = requests.get(endpoints.activity(activity_id), headers=auth_header)
        return response.json()

    def update_activity(self, athlete_id, activity_id, updatable_activity: UpdatableActivity):
        auth_header = self.authorisation.generate_authorisation_header(athlete_id)
        response = requests.put(endpoints.activity(activity_id), headers=auth_header, data=updatable_activity.to_json())
        return response.json()

    def get_activity_stream_set(self, athlete_id, activity_id, streams):
        auth_header = self.authorisation.generate_authorisation_header(athlete_id=athlete_id)
        stream_keys_string = ''
        for key in streams:
            stream_keys_string += f'{key},'
        stream_keys_string = stream_keys_string[:-1]

        params = {'keys': stream_keys_string,
                  'key_by_type': 'true'}
        print(params)
        response = requests.get(endpoints.activity_streams(activity_id), headers=auth_header, params=params)
        print(response.text)
        return response.json()
