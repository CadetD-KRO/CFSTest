#!/usr/bin/python3
from flask import Flask, redirect, render_template, request, session, url_for
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'q3jwIK9F8984pUIs4OnaDl'

# OIDC configuration
oauth = OAuth(app)
oidc = oauth.register(
    'oidc',
    client_id='http://oidc_cfstest',
    client_secret='rc9nOYG1MW6Zd5O4iQ0ZEJpb2hfzrhajyC63EC23LiQj',
    authorize_url='https://cfs001.dudleycadet.us/cfs/testusers/',
    authorize_params=None,
    access_token_url='OIDC-token-url',
    access_token_params=None,
    userinfo_endpoint='OIDC-userinfo-url',
    client_kwargs={'scope': 'openid profile email'}
)

# Simulated user database
users = {
    'testuser001@cadet-lab.dudleycadet.us': {'name': 'testuser001', 'password': 'password1'},
    'testuser002@cadet-lab.dudleycadet.us': {'name': 'testuser002', 'password': 'password2'}
}

@app.route('/')
def index():
    if 'user' in session:
        return f'Hello, {session["user"]["name"]}! <a href="/logout">Logout</a>'
    return 'Hello, guest! <a href="/login">Login with OIDC</a>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Validate the user's credentials
        if email in users and users[email]['password'] == password:
            return oidc.authorize_redirect(redirect_uri=url_for('oidc_callback', _external=True))
        else:
            return 'Invalid credentials'

    return render_template('login.html')

@app.route('/oidc-callback')
def oidc_callback():
    oidc.authorize_access_token()
    user_info = oidc.userinfo()
    session['user'] = user_info
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
