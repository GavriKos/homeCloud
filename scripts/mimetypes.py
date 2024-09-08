from flask import send_file

mimetypes_extensions_map = {
    "video": ["mp4"],
    "maptrack": ["gpx"],
    "image": ["jpg", "png", "jpeg"],
    "unknown": []
}
mimetype_unknown = "unknown"


def sendImage(filepath):
    return send_file(filepath, mimetype='image/jpeg')


def sendVideo(filepath):
    return send_file(filepath, as_attachment=False)


def sentFileBlob(filepath):
    return send_file(filepath)


mimetypes_returns = {
    'image': sendImage,
    'video': sendVideo,
    'maptrack': sentFileBlob
}


def getmimeType(extension):
    for key, values in mimetypes_extensions_map.items():
        if extension in values:
            return key
    return "unknown"


def getFileByMimetype(mimetype, filePath):
    return mimetypes_returns[mimetype](filePath)
