
def download(url, path):
    from subprocess import call
    call(["youtube-dl", "-x", "--id",
          "--audio-quality", "9",
          "--audio-format", "mp3",
          "--exec", "mv {} " + path,
          url])
