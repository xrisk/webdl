import sha
import os


def sha_hash(content):
    return sha.new(content).hexdigest()


def download(url):
    from subprocess import call
    
    retcode = call(["youtube-dl", "-x", "--id",
          "--audio-quality", "9",
          "--audio-format", "mp3",
          "--exec", "mv {} " + os.path.join('/app/', sha_hash(url)),
          url])

    if retcode == 0:
        return sha_hash(url)
    else:
        raise Exception
