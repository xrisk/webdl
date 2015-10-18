# webdl 

> A _light, libre and oh-so-fast_ downloader for YouTube.
> In all of 2,596 bytes. 

![Screenshot of webdl](https://i.imgur.com/K7K4rz0.png)

===========

##### How it works

The webdl downloader uses ffmpeg and youtube to do all the hard work. The server is written in asynchronous Tornado, and uses state-of-the-art techniques like compression and caching. This _is_ speed pushed to its limits.

##### Dependencies

* yasm (not strictly required but offers significant speed boost)
* ffmpeg, compiled with the libmp3lame codec (required to convert to mp3 format)
* Tornado

##### Run it yourself

```

# OS X using Homebrew
brew install yasm lame ffmpeg --with-lame

# APT
sudo apt-get yasm libmp3lame0 ffmpeg

git clone https://github.com/xrisk/webdl.git
cd webdl

mkdir mp3cache
mkdir mp4cache

pip install -r requirements.txt

export PORT=5000
python -u server.py
```

Then navigate to http://localhost:5000 to see it in action.

##### License

Distributed under the MIT license.
