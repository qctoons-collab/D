from flask import Flask, request, jsonify, render_template, send_file
import yt_dlp
import os
import uuid
import threading
import time

app = Flask(__name__, template_folder='.')

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# ফাইল ডিলিট করার ফাংশন (ব্যাকগ্রাউন্ডে চলবে)
def delete_file_after_delay(filepath, delay=300): # ৫ মিনিট পর ডিলিট হবে
    def delay_delete():
        time.sleep(delay)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted: {filepath}")
    
    threading.Thread(target=delay_delete).start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get-url', methods=['POST'])
def get_url():
    data = request.json
    video_url = data.get('url')
    res = data.get('resolution')

    if not video_url:
        return jsonify({'success': False, 'error': 'Link dewa hoyni'})

    file_id = str(uuid.uuid4())
    # এক্সটেনশন ডাইনামিক রাখার জন্য %(ext)s ব্যবহার
    output_template = f'{DOWNLOAD_FOLDER}/{file_id}.%(ext)s'

    ydl_opts = {
        'format': f'bestvideo[height<={res}]+bestaudio/best[height<={res}]/best',
        'outtmpl': output_template,
        'merge_output_format': 'mp4',
        'cookiefile': 'cookies.txt',
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            # মার্জ হওয়ার পর মেইন ফাইলটি হবে .mp4
            actual_filename = f"{file_id}.mp4"
            filepath = os.path.join(DOWNLOAD_FOLDER, actual_filename)
            
            download_link = f"{request.host_url}download/{actual_filename}"
            
            # ফাইলটি তৈরি হওয়ার পর ৫ মিনিট সময় দেওয়া হলো ডাউনলোড করার জন্য, তারপর অটো ডিলিট
            delete_file_after_delay(filepath, delay=600) # ১০ মিনিট সময় দেওয়া হলো

            return jsonify({
                'success': True, 
                'download_url': download_link,
                'title': info.get('title')
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def serve_file(filename):
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        # as_attachment=True দিলে ব্রাউজারে ফাইলটি সরাসরি ডাউনলোড হবে
        return send_file(filepath, as_attachment=True)
    else:
        return "Fileটি সার্ভার থেকে ডিলিট হয়ে গেছে বা পাওয়া যাচ্ছে না। আবার চেষ্টা করুন।", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
