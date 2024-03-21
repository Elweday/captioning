import json
from package import get_audio_from_video, convert_array, split_text_into_lines, create_caption, create_video_from_subtitles, transcribe
from moviepy.editor import VideoFileClip

with open("time_stamps.json", encoding='utf8') as f:
    time_stamps = json.load(f)

create_video_from_subtitles("sample.mp4", convert_array(time_stamps), **{
    "font": "Arial-Bold",
    "fontsize": 50,
    "color": "white",
    "highlight_color": "yellow",
    "bg_color": (0 ,0, 255),
    "bg_opacity": 1,
    "bg_scaling": 1.25,
    "bg_x_padding": 25,
    "bg_y_padding": 15,
    "stroke_color": "black",
    "stroke_width": 5,
    "spacing": 1.7,
    "frame_padding": 0.03,
    "max_chars": 50,
    "max_duration": 2,
    "max_gap": 2,
});