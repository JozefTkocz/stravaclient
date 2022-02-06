from stravaclient.authorisation import OAuthHandler
from stravaclient.endpoint_methods import StravaClient

REQUIRE_USER_AUTHORISATION = False

if __name__ == '__main__':
    athlete_id = 36371430

    oauth = OAuthHandler.from_config('authorisation.ini')

    if REQUIRE_USER_AUTHORISATION:
        oauth.prompt_user_authorisation()

    client = StravaClient(oauth)

    data = client.get_athlete_info(athlete_id)
    print(data)

    data = client.list_activities(athlete_id)
    print(data)

    data = client.get_activity(athlete_id, 6635782418)
    print(data)