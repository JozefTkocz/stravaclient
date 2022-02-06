import requests
import stravaclient.constants.endpoints as endpoints
from stravaclient.authorisation import OAuthHandler

REQUIRE_USER_AUTHORISATION = False

if __name__ == '__main__':
    # request access token
    athlete_id = 36371430

    

    if REQUIRE_USER_AUTHORISATION:
        oauth.prompt_user_authorisation()

    auth_header = oauth.generate_authorisation_header(athlete_id)

    print('requesting athlete data...')
    response = requests.get(endpoints.athlete_info, headers=auth_header)

    print(response.status_code)
    print(response.text)
