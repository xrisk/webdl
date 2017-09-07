from flask import Flask

from flask import request, jsonify, abort
from downloader import YoutubeDownloader

app = Flask(__name__)
yt = YoutubeDownloader('cache')


@app.route('/download/<req_type>', methods=['POST'])
def handle_download_request(req_type):
    if 'url' not in request.form:
        abort(400)
    if req_type != "mp3" and req_type != "mp4":
        abort(400)
    try:
        a = True if req_type == "mp3" else False
        req_id = yt.start_download(request.form['url'], audio_only=a)
        return jsonify({'req_id': req_id})
    except Exception as e:
        print(e)
        return jsonify({'status': 'error'})


@app.route('/status/<int:req_id>', methods=['GET'])
def handle_status_request(req_id):
    status = yt.get_status(req_id)
    return jsonify(status)


if __name__ == '__main__':
    app.run(debug=True)
