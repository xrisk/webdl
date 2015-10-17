import sha
import os


def sha_hash(content):
    return sha.new(content).hexdigest()


def download(url):
    from subprocess import call
    try:
        call(["youtube-dl", "-x", "--id",
              "--audio-quality", "9",
              "--audio-format", "mp3",
              "--exec", "mv {} " + os.path.join('/app/', sha_hash(url)),
              url])

        with open('/app/' + sha_hash(url), 'rb') as fin:
            resp = fin.read()
    except:
        raise Exception('Malformed URL.')
    return resp
