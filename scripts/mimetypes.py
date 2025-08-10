"""
MIME type handling module for homeCloud application.
Contains functions for determining file types and serving files based on their MIME types.
"""

from flask import send_file

# Mapping of MIME types to file extensions
mimetypes_extensions_map = {
    "video": ["mp4"],
    "maptrack": ["gpx"],
    "image": ["jpg", "png", "jpeg"],
    "unknown": []
}
mimetype_unknown = "unknown"


def sendImage(filepath):
    """
    Send image file with appropriate MIME type.

    Args:
        filepath (str): Path to the image file

    Returns:
        Response: Flask file response for image
    """
    return send_file(filepath, mimetype='image/jpeg')


def sendVideo(filepath):
    """
    Send video file for streaming.

    Args:
        filepath (str): Path to the video file

    Returns:
        Response: Flask file response for video
    """
    return send_file(filepath, as_attachment=False)


def sentFileBlob(filepath):
    """
    Send file as binary blob.

    Args:
        filepath (str): Path to the file

    Returns:
        Response: Flask file response
    """
    return send_file(filepath)


# Mapping of MIME types to their corresponding send functions
mimetypes_returns = {
    'image': sendImage,
    'video': sendVideo,
    'maptrack': sentFileBlob
}


def getmimeType(extension):
    """
    Determine MIME type based on file extension.

    Args:
        extension (str): File extension (without dot)

    Returns:
        str: MIME type string or "unknown" if not recognized
    """
    for key, values in mimetypes_extensions_map.items():
        if extension in values:
            return key
    return "unknown"


def getFileByMimetype(mimetype, filePath):
    """
    Serve file using appropriate handler based on MIME type.

    Args:
        mimetype (str): MIME type of the file
        filePath (str): Path to the file

    Returns:
        Response: Flask file response using appropriate handler
    """
    return mimetypes_returns[mimetype](filePath)
