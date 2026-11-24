# Keys jodne ke steps (24 Nov 2026) — repo Settings > Secrets and variables > Actions > New repository secret

## 1. YouTube asli views (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN) — sabse zaroori
1. console.cloud.google.com -> naya project -> "APIs & Services" -> Library -> "YouTube Data API v3" aur "YouTube Analytics API" dono Enable.
2. OAuth consent screen -> External -> apna Gmail test user. Phir "Publish app" (In production) kar do, warna refresh token 7 din mein mar jaata hai.
3. Credentials -> Create credentials -> OAuth client ID -> Web application -> Authorized redirect URI: https://developers.google.com/oauthplayground -> Client ID aur Client secret copy.
4. developers.google.com/oauthplayground -> gear icon -> "Use your own OAuth credentials" -> ID/secret daalo -> scopes: youtube.readonly, yt-analytics.readonly, youtube.upload (aur youtube agar title badalna ho) -> Authorize (Katha Chitra wale Google account se) -> "Exchange authorization code for tokens" -> Refresh token copy.
5. Teeno GitHub secret mein daalo.

## 2. ElevenLabs (ELEVENLABS_API_KEY)
elevenlabs.io -> profile -> API Keys -> Create -> copy -> secret. Dhyan: library ki famous awaazein API se free plan par nahi chalti, paid plan lagta hai (jaanch lena).

## 3. Tyohar tarikh (GCAL_API_KEY)
Wahi Google Cloud project -> Library -> "Google Calendar API" Enable -> Credentials -> API key -> secret. Calendar: en.indian#holiday@group.v.calendar.google.com

## 4. Instagram (IG_ACCESS_TOKEN, IG_USER_ID)
@kathachitra56 ko Professional (Creator/Business) account karo -> Facebook Page se jodo -> developers.facebook.com par app -> Instagram Graph API -> lamba token + Instagram user id.

Jodne ke baad `python tools/tool_check.py` ya agle roz ke report mein ✅ dikhna chahiye.
