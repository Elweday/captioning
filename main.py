import json
from package import get_audio_from_video, convert_array, split_text_into_lines, create_caption, create_video_from_subtitles, transcribe
from moviepy.editor import VideoFileClip

with open("time_stamps.json", encoding='utf8') as f:
    time_stamps = json.load(f)

create_video_from_subtitles("sample.mp4", convert_array(time_stamps), **{
    "font": "Arial-Bold",
    "fontsize": 40,
    "color": "white",
    "highlight_color": "white",
    "bg_color": (142, 171, 211),
    "bg_opacity": 1,
    "bg_border_radius": 15,
    "bg_scaling_factor": 1.2,
    "bg_scaling_damping": 1.0,
    "bg_scaling_stiffness": 0.1,
    "bg_x_padding": 25,
    "bg_y_padding": 15,
    "stroke_color": "black",
    "stroke_width": 5,
    "spacing": 1.0,
    "frame_padding": 0.1,
    "max_chars": 20,
    "max_duration": 2,
    "max_gap": 2,
});