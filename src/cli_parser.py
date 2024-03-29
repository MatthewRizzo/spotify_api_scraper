#------------------------------STANDARD DEPENDENCIES-----------------------------#
import argparse
import os

#------------------------------Project Imports-----------------------------#
import constants

class CLIParser():
    def __init__(self):
        self.parser = argparse.ArgumentParser(description=constants.PROJECT_NAME)
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
            default=env_port if env_port is not None else 53689,
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

        self.parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            default=False,
            dest="verbose",
            help="Set this flag to have more information get printed"
        )

        self.parser.add_argument(
            "-l", "--localhost",
            action="store_true",
            default=False,
            dest="redirect_localhost",
            help="Set this flag to have the redirect url after authroziation be localhost instead of an actual IP"
        )
