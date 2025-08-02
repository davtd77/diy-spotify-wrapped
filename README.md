# DIY Spotify Wrapped — Custom Spotify Listening Stats Explorer
Overview:
This interactive web app lets users explore their personal Spotify listening data over custom time frames — not just the default "past month," "6 months," or "all time" views offered by Spotify. Inspired by the popular Spotify Wrapped, the app uses the Spotify Web API to create a deeper, more flexible and shareable experience.

## Key Features:

🔐 Secure Spotify Authentication
- Users log in via OAuth to connect their Spotify accounts safely.

🎵 Personal Listening Insights
- View top tracks, artists, genres, and more based on personal playback history.

📆 Flexible Timeframe
- Choose a short/medium/long-term window in which your results are gathered.

## Skills Gained:
*OAuth2 Authorization Flow (Spotify)*
- Successfully built login, callback, and token storage.

*Session handling with FastAPI + Starlette*
- Stored and reused access tokens across requests.

*Ngrok setup for local development*
- Configured HTTPS tunneling for real-world API testing.

*Environment variable management*
- Hid credentials using .env and dotenv.

*API querying & response handling*
- Pulled real user data and parsed JSON in the backend.

