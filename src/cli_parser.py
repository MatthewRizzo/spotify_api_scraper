#------------------------------STANDARD DEPENDENCIES-----------------------------#
import argparse
import os


class CLIParser():
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Spotify API Scraper Parser")
        self.create_expected_params()

        self.args = vars(self.parser.parse_args())

    def create_expected_params(self):
        """@post: the `parse_args()` can be called"""
        env_port = os.environ.get("PORT")
        self.parser.add_argument(
            "-p", "--port",
            type=int,
            required=False,
            help="The port The Web App is run from",
            default=env_port if env_port is not None else 8080,
            dest="port"
        )

        # debugMode will default to false - only true when the flag exists
        self.parser.add_argument(
            "--debugModeOn",
            action="store_true",
            dest="debugMode",
            required=False,
            help="Use debug mode for development environments",
            default=False
        )
        self.parser.add_argument(
            "--debugModeOff",
            action="store_false",
            dest="debugMode",
            required=False,
            help="Dont use debug mode for production environments",
            default=True
        )
