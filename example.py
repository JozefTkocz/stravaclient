from stravaclient.authorisation import OAuthHandler
from stravaclient.endpoint_methods import StravaClient
from stravaclient.models.activity import UpdatableActivity

REQUIRE_USER_AUTHORISATION = False

if __name__ == '__main__':
    athlete_id = 36371430

    authenticator = OAuthHandler.from_config('authorisation.ini')

    if REQUIRE_USER_AUTHORISATION:
        authenticator.prompt_user_authorisation()

    client = StravaClient(authenticator)

    an_activity = client.get_activity(athlete_id, 6635782418)
    print(an_activity)

    temp_activity = UpdatableActivity.from_activity(an_activity)
    temp_activity.description = 'Strava API update activity endpoint test  message.'

    response = client.update_activity(athlete_id, 6635782418, temp_activity)
    print(response)
