from stravaclient.authorisation import OAuthHandler
from stravaclient.endpoint_methods import StravaClient
from stravaclient.models.activity import UpdatableActivity
import json

REQUIRE_USER_AUTHORISATION = False

if __name__ == '__main__':
    athlete_id = 36371430
    # activity_id = 6635782418

    authenticator = OAuthHandler.from_config('authorisation.ini')

    if REQUIRE_USER_AUTHORISATION:
        authenticator.prompt_user_authorisation()

    client = StravaClient(authenticator)

    activities = client.list_activities(athlete_id=athlete_id)
    print(activities)

    activity_id = activities[9]['id']
    print(activity_id)

    an_activity = client.get_activity(athlete_id, activity_id)
    print(an_activity)

    temp_activity = UpdatableActivity.from_activity(an_activity)
    temp_activity.description = 'Strava API update activity endpoint test message.'

    print(temp_activity.to_json())

    print('Getting streamsets...')
    streamset = client.get_activity_stream_set(athlete_id=athlete_id,
                                               activity_id=activity_id,
                                               streams=['time', 'altitude', 'heartrate', 'latlng', 'latlng', 'moving', 'LatLng', 'randomstring', 'lat', 'lng'])

    print()
    print(streamset)

    with open('streamset.json', 'w') as file:
        json.dump(streamset, file)

    # response = client.update_activity(athlete_id, activity_id, temp_activity)
    # print(response)
