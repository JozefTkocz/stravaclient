import requests

import stravaclient.constants.endpoints as endpoints
from stravaclient.authorisation import OAuthHandler


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




def get_last_activity():
    pass


def update_activity():
    pass
