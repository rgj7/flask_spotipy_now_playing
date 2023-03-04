# flask_spotipy_now_playing

A simple Flask app to expose an endpoint to display a logged-in user's currently played song.

1. You will need to register an app at [Spotify for Developers](https://developer.spotify.com) in order to generate a Client ID and Client Secret. Redirect URI will also need to point to the `/callback` endpoint. Because your app will be in development mode, you will also need to manually add the e-mail addresses of the users using your app in the 'Users and Access' section of the Spotify Dashboard.

2. Install requirements and configure your environment variables (see `.env.example`)
```shell
> pip install -r requirements.txt
> python main.py
```

3. Launch the app to see a sign-in link which will ask for authorization via the Spotify Accounts service. Once you're signed in, a randomized endpoint will be created for you. 

4. This endpoint will display your current song and can be called via a Twitch chat bot, for example.

```
# streamelements custom bot command
${urlfetch http://www.yoursite.com/spotify/currently_playing/PgGE2r5}
```

### Notes:
- I made this primarily for my streaming friends to add a !song command without having to download any scrobbling software.
- Sessions should be persistent for a year. Signing out will remove your tokens and session. Logging back in will create a new endpoint.
- Currently uses Redis to store access and refresh tokens, though it could be modified to use any database.
