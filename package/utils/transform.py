import numpy as np
from moviepy.editor import TextClip, CompositeVideoClip, concatenate_videoclips,VideoFileClip, ColorClip, ImageClip
import json
import ffmpeg    

def round_corners(image, radius):
    height, width, channels = image.shape
    y, x = np.ogrid[0:height, 0:width]
    mask = np.ones((height, width))

    # Calculate distance from center for each pixel
    x_center, y_center = width / 2, height / 2
    distance_from_center = np.sqrt((x - x_center)**2 + (y - y_center)**2)

    # Apply mask to create rounded corners
    mask[distance_from_center <= radius] = 0

    # Multiply the image with the mask
    rounded_image = image * mask[:,:,np.newaxis]

    return rounded_image


def makeUpdater(scale, duration, initial_width, initial_height, initial_x, initial_y):
    initial_scale = 1
    final_width = initial_width
    final_height = initial_height
    
    def scaleUpdater(t):
        start_scale = initial_scale
        damping = 0.8  # Damping factor for the spring
        stiffness = 0.2  # Stiffness of the spring
        delta_scale = scale - start_scale
        spring_force = -stiffness * delta_scale
        damping_force = -damping * t * delta_scale / duration
        acceleration = (spring_force + damping_force) / duration
        scale_factor = start_scale + t/duration * (scale - start_scale) + acceleration * t
        
        # Return scale factor
        return scale_factor
    
    def positionUpdater(t):
        scale_factor = scaleUpdater(t)
        
        # Calculate the new width and height based on the scale factor
        new_width = initial_width * scale_factor
        new_height = initial_height * scale_factor
        
        # Calculate the offset to center the object
        x_offset = (final_width - new_width) / 2
        y_offset = (final_height - new_height) / 2
        
        # Calculate the new position
        new_x = initial_x + x_offset
        new_y = initial_y + y_offset
        
        # Return position
        return new_x, new_y
    
    return scaleUpdater, positionUpdater


def get_audio_from_video(videofilename):
    audiofilename = videofilename.replace(".mp4",'.mp3')
    input_stream = ffmpeg.input(videofilename)
    audio = input_stream.audio
    output_stream = ffmpeg.output(audio, audiofilename)
    output_stream = ffmpeg.overwrite_output(output_stream)
    ffmpeg.run(output_stream)
    return audiofilename

def convert_array(original_array):
    converted_array = []
    previous_end_time = None

    for item in original_array:
        current_start_time = previous_end_time if previous_end_time is not None else 0
        current_end_time = item['time']
        converted_array.append({
            'start': current_start_time,
            'end': current_end_time,
            'word': item['word']
        })
        previous_end_time = current_end_time

    return converted_array


def split_text_into_lines(data, **kwargs):
    max_chars = kwargs.get("max_chars", 40)
    max_duration = kwargs.get("max_duration", 2)
    max_gap = kwargs.get("max_gap", 2)
    
    subtitles = []
    line = []
    line_duration = 0
    line_chars = 0


    for idx,word_data in enumerate(data):
        word = word_data["word"]
        start = word_data["start"]
        end = word_data["end"]

        line.append(word_data)
        line_duration += end - start

        temp = " ".join(item["word"] for item in line)

        new_line_chars = len(temp)

        duration_exceeded = line_duration > max_duration
        chars_exceeded = new_line_chars > max_chars
        if idx>0:
          gap = word_data['start'] - data[idx-1]['end']
          maxgap_exceeded = gap > max_gap
        else:
          maxgap_exceeded = False


        if duration_exceeded or chars_exceeded or maxgap_exceeded:
            if line:
                subtitle_line = {
                    "word": " ".join(item["word"] for item in line),
                    "start": line[0]["start"],
                    "end": line[-1]["end"],
                    "textcontents": line
                }
                subtitles.append(subtitle_line)
                line = []
                line_duration = 0
                line_chars = 0


    if line:
        subtitle_line = {
            "word": " ".join(item["word"] for item in line),
            "start": line[0]["start"],
            "end": line[-1]["end"],
            "textcontents": line
        }
        subtitles.append(subtitle_line)
    
    print(subtitles)

    return subtitles

