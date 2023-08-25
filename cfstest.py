from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key")

# Set up OAuth with Google as the OID provider
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id='your-google-client-id',
    client_secret='your-google-client-secret',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:5000/callback',
    client_kwargs={'scope': 'openid profile email'},
)

@app.route('/')
def index():
    if 'user' in session:
        return f'Hello, {session["user"]["name"]}! <a href="/logout">Logout</a>'
    return 'Hello, guest! <a href="/login">Login with Google</a>'

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/auth')
def auth():
    oauth.google.authorize_access_token()
    user_info = oauth.google.get('userinfo')
    session['user'] = user_info.json()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
