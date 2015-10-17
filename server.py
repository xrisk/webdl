import BaseHTTPServer
import gzip
import logging
import os
import random
import sha
import sys
import urlparse


def sha_hash(content):
    return sha.new(content).hexdigest()


def mime(path):
    for i in mimetable:
        if path.endswith(i):
            return mimetable[i]
    logging.warn('Mime type not found for' + path)
    return 'text/plain'


def gzip_content(content):
    h = sha_hash(content) + '.gzip'
    if os.path.isfile(h):
        with open(h, 'rb') as fin:
            return fin.read()
    with gzip.open(h, 'wb') as fout:
        fout.write(content)
    fout.close()
    with open(h, 'rb') as fin:
        return fin.read()


def has_gzip(self):
    if 'Accept-Encoding' in self.headers:
        if 'gzip' in self.headers['Accept-Encoding']:
            return True
    else:
        return False


def smart_reply(self, resp):
    if self.has_gzip():
        self.send_header('Content-Encoding', 'gzip')
        self.end_headers()
        self.wfile.write(gzip_content(resp))
    else:
        self.end_headers()
        self.wfile.write(resp)

# let's be a nice compliant server
mimetable = {
    ".css": "text/css",
    ".eot": "application/octet-stream",
    ".html": "text/html",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".ttf": "application/x-font-ttf",
    ".woff": "application/octet-stream",
    ".woff2": "application/octet-stream",
}

hash_lookup = {}

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        if '--force-ssl' in sys.argv:
            if self.headers['X-Forwarded-Proto'] != 'https':
                self.send_response(301, 'Must use SSL')
                self.send_header(
                        'Location', 'https://icse.herokuapp.com' + self.path)
                self.end_headers()
                return

        if self.path == '/':
            path = os.path.join('web', 'index.html')
        else:
            if self.path.startswith('/'):
                path = os.path.join('web', self.path[1:])
            else:
                path = os.path.join('web', self.path)

        if not os.path.isfile(path):
            self.send_response(404)
            self.send_header('Content-Type', 'text/html')
            with open('web/404-generic.html') as fin:
                resp = fin.read()
            self.write(resp)
            return

        with open(path) as fin:
            resp = fin.read()

        if path in hash_lookup:
            h = hash_lookup[path]
        else:
            h = sha_hash(resp)
            hash_lookup[path] = h

        if 'If-None-Match' in self.headers:
            if h == self.headers['If-None-Match']:
                self.send_response(304, "Unchanged")
                self.send_header("Cache-Control", "no-cache, max-age=604800")
                self.send_header("ETag", h)
                self.end_headers()
                return

        self.send_response(200, 'OK')
        self.send_header("Cache-Control", "no-cache, max-age=604800")
        self.send_header("Content-type", mime(path))
        self.send_header("ETag", h)
        self.write(resp)

Handler.has_gzip = has_gzip
Handler.write = smart_reply

if 'PORT' in os.environ:
    PORT = int(os.environ['PORT'])
else:
    PORT = random.choice(range(5000, 10000))

httpd = BaseHTTPServer.HTTPServer(('', PORT), Handler)
print "serving at port", PORT
httpd.serve_forever()