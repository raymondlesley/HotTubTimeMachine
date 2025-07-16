"""
Bestway exceptions
"""

# =====================================)
# Exceptions

class InvalidToken(Exception):
    def __init__(self):
        super().__init__('Token expired')

class InvalidArgument(Exception):
    def __init__(self, message):
        super().__init__(message)

class UnknownDevice(Exception):
    def __init__(self, id):
        super().__init__(f"Unknown device: {id}")

class UnsupportedDevice(Exception):
    def __init__(self):
        super().__init__('Unsupported device')

class DeviceOffline(Exception):
    def __init__(self):
        super().__init__('Device offline')
