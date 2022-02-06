from stravaclient.authorisation import OAuthHandler
from stravaclient.endpoint_methods import StravaClient
from stravaclient.models.activity import UpdatableActivity

REQUIRE_USER_AUTHORISATION = False

if __name__ == '__main__':
    athlete_id = 36371430

    oauth = OAuthHandler.from_config('authorisation.ini')

    if REQUIRE_USER_AUTHORISATION:
        oauth.prompt_user_authorisation()

    client = StravaClient(oauth)

    #data = client.get_athlete_info(athlete_id)
    #print(data)

    #data = client.list_activities(athlete_id)
    #print(data)

    an_activity = client.get_activity(athlete_id, 6635782418)
    print(an_activity)

    temp_activity = UpdatableActivity.from_activity(an_activity)
    temp_activity.description = 'Strava API update activity endpoint test  message.'

    response = client.update_activity(athlete_id, 6635782418, temp_activity)
    print(response)