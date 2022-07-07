from dataclasses import dataclass


@dataclass
class UpdatableActivity:
    commute: bool
    trainer: bool
    hide_from_home: bool
    description: str
    name: str
    type: str
    gear_id: str

    @classmethod
    def from_activity(cls, activity):
        return cls(activity['commute'],
                   activity['trainer'],
                   activity['hide_from_home'],
                   activity['description'],
                   activity['name'],
                   activity['type'],
                   activity['gear_id'])

    def to_dict(self):
        return {'commute': self.commute,
                'trainer': self.trainer,
                'hide_from_home': self.hide_from_home,
                'description': self.description,
                'name': self.name,
                'type': self.type,
                'gear_id': self.gear_id}
