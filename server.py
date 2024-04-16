from flask import Flask, request, send_file, logging, jsonify
import os
import json
from moviepy.editor import VideoFileClip
import sys
from app.utils import convert_array, create_video_from_subtitles


app = Flask(__name__)


@app.route('/process_video', methods=['POST'])
def process_video():
    # Check if the request contains a file
    if 'file' not in request.files:
        return 'No file uploaded', 400

    if 'timestamps' not in request.files:
        return 'No data uploaded', 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return 'No file selected', 400

    filename = uploaded_file.filename

    time_stamps = json.loads(request.files['timestamps'].read())

    try:
        options = json.loads(request.files['options'].read())
    except:
        options = {}

    # Save the uploaded file
    uploaded_file.save(filename)
    output_filename = create_video_from_subtitles(
        filename, convert_array(time_stamps), **options)

    # Return the processed video file
    return send_file(output_filename, mimetype='video/mp4')


if __name__ == '__main__':
    app.run(debug=True)


# read json
with open('time_stamps.json') as json_file:
    data = json.load(json_file)
