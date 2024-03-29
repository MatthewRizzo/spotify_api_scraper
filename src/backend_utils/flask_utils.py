from typing import List
from flask import Flask, url_for
from werkzeug.routing import Rule
from typing import Dict
import requests

class FlaskUtils():
    app = None
    port = None
    def __init__(self, app: Flask = None, port: int = None) -> None:
        """Class used to implement any helper functions needed for flask that don't directly achieve functionality"""
        self.cls = __class__

        # onyl set the vars if they are not already set
        self.cls.app = app if app is not None else self.cls.app
        self.cls.port = port if port is not None else self.cls.port

    def _get_available_uri(self) -> list:
        """Returns a list of all GET-able endpoints"""
        create_url = lambda endpoint: f"http://localhost:{self.cls.port}{endpoint}"
        available_links = list(map(create_url, self.cls.app.url_map.iter_rules()))
        available_links.sort()
        return available_links

    def get_valid_endpoints(self) -> Dict:
        """Returns a dict of all the valid GET endpoints for this server. starts from / and goes till end.

        """
        create_url = lambda endpoint: f"{endpoint}"
        all_links = list(map(create_url, self.cls.app.url_map.iter_rules()))
        return all_links

    def generate_site_links(self):
        """Make a route that is used to get the available GET links for the server"""
        @self.cls.app.route("/get-site-links")
        def site_links() -> list:
            return self._get_available_uri()

    def print_routes(self) -> None:
        """Print all get-able links served by this app"""
        print("Existing URLs:")
        print("\n".join(self._get_available_uri()))

    @classmethod
    def get_app_base_url_str(cls, port : int) -> str:
        """:pre This class has been instantiated once so app and port are set
        :return the base url for this app (i.e. `http://localhost:port`"""
        base_ip = cls.get_public_ip()
        full_base = base_ip + ":" + str(port)
        return full_base

    @classmethod
    def get_public_ip(cls) -> str:
        """Gets the public / external ip of this device"""
        base = "http://"
        ip_dot_notation = str(requests.get('https://api.ipify.org').content.decode('utf8'))
        return base + ip_dot_notation

    def _has_no_empty_params(self, rule: Rule):
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)
