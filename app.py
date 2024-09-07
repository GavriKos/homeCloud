from flask import Flask, request, send_file, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/share/<md5>')
def share(md5):
    image_path = '1.jpg'
    
    return send_file(image_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
