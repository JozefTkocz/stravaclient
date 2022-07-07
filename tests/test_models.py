from stravaclient.models.activity import UpdatableActivity


def test_updateableactivity():
    example_strava_activity = {'commute': False,
                               'trainer': None,
                               'hide_from_home': False,
                               'description': 'some_string',
                               'name': 'activity_name',
                               'type': 'run',
                               'gear_id': 123}
    activity_model = UpdatableActivity.from_activity(example_strava_activity)
    assert activity_model.to_dict() == example_strava_activity
