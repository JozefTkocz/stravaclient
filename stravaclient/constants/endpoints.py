base_url = 'http://www.strava.com'

oauth_authorisation = base_url + '/oauth/authorize'
oauth_token = base_url + '/oauth/token'

athlete_info = base_url + '/api/v3/athlete'
athlete_activities = athlete_info + '/activities'


def activity(activity_id):
    return base_url + f'/api/v3/activities/{activity_id}'
