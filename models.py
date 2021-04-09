import json
from datetime import datetime
from dataclasses import dataclass, field, asdict


@dataclass
class Message:
    user: str = field(default='')
    value: str = field(default='')

    def __post_init__(self):
        self.datetime = str(datetime.now())
    
    def get(self, attr):
        return getattr(self, attr)

    def dict(self):
        return asdict(self)

    def string(self):
        return json.dumps(asdict(self))
