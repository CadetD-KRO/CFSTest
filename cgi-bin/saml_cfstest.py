#!/usr/bin/python3
from flask import Flask, redirect, request, session, url_for
from onelogin.saml2.auth import OneLogin_Saml2_Auth
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cfs001SecretKey")

# SAML configuration
# SAML configuration
saml_settings = {
    'strict': True,
    'debug': False,
    'sp': {
        'entityId': 'http://cfstest001/saml_app',
        'assertionConsumerService': {
            'url': 'http://localhost:5000/acs',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
        },
        'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
        'x509cert': open('path/to/your/sp/certificate.pem').read(),
        'privateKey': open('path/to/your/sp/private-key.pem').read(),
    },
    'idp': {
        'entityId': 'http://cfstest001.dudleycadet.us/saml_IDP',
        'singleSignOnService': {
            'url': 'IDP-Single-Sign-On-URL',
            'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
        },
        'x509cert': open('path/to/your/idp/public-certificate.pem').read(),
    },
}

#saml_auth = OneLogin_Saml2_Auth(None, saml_settings)


#Use below to point to metadata.xml or above to fill-out inline. 
saml_auth = OneLogin_Saml2_Auth(request, custom_base_path=os.path.join(os.path.dirname("cfs001_saml.xml"), 'saml'))


# Simulated user database
users = {
    'testuser001@dudleycadet.us': {'name': 'TestUser001'},
    'testuser002@dudleycadet.us': {'name': 'TestUser002'}
}

@app.route('/')
def index():
    if 'user' in session:
        return f'Hello, {session["user"]["name"]}! <a href="/logout">Logout</a>'
    return 'Hello, guest! <a href="/login">Login with SAML</a>'

@app.route('/login')
def login():
    saml_auth.login()
    return redirect(saml_auth.redirect_to)

@app.route('/sso/acs', methods=['POST'])
def acs():
    saml_auth.process_response()
    errors = saml_auth.get_errors()
    if not errors:
        email = saml_auth.get_attributes()['email'][0]
        if email in users:
            session['user'] = users[email]
            return redirect(url_for('index'))
    return 'SAML authentication failed'

@app.route('/logout')
def logout():
    session.pop('user', None)
    saml_auth.logout()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
