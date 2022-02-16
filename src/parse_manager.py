import argparse

class ParseManager():
    def __init__(self):
        parser = argparse.ArgumentParser(description="Spotify API Scraper Parser")
        parser.add_argument(
            "-p", "--pie-chart",
            required=False,
            default=False,
            action="store_true",
            dest="pie_chart",
            help="If a pie chart should be displayed or not"
        )

        self.args = vars(parser.parse_args())
