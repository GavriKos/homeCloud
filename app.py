from flask import Flask, request, send_file, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_all_images')
def get_all_images():
    
    return "{\"md5_list\":[\"1\",\"2\",\"3\"]}"

@app.route('/share/<md5>')
def share(md5):
    num = int(md5)-3
    image_path = str(num)+'.jpg'
    
    return send_file(image_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
