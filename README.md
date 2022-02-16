# spotify_api_scraper
Utilizes Spotify's API for devs to analyze playlists and viewing habits. Personal / for fun project because I use spotify so much

## TODO:
* break down a playlist
  * into percentages of a given artist - make a pie chart or some nice graphic
  * find way to cross reference song titles to get theri genre and make genre pie chart
  *


## Setup Notes:
1. This scrapper requires your Spotify account to have access to the Developer API's
  * To do this, sign up for an app as directed here: https://developer.spotify.com/documentation/general/guides/authorization/app-settings/
  * **Create an application** - https://developer.spotify.com/dashboard/applications
  * *Maybe*: Add a user to your application - your user
2. Copy the template provided by [data/default_app_auth.json](data/default_app_auth.json) into `data/app_auth.json`
   1. **THIS IS IMPORTANT**. The application will search for this file. If it does not exist, you will be prompted to create it.
   2. Replace the default values with those associated with your Application
      1. see: https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
      2. client_id = client id of your new registered application
3. Run the install script at [install/install.sh](install/install.sh)
4.
