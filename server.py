import BaseHTTPServer
import os
import random


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write('web-dl. Coming soon.')

if 'PORT' in os.environ:
    PORT = int(os.environ['PORT'])
else:
    PORT = random.choice(range(5000, 10000))

httpd = BaseHTTPServer.HTTPServer(('', PORT), Handler)
print "serving at port", PORT
httpd.serve_forever()
