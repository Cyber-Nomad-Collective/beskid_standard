// h2 + http/1.1 TLS server for the Beskid Web client interop (curl-interop.sh).
// Answers "node <httpVersion> <url>" or, for POST, "node received <length>".
const http2 = require('http2');
const fs = require('fs');
const certs = process.argv[2];
const port = Number(process.argv[3] || 18444);
const server = http2.createSecureServer({
  key: fs.readFileSync(certs + '/server.key'),
  cert: fs.readFileSync(certs + '/server.pem'),
  allowHTTP1: true,
  minVersion: 'TLSv1.3',
}, (req, res) => {
  let n = 0;
  req.on('data', (c) => { n += c.length; });
  req.on('end', () => {
    const body = req.method === 'POST' ? 'node received ' + n : 'node ' + req.httpVersion + ' ' + req.url;
    res.writeHead(200, { 'content-type': 'text/plain', 'content-length': Buffer.byteLength(body) });
    res.end(body);
  });
});
server.listen(port, '127.0.0.1', () => console.log('ready'));
