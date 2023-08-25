const express = require('express');
const { parseString } = require('xml2js');
const fs = require('fs');
const app = express();

app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

app.set('view engine', 'ejs');

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});

function readIdpMetadata() {
  const metadataXml = fs.readFileSync('ws-fed_cfstest.xml', 'utf-8');
  return metadataXml;
}

const idpMetadataXml = readIdpMetadata();

const idpMetadata = {
  entity_id: 'https://cfs001.dudleycadet.us',
  sso_service: {
    binding: 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
    url: 'https://cfs001.dudleycadet.us/cfs/WsFed/testusers/9bc41285-8afc-40a0-ad12-22e0d0d09197'
  }
};

app.get('/', (req, res) => {
  if (req.session.user) {
    res.send(`Hello, ${req.session.user.name}! <a href="/logout">Logout</a>`);
  } else {
    res.send('Hello, guest! <a href="/login">Login with WS-Federation</a>');
  }
});

app.get('/login', (req, res) => {
  res.render('login');
});

app.post('/login', (req, res) => {
  const email = req.body.email;
  const password = req.body.password;

  // Validate the user's credentials
  if (users[email] && users[email].password === password) {
    // Create and send WS-Federation request
    res.redirect(`/wsfed?email=${email}`);
  } else {
    res.send('Invalid credentials');
  }
});

app.get('/wsfed', (req, res) => {
  const email = req.query.email;
  const idpLoginUrl = idpMetadata.sso_service.url;

  const encodedRedirectUrl = encodeURIComponent('http://localhost:3000/wsfed-callback');

  // Construct the WS-Federation login URL
  const wsfedLoginUrl = `${idpLoginUrl}?whr=${idpMetadata.entity_id}&wreply=${encodedRedirectUrl}&username=${email}`;

  res.redirect(wsfedLoginUrl);
});

app.get('/wsfed-callback', (req, res) => {
  // Handle WS-Federation response
  // ...
});

app.get('/logout', (req, res) => {
  req.session.user = null;
  res.redirect('/');
});

const users = {
  'testuser001@dudleycadet.us': { name: 'TestUser001', password: 'My2Kids000' },
  'testuser002@dudleycadet.us': { name: 'TestUser002', password: 'My2Kids000' }
};
