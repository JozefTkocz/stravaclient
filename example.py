from stravaclient.authorisation import OAuthHandler
from stravaclient.endpoint_methods import StravaClient
from stravaclient.models.activity import UpdatableActivity
from stravaclient.storage.tokens import LocalTokenCache

REQUIRE_USER_AUTHORISATION = True

YOUR_ATHLETE_ID = None
YOUR_CLIENT_ID = None
YOUR_CLIENT_SECRET = None

if __name__ == '__main__':
    # Create a TokenCache for storing your API access tokens per authorised user. LocalTokenCache persists the data to
    # local file storage. An DynamoDB token cache implements storage in an AWS DynamoDB table. Other storage options can
    # be used, as long as the TokenCache protocol is adhered to.
    token_cache = LocalTokenCache(filename='token_cache')

    # An OAuthHandler is used to store and retrieve tokens from the cache
    authenticator = OAuthHandler(client_id=YOUR_CLIENT_ID,
                                 client_secret=YOUR_CLIENT_SECRET,
                                 token_cache=token_cache)

    # If the token cache is empty, or you don't know your athlete ID, you will need to sign into Strava and authorise
    # its access. The authorisation code should be included in the query string of the redirect uri you supply
    if YOUR_ATHLETE_ID is None:
        athlete_id = authenticator.prompt_user_authorisation(redirect_uri='https://localhost/')
        print(f'Your athlete ID is {athlete_id}')
    else:
        athlete_id = YOUR_ATHLETE_ID

    # The client can now be instantiated, and a number of handy endpoint methods are available.
    client = StravaClient(authenticator)

    # List activities for a given athlete
    activities = client.list_activities(athlete_id=athlete_id)
    print('Your recent activities:')
    print(activities)

    # Download the activity object for the first returned activity
    activity_id = activities[0]['id']
    an_activity = client.get_activity(athlete_id, activity_id)
    print('Your most recent activity:')
    print(an_activity)

    # An UpdatableActivity object model is available for convenient edits to activities on your feed.
    # (Remember to delete this message once you're done!)
    temp_activity = UpdatableActivity.from_activity(an_activity)
    temp_activity.description += '\nStrava API update activity endpoint test message.'
    response = client.update_activity(athlete_id, activity_id, temp_activity)

    # Streamset data can also be downloaded for a given activity
    print(f'Downloading streamsets for activity {activity_id}...')
    streamset = client.get_activity_stream_set(athlete_id=athlete_id,
                                               activity_id=activity_id,
                                               streams=['time', 'altitude', 'heartrate', 'latlng', 'latlng', 'moving',
                                                        'LatLng', 'randomstring', 'lat', 'lng'])
    print(streamset)
