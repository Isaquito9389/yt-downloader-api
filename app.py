from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os
import tempfile

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({'error': 'URL non fournie'}), 400
    
    try:
        temp_dir = tempfile.mkdtemp()
        
        options = {
            'format': 'best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
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

        file_list = os.listdir(temp_dir)
        if not file_list:
            return jsonify({'error': 'Échec du téléchargement'}), 500
        
        file_name = file_list[0]
        return jsonify({
            'message': 'Téléchargement réussi',
            'filename': file_name
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "API YT Downloader OK", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
