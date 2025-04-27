from flask import Flask, request, jsonify, send_from_directory
from yt_dlp import YoutubeDL
import os
import tempfile

app = Flask(__name__)
DOWNLOAD_FOLDER = tempfile.mkdtemp()
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({'error': 'URL non fournie'}), 400
    
    try:
        options = {
            'format': 'best',
            'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'extractor_args': {'youtube': {'player_client': ['android']}},
        }
        
        with YoutubeDL(options) as ydl:
            ydl.download([video_url])

        file_list = os.listdir(app.config['DOWNLOAD_FOLDER'])
        if not file_list:
            return jsonify({'error': 'Échec du téléchargement'}), 500
        
        file_name = file_list[-1]  # Dernier fichier téléchargé

        file_url = request.host_url + "videos/" + file_name

        return jsonify({
            'success': True,
            'file_url': file_url
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/videos/<path:filename>', methods=['GET'])
def serve_video(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/', methods=['GET'])
def home():
    return "API YT Downloader OK", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
