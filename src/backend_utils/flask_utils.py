from flask import Flask, url_for


class FlaskUtils():
    def __init__(self, app: Flask, port: int) -> None:
        """Class used to implement any helper functions needed for flask that don't directly achieve functionality"""
        self.app = app
        self.port = port

    def _get_available_uri(self) -> list:
        """Returns a list of all GET-able endpoints"""
        create_url = lambda endpoint: f"http://localhost:{self.port}{endpoint}"
        available_links = list(map(create_url, self.app.url_map.iter_rules()))
        available_links.sort()
        return available_links

    def generate_site_links(self):
        """Make a route that is used to get the available GET links for the server"""
        @self.app.route("get-site-links")
        def site_links() -> list:
            return self._get_available_uri()

    def print_routes(self) -> None:
        """Print all get-able links served by this app"""
        print("Existing URLs:")
        print("\n".join(self._get_available_uri()))
