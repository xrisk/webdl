import tornado.ioloop
import tornado.web
import gzip
import logging
import downloader
import os
import sys
import hashlib

hash_lookup = {}

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


def sha_hash(content):
    if type(content) == str:
        content = content.encode('utf-8')
    m = hashlib.sha256()
    m.update(content)
    return m.hexdigest()


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
        if type(content) == str:
            content = content.encode('utf-8')
        fout.write(content)
    fout.close()
    with open(h, 'rb') as fin:
        return fin.read()


def has_gzip(self):
    if 'Accept-Encoding' in self.request.headers:
        if 'gzip' in self.request.headers['Accept-Encoding']:
            return True
    else:
        return False


def smart_reply(self, resp):
    if self.has_gzip():
        if '--no-compress' not in sys.argv:
            self.set_header('Content-Encoding', 'gzip')
            self.write(gzip_content(resp))
            return
    self.write(resp)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if self.request.path == '/':
            path = os.path.join('web', 'index.html')
        else:
            if self.request.path.startswith('/'):
                path = os.path.join('web', self.request.path[1:])
            else:
                path = os.path.join('web', self.request.path)

        if not os.path.isfile(path):
            self.set_status(404, 'Not Found')
            self.set_header('Content-Type', 'text/html')
            with open('web/404-generic.html') as fin:
                resp = fin.read()
            self.smart_write(resp)
            self.finish()
            return

        with open(path, 'rb') as fin:
            resp = fin.read()

        if path in hash_lookup:
            h = hash_lookup[path]
        else:
            h = sha_hash(resp)
            hash_lookup[path] = h

        if 'If-None-Match' in self.request.headers:
            if h == self.request.headers['If-None-Match']:
                self.set_status(304, "Unchanged")
                self.set_header("Cache-Control", "no-cache, max-age=604800")
                self.set_header("ETag", h)
                self.finish()
                return

        self.set_status(200, 'OK')
        self.set_header("Cache-Control", "no-cache, max-age=604800")
        self.set_header("Content-type", mime(path))
        self.set_header("ETag", h)
        self.smart_write(resp)
        self.finish()


class AudioHandler(tornado.web.RequestHandler):
    def get(self):
        link = self.get_argument('link')
        path = os.path.join('mp3cache/', sha_hash(link))
        if not os.path.exists(path):
            try:
                downloader.download_audio(link)
            except Exception:
                self.set_status(404, 'Not Found')
                self.set_header('Content-Type', 'text/html')
                with open('web/404-video.html') as fin:
                    self.smart_write(fin.read())
                self.finish()
                return

        self.set_status(200, 'OK')
        self.set_header('Content-Type', 'application/octet-stream')
        with open(path, 'rb') as fin:
            self.smart_write(fin.read())
        self.finish()


class VideoHandler(tornado.web.RequestHandler):
    def get(self):
        link = self.get_argument('link')
        path = os.path.join('mp4cache/', sha_hash(link))
        if not os.path.exists(path):
            try:
                downloader.download_video(link)
            except Exception:
                self.set_status(404, 'Not Found')
                self.set_header('Content-Type', 'text/html')
                with open('web/404-video.html') as fin:
                    self.smart_write(fin.read())
                self.finish()
                return

        self.set_status(200, 'OK')
        self.set_header('Content-Type', 'application/octet-stream')
        with open(path, 'rb') as fin:
            self.smart_write(fin.read())
        self.finish()


def make_app():
    return tornado.web.Application([
        (r"^/download\.mp3.*$", AudioHandler),
        (r"^/download\.mp4.*$", VideoHandler),
        (r"/.*", MainHandler),
    ])


MainHandler.smart_write = smart_reply
MainHandler.has_gzip = has_gzip
AudioHandler.smart_write = smart_reply
AudioHandler.has_gzip = has_gzip
VideoHandler.smart_write = smart_reply
VideoHandler.has_gzip = has_gzip

app = make_app()
app.listen(os.environ['PORT'])
tornado.ioloop.IOLoop.current().start()
