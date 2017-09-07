import threading
import youtube_dl


class YoutubeDownloader:

    db = {}
    req_ids = {}
    cur_req = 0

    audio_opts = {
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }],
        'outtmpl': '{}/%(title)s-%(id)s.%(ext)s',
    }

    video_opts = {
        'format': 'mp4',
        'outtmpl': '{}/%(title)s-%(id)s.%(ext)s',
    }

    def __init__(self, savedir):
        self.savedir = savedir
        self.audio_opts["outtmpl"] = self.audio_opts["outtmpl"].format(savedir)
        self.video_opts["outtmpl"] = self.video_opts["outtmpl"].format(savedir)

    def _make_progress_hook(self, url, audio_only=False):
        def func(cb):
            d = self.db[(url, audio_only)]
            if cb["status"] == "finished":
                d["status"] = "finished"
                d["filename"] = cb["filename"]
                if "eta" in d: 
                    del d["eta"]
            elif cb["status"] == "downloading":
                d["status"] = "downloading"
                if cb["eta"]:
                    d["eta"] = cb["eta"]
            elif cb["status"] == "error":
                d["status"] = "error"
        return func

    def _get_new_req_id(self):
        self.cur_req += 1
        return self.cur_req

    def start_download(self, url, audio_only=True):
        if (url, audio_only) in self.db:
            return
        self.db[(url, audio_only)] = {"status": "added"}
        req_id = self._get_new_req_id()
        self.req_ids[req_id] = (url, audio_only)

        def new_ydl_object():
            opts = self.audio_opts if audio_only else self.video_opts
            with youtube_dl.YoutubeDL(opts) as ydl:
                hook = self._make_progress_hook(url, audio_only)
                ydl.add_progress_hook(hook)
                try:
                    ydl.download([url])
                except youtube_dl.utils.YoutubeDLError as e:
                    print(e)
                    self.db[(url, audio_only)]["status"] = "error"
        threading.Thread(target=new_ydl_object).start()
        return req_id

    def get_status(self, req_id):
        if req_id not in self.req_ids:
            return {"message": "No such request id"}
        return self.db[self.req_ids[req_id]]
