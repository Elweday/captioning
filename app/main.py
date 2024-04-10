import json
from moviepy.editor import VideoFileClip
import sys
from utils import get_audio_from_video, convert_array, split_text_into_lines, create_caption, create_video_from_subtitles


assert 3 <= len(sys.argv) <= 4, """
    Usage: python app/main.py <video_file> <time_stamps.json> [<options.json>]
"""

with open(sys.argv[2], encoding='utf8') as f:
    time_stamps = json.load(f)
    
options = {} 
try: 
    with open(sys.argv[3], encoding='utf8') as f:
        options = json.load(f)
except:
    pass

create_video_from_subtitles(sys.argv[1], convert_array(time_stamps), **options);