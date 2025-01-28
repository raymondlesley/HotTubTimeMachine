import json

DEFAULT_CONFIG = {
    "username": "unset",
    "password": "NONE",
    "token": {},
}

class Configuration:
    """Abstraction of persisted configuration"""

    def __init__(self, config_json=dict()):
        self.__dict__ = config_json

    def __repr__(self):
        return json.dumps(self.__dict__)

    def fromJson(self, config_json):
        self.__dict__ = json.loads(config_json)

    @classmethod
    def fromFile(self, filename):
        try:
            with open(filename) as json_data:
                return Configuration(json.load(json_data))
        except FileNotFoundError:
            # default configuration
            return Configuration(DEFAULT_CONFIG)


    def toFile(self, filename):
        with open(filename, 'w') as json_data:
            json.dump(self.__dict__, json_data, indent=2)

    def __getitem__(self, item):
        return self.__dict__.get(item)

    def getConfiguration(self):
        return self.__dict__
