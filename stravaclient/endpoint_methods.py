import pandas as pd
import numpy as np
import requests
from typing import List, Dict, Union

import stravaclient.constants.endpoints as endpoints
from stravaclient.authorisation import OAuthHandler
from stravaclient.models.activity import UpdatableActivity


class StravaClient:
    def __init__(self, authorisation: OAuthHandler):
        self.authorisation = authorisation

    def get_athlete_info(self, athlete_id: int) -> Dict:
        auth_header = self.authorisation.generate_authorisation_header(athlete_id)
        response = requests.get(endpoints.athlete_info, headers=auth_header)
        return response.json()

    def list_activities(self, athlete_id: int, page: int = 1, per_page: int = 30) -> Dict:
        request_params = {'page': page,
                          'per_page': per_page}

        auth_header = self.authorisation.generate_authorisation_header(athlete_id)
        response = requests.get(endpoints.athlete_activities, headers=auth_header, params=request_params)
        return response.json()

    def get_activity(self, athlete_id: int, activity_id: int) -> Dict:
        auth_header = self.authorisation.generate_authorisation_header(athlete_id)
        response = requests.get(endpoints.activity(activity_id), headers=auth_header)
        return response.json()

    def update_activity(self, athlete_id, activity_id, updatable_activity: UpdatableActivity) -> Dict:
        auth_header = self.authorisation.generate_authorisation_header(athlete_id)
        response = requests.put(endpoints.activity(activity_id), headers=auth_header, json=updatable_activity.to_dict())
        return response.json()

    def get_activity_stream_set(self, athlete_id: int, activity_id: int, streams: List[str],
                                as_df: bool = False) -> Union[Dict, pd.DataFrame]:
        if as_df:
            activity_json = self.get_activity_stream_set(athlete_id=athlete_id,
                                                         activity_id=activity_id,
                                                         streams=streams,
                                                         as_df=False)
            return self._convert_streamset_to_pandas(activity_json)

        auth_header = self.authorisation.generate_authorisation_header(athlete_id=athlete_id)
        stream_keys_string = ''
        for key in streams:
            stream_keys_string += f'{key},'
        stream_keys_string = stream_keys_string[:-1]

        params = {'keys': stream_keys_string,
                  'key_by_type': 'true'}
        response = requests.get(endpoints.activity_streams(activity_id), headers=auth_header, params=params)
        return response.json()

    @staticmethod
    def _convert_streamset_to_pandas(streamset: Dict) -> pd.DataFrame:
        columns = streamset.keys()
        df = pd.DataFrame()
        for col in columns:
            df[col] = streamset[col]['data']

        if 'latlng' in streamset.keys():
            lat = np.array(streamset['latlng']['data'])[:, 0]
            lng = np.array(streamset['latlng']['data'])[:, 1]
            df['lat'] = lat
            df['lng'] = lng
            df.drop(columns=['latlng'], inplace=True)

        return df