def create_caption(textJSON, framesize, **kwargs):
    font = kwargs.get('font', "Arial-Bold")
    fontsize = kwargs.get('fontsize', 60)
    color = kwargs.get('color', 'white')
    highlight_color = kwargs.get('highlight_color', 'yellow')
    bg_color = kwargs.get('bg_color', (150, 0, 100))
    bg_opacity = kwargs.get('bg_opacity', 1)
    bg_scaling = kwargs.get('bg_scaling', 1.8)
    bg_x_padding = kwargs.get('bg_x_padding', 25)
    bg_y_padding = kwargs.get('bg_y_padding', 15)
    stroke_color = kwargs.get('stroke_color', 'black')
    stroke_width = kwargs.get('stroke_width', 25)
    spacing = kwargs.get('spacing', 1.5)
    frame_padding = kwargs.get('frame_padding', 0.07)
    
    wordcount = len(textJSON['textcontents'])
    full_duration = textJSON['end']-textJSON['start']
    word_clips = []
    xy_textclips_positions = []

    x_pos = bg_x_padding//2
    y_pos = bg_y_padding//2
    line_width = 0  # Total width of words in the current line
    frame_width = framesize[0]
    frame_height = framesize[1]

    x_buffer = frame_width*frame_padding

    max_line_width = frame_width - 2 * (x_buffer)

    space_width = 0
    space_height = 0
    
    word_height = 0
    word_width = 0
    
    lines = []
    line = []

    for index,wordJSON in enumerate(textJSON['textcontents']):
        duration = wordJSON['end']-wordJSON['start']
        word_clip = TextClip(wordJSON['word'], font = font,fontsize=fontsize, color=color).set_start(textJSON['start']).set_duration(full_duration)
        word_clip_stroke = TextClip(wordJSON['word'], font = font,fontsize=fontsize, color=color,stroke_color=stroke_color,stroke_width=stroke_width).set_start(textJSON['start']).set_duration(full_duration)
        word_clip_space = TextClip(" ", font = font,fontsize=fontsize*spacing, color=color).set_start(textJSON['start']).set_duration(full_duration)
        word_width, word_height = word_clip.size
        space_width,space_height = word_clip_space.size
        if line_width + word_width+ space_width <= max_line_width:
            # Store info of each word_clip created
            xy_textclips_positions.append({
                "x_pos":x_pos,
                "y_pos": y_pos,
                "width" : word_width,
                "height" : word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })

            word_clip = word_clip.set_position((x_pos, y_pos))
            word_clip_stroke = word_clip_stroke.set_position((x_pos - stroke_width/2, y_pos - stroke_width/2))
            word_clip_space = word_clip_space.set_position((x_pos+ word_width, y_pos))

            x_pos = x_pos + word_width+ space_width
            line_width = line_width + word_width + space_width
        else:
            # Move to the next line
            lines.append(line)
            line = []
            x_pos = bg_x_padding//2
            y_pos = y_pos + word_height + bg_y_padding//2
            line_width = word_width + space_width

            # Store info of each word_clip created
            xy_textclips_positions.append({
                "x_pos":x_pos,
                "y_pos": y_pos,
                "width" : word_width,
                "height" : word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })

            word_clip = word_clip.set_position((x_pos, y_pos))
            word_clip_stroke = word_clip_stroke.set_position((x_pos - stroke_width/2, y_pos - stroke_width/2))

            word_clip_space = word_clip_space.set_position((x_pos+ word_width , y_pos))
            x_pos = word_width + space_width
        
        
        line += [word_clip_stroke, word_clip, word_clip_space]
        word_clips += [word_clip_stroke, word_clip, word_clip_space]

    for highlight_word in xy_textclips_positions:
      word_clip_highlight = TextClip(highlight_word['word'], font = font,fontsize=fontsize, color=highlight_color).set_start(highlight_word['start']).set_duration(highlight_word['duration'])
      word_clip_highlight = word_clip_highlight.set_position((highlight_word['x_pos'], highlight_word['y_pos']))

      w_init = highlight_word['width'] + bg_x_padding
      h_init = highlight_word['height'] + bg_y_padding
      x_init = highlight_word['x_pos'] - bg_x_padding // 2
      y_init = highlight_word['y_pos'] - bg_y_padding // 2
      dt = highlight_word['duration']
      size = (w_init, h_init)
      scaleFunc, posFunc = makeUpdater(bg_scaling, dt, w_init, h_init, x_init , y_init)
      color_clip = ColorClip(size=(size), color= bg_color) \
        .set_opacity(bg_opacity) \
        .set_position(posFunc) \
        .resize(scaleFunc) \
        .set_start(highlight_word['start']) \
        .set_duration(highlight_word['duration']) \
        
      word_clips.insert(0, color_clip)
      word_clips.append(word_clip_highlight)

    return word_clips, lines

def create_video_from_subtitles(videofilename, timestamps, **kwargs):
    linelevel_subtitles = split_text_into_lines(timestamps, **kwargs)
    input_video = VideoFileClip(videofilename)
    frame_size = input_video.size
    max_width, max_height = frame_size
    all_linelevel_splits=[]

    for line in linelevel_subtitles:
        out_clips, out_clips_lines = create_caption(line, frame_size, **kwargs)
        print(out_clips_lines)
        clip_to_overlay = CompositeVideoClip(out_clips, size=(max_width, int(max_height * 0.2))).set_start(line['start']).set_duration(line['end']-line['start'])
        all_linelevel_splits.append(clip_to_overlay)
    
    input_video_duration = input_video.duration
    final_video = CompositeVideoClip([input_video] + all_linelevel_splits)
    final_video = final_video.set_audio(input_video.audio)
    final_video = final_video.subclip(0, 6) # TODO: remove
    output_filename = videofilename.replace(".mp4","_output.mp4")
    
    final_video.write_videofile(output_filename, fps=input_video.fps, codec="libx264", audio_codec="aac")