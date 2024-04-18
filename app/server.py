from flask import Flask, request, send_file
import json
from utils import convert_array, create_video_from_subtitles
from os import environ

app = Flask(__name__)

default_options = {
    "font": "Arial-Bold",
    "fontsize": 50,
    "color": "white",
    "location": 0.5,
    "highlight_color": "white",
    "bg_color": [142, 171, 211],
    "bg_opacity": 1,
    "bg_border_radius": 20,
    "bg_scaling_factor": 1.1,
    "bg_scaling_damping": 0.3,
    "bg_scaling_stiffness": 0.4,
    "bg_scaling_duration": 0.3,
    "bg_x_padding": 35,
    "bg_y_padding": 25,
    "stroke_color": "black",
    "stroke_width": 5,
    "spacing": 1.2,
    "frame_padding": 0.1,
    "max_chars": 20,
    "max_duration": 2,
    "max_gap": 2
}


@app.route('/', methods=['GET'])
def index():
    return """
    <h1>Video Subtitle Generator send a POST request with a video and timestamps</h1>
    """


@app.route('/', methods=['POST'])
def process_video():
    # Check if the request contains a file
    if 'video' not in request.files:
        return 'No file uploaded', 400

    if 'timestamps' not in request.files:
        return 'No data uploaded', 400

    uploaded_file = request.files['video']
    if uploaded_file.filename == '':
        return 'No file selected', 400

    filename = uploaded_file.filename

    time_stamps = json.loads(request.files['timestamps'].read())

    try:
        options = json.loads(request.files['options'].read())
    except:
        options = default_options

    uploaded_file.save(filename)
    output_filename = create_video_from_subtitles(
        filename, convert_array(time_stamps), **options)

    return send_file(output_filename, mimetype='video/mp4')


if __name__ == '__main__':
    app.run(host='0.0.0.0',  port=environ.get('PORT', 8080))
