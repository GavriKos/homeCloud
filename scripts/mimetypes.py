"""
MIME type handling module for homeCloud application.
Contains functions for determining file types and serving files based on their MIME types.
"""

from flask import send_file

# Initialize HEIC support for Pillow
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # pillow-heif not available, HEIC support will be limited

# Mapping of MIME types to file extensions
mimetypes_extensions_map = {
    "video": ["mp4", "avi", "mov", "mkv", "webm"],
    "maptrack": ["gpx"],
    "image": ["jpg", "png", "jpeg", "webp", "gif", "bmp", "tiff", "svg", "heic", "heif"],
    "unknown": []
}
mimetype_unknown = "unknown"


def sendImage(filepath):
    """
    Send image file with appropriate MIME type.
    For HEIC/HEIF files, converts to JPEG since browsers don't support HEIC natively.

    Args:
        filepath (str): Path to the image file

    Returns:
        Response: Flask file response for image
    """
    import os
    import io
    from PIL import Image

    # Get file extension and determine proper MIME type
    _, ext = os.path.splitext(filepath.lower())
    ext = ext.lstrip('.')

    # Check if it's a HEIC/HEIF file that needs conversion
    if ext in ['heic', 'heif']:
        # Ensure pillow-heif is registered
        try:
            from pillow_heif import register_heif_opener
            register_heif_opener()
        except ImportError:
            # If pillow-heif is not available, send as-is
            return send_file(filepath, mimetype='image/jpeg')

        try:
            # Convert HEIC to JPEG in memory for browser compatibility
            with Image.open(filepath) as img:
                # Convert to RGB if necessary (HEIC might be in different color space)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Create in-memory buffer
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG', quality=85)
                img_buffer.seek(0)

                return send_file(img_buffer, mimetype='image/jpeg', as_attachment=False)
        except Exception:
            # If conversion fails, send as-is
            return send_file(filepath, mimetype='image/jpeg')

    # For other image formats, send as-is
    mime_map = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'webp': 'image/webp',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'tiff': 'image/tiff',
        'svg': 'image/svg+xml'
    }

    mimetype = mime_map.get(ext, 'image/jpeg')  # Default to jpeg if unknown
    return send_file(filepath, mimetype=mimetype)


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
    'maptrack': sentFileBlob,
    'unknown': sentFileBlob  # Handle unknown files as binary blobs
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
    # Use the appropriate handler or default to binary blob for unknown types
    handler = mimetypes_returns.get(mimetype, sentFileBlob)
    return handler(filePath)
