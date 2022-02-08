class UpdatableActivity:
    def __init__(self,
                 commute: bool,
                 trainer: bool,
                 hide_from_home: bool,
                 description: str,
                 name: str,
                 type: str,
                 gear_id: str):
        self.commute = commute
        self.trainer = trainer
        self.hide_from_home = hide_from_home
        self.description = description
        self.name = name
        self.type = type
        self.gear_id = gear_id

    @classmethod
    def from_activity(cls, activity):
        return cls(bool(activity['commute']),
                   bool(activity['trainer']),
                   bool(activity['hide_from_home']),
                   activity['description'],
                   activity['name'],
                   activity['type'],
                   activity['gear_id'])

    def to_json(self):
        return {
            'commute': self.commute,
            'trainer': self.trainer,
            'hide_from_home': self.hide_from_home,
            'description': self.description,
            'name': self.name,
            'type': self.type,
            'gear_id': self.gear_id
        }