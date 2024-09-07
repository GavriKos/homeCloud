from flask import Flask, request, send_file, render_template
import os, json

app = Flask(__name__)

@app.route('/share/<md5>')
def getShare(md5):
    return render_template('index.html')

@app.route('/share/all/<md5_share>')
def getAllfromShare(md5_share):
    data = {}
    data["mediaList"] = []
    data["mediaList"].append(4)
    data["mediaList"].append(5)
    data["mediaList"].append(6)
    return json.dumps(data)

@app.route('/share/<md5_share>/<md5_file>')
def share(md5_share,md5_file):
    num = int(md5_file)-3
    image_path = str(num)+'.jpg'
    
    return send_file(image_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
