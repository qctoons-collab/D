from flask import Flask, request, jsonify, render_template
import yt_dlp
import os

# Template folder '.' দেওয়ায় index.html একই ফোল্ডারে রাখা যাবে
app = Flask(__name__, template_folder='.')

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

    # 'b' ব্যবহার করা হয়েছে কারণ এটি video+audio একসাথে (pre-merged) ফাইল খুঁজে পায়।
    # 'b[height<=?]/b' এর মানে হলো নির্দিষ্ট রেজল্যুশন খুঁজবে, না পেলে যেটা এভেইলঅ্যাবল সেটা দেবে।
    if res == 'best':
        format_str = 'b/best'
    else:
        format_str = f'b[height<={res}]/b/best'

    ydl_opts = {
        'format': format_str,
        'noplaylist': True,
        'quiet': True,
        'cookiefile': 'cookies.txt', # আপনার দেওয়া কুকি ফাইলটি অবশ্যই একই ফোল্ডারে থাকতে হবে
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            # অনেক সময় 'url' সরাসরি না পাওয়া গেলে 'formats' থেকে নেওয়া হয়
            download_url = info.get('url') or info.get('formats')[-1].get('url')
            
            return jsonify({
                'success': True, 
                'download_url': download_url,
                'title': info.get('title', 'Video')
            })
    except Exception as e:
        # এরর মেসেজটি একটু পরিষ্কারভাবে দেখানোর জন্য
        error_msg = str(e)
        if "format is not available" in error_msg:
            error_msg = "Ei resolution e video+audio eksathe pawa jacche na. Onno res try korun."
        return jsonify({'success': False, 'error': error_msg})

if __name__ == '__main__':
    # Render-এর জন্য ডাইনামিক পোর্ট সেটআপ
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
