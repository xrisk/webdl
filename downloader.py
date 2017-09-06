import os
import hashlib


def sha_hash(content):
    if type(content) == str:
        content = content.encode('utf-8')
    m = hashlib.sha256()
    m.update(content)
    return m.hexdigest()

def download_audio(url):
    from subprocess import call

    retcode = call(["youtube-dl", "-x", "--id",
                    "--audio-quality", "9",
                    "--audio-format", "mp3",
                    "--exec",
                    "mv {} " + os.path.join('mp3cache/', sha_hash(url)),
                    url])

    if retcode == 0:
        return sha_hash(url)
    else:
        raise Exception


def download_video(url):
    from subprocess import call
    retcode = call(["youtube-dl", "--format", "mp4",
                    "--exec",
                    "mv {} " + os.path.join('mp4cache/', sha_hash(url)),
                    url])

    if retcode == 0:
        return sha_hash(url)
    else:
        raise Exception
