const http = require('http');

const data = JSON.stringify({
  email: "test@domain.com",
  password: "mypassword",
  full_name: "Test User"
});

const options = {
  hostname: 'localhost',
  port: 8000,
  path: '/api/v1/auth/register',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': data.length
  }
};

const req = http.request(options, res => {
  console.log(`Status Code: ${res.statusCode}`);
  let body = '';
  res.on('data', chunk => body += chunk);
  res.on('end', () => console.log(`Body: ${body}`));
});

req.on('error', error => {
  console.error(`Request Error: ${error.message}`);
});

req.write(data);
req.end();
