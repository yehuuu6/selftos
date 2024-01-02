"""\
This module provides the necessary client classes for your Selftos chat application.
"""

from socket import socket
import json

class User:
    def __init__(self, id: str, name: str, client: socket):
        self.id = id
        self.name = name
        self.client = client
    
    def get_json(self) -> str:
        data = {
            "id": self.id,
            "name": self.name,
        }
        return json.dumps(data)