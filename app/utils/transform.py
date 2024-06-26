import numpy as np
from moviepy.editor import TextClip, CompositeVideoClip, concatenate_videoclips, VideoFileClip, ColorClip, ImageClip
import json
import ffmpeg
import random
import cv2


def rounded_mask(width, height, radius, color=(255, 255, 255, 255), margin=(0, 0)):
    mx, my = margin
    img = np.zeros((height + 2*my, width + 2*mx, 4),
                   dtype=np.uint8)  # Expand image size
    cv2.rectangle(img, (mx, my + radius),
                  (width + mx, height + my - radius), color, -1)
    cv2.rectangle(img, (mx + radius, my),
                  (width + mx - radius, height + my), color, -1)
    cv2.circle(img, (mx + radius, my + radius), radius, color, -1)
    cv2.circle(img, (width + mx - radius, my + radius), radius, color, -1)
    cv2.circle(img, (mx + radius, height + my - radius), radius, color, -1)
    cv2.circle(img, (width + mx - radius, height +
               my - radius), radius, color, -1)
    return img


def random_color():
    return (int(random.random() * 255), int(random.random() * 255), int(random.random() * 255), 30)


def makeUpdater(scale, duration, initial_width, initial_height, initial_x, initial_y, damping, stiffness, mx, my):
    initial_scale = 1
    final_width = (initial_width * initial_scale)
    final_height = (initial_height * initial_scale)

    def scaleUpdater(t):
        start_scale = initial_scale
        delta_scale = scale - start_scale
        spring_force = -stiffness * delta_scale
        damping_force = -damping * t * delta_scale / duration
        acceleration = (spring_force + damping_force) / duration
        scale_factor = start_scale + t/duration * \
            (scale - start_scale) + acceleration * t
        return scale_factor if scale_factor >= initial_scale else initial_scale

    def positionUpdater(t):
        scale_factor = scaleUpdater(t)
        x_offset = (initial_width) * (1 - scale_factor) / 2
        y_offset = (initial_height) * (1 - scale_factor) / 2
        new_x = initial_x + x_offset - mx
        new_y = initial_y + y_offset - my
        return new_x, new_y
    return scaleUpdater, positionUpdater


def get_audio_from_video(videofilename):
    audiofilename = videofilename.replace(".mp4", '.mp3')
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

    for idx, word_data in enumerate(data):
        word = word_data["word"]
        start = word_data["start"]
        end = word_data["end"]

        line.append(word_data)
        line_duration += end - start

        temp = " ".join(item["word"] for item in line)

        new_line_chars = len(temp)

        duration_exceeded = line_duration > max_duration
        chars_exceeded = new_line_chars > max_chars
        if idx > 0:
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
    return subtitles


def create_caption(textJSON, framesize, **kwargs):
    font = kwargs.get('font', "Arial-Bold")
    fontsize = kwargs.get('fontsize', 60)
    color = kwargs.get('color', 'white')
    highlight_color = kwargs.get('highlight_color', 'yellow')
    bg_color = kwargs.get('bg_color', (150, 0, 100))
    bg_opacity = kwargs.get('bg_opacity', 1)
    bg_scaling = kwargs.get('bg_scaling_factor', 1.2)
    damping = kwargs.get('bg_scaling_damping', 0.8)
    stiffness = kwargs.get('bg_scaling_stiffness', 0.2)
    bg_x_padding = kwargs.get('bg_x_padding', 25)
    bg_y_padding = kwargs.get('bg_y_padding', 15)
    bg_border_radius = kwargs.get('bg_border_radius', 15)
    stroke_color = kwargs.get('stroke_color', 'black')
    stroke_width = kwargs.get('stroke_width', 25)
    spacing = kwargs.get('spacing', 1.5)
    frame_padding = kwargs.get('frame_padding', 0.07)

    wordcount = len(textJSON['textcontents'])
    full_duration = textJSON['end']-textJSON['start']
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

    for index, wordJSON in enumerate(textJSON['textcontents']):
        duration = wordJSON['end']-wordJSON['start']
        word_clip = TextClip(wordJSON['word'], font=font, fontsize=fontsize, color=color).set_start(
            textJSON['start']).set_duration(full_duration)
        word_clip_stroke = TextClip(wordJSON['word'], font=font, fontsize=fontsize, color=color, stroke_color=stroke_color,
                                    stroke_width=stroke_width).set_start(textJSON['start']).set_duration(full_duration)
        word_clip_space = TextClip(" ", font=font, fontsize=fontsize*spacing,
                                   color=color).set_start(textJSON['start']).set_duration(full_duration)
        word_width, word_height = word_clip.size
        space_width, space_height = word_clip_space.size

        word, start, end = wordJSON['word'], wordJSON['start'], wordJSON['end']
        dt = end - start

        word_clip = word_clip.set_position((x_pos, y_pos))
        word_clip_stroke = word_clip_stroke.set_position(
            (x_pos - stroke_width/2, y_pos - stroke_width/2))
        word_clip_space = word_clip_space.set_position(
            (x_pos + word_width, y_pos))
        word_clip_highlight = TextClip(
            word, font=font, fontsize=fontsize, color=highlight_color).set_start(start).set_duration(dt)
        word_clip_highlight = word_clip_highlight.set_position((x_pos, y_pos))

        w_init = word_width + bg_x_padding
        h_init = word_height + bg_y_padding
        w_final = int(w_init * bg_scaling)
        h_final = int(h_init * bg_scaling)
        mx, my = (w_final-w_init, h_final-h_init)
        x_init = x_pos - bg_x_padding//2
        y_init = y_pos - bg_y_padding//2
        t = kwargs.get('bg_scaling_duration', 0.25)
        scaleFunc, posFunc = makeUpdater(
            bg_scaling, t, w_init, h_init, x_init, y_init, damping, stiffness, mx, my)
        # box_color = (*bg_color, int(bg_opacity * 255))
        box_color = tuple(list(bg_color) + [int(bg_opacity * 255)])

        img = rounded_mask(w_init, h_init, bg_border_radius,
                           color=box_color, margin=(mx, my))
        color_clip = ImageClip(img, duration=duration) \
            .set_opacity(bg_opacity) \
            .set_position(posFunc) \
            .resize(scaleFunc) \
            .set_start(start) \
            .set_duration(dt) \

        line += [color_clip, word_clip_stroke, word_clip,
                 word_clip_space, word_clip_highlight]

        x_pos += word_width + space_width
        line_width += word_width + space_width
        if (line_width + word_width + space_width > max_line_width) or (index == wordcount-1):
            lines.append({"line": line, "width": line_width, "height": word_height,
                         "start": textJSON['start'], "duration": full_duration})
            line = []
            x_pos = bg_x_padding//2
            line_width = 0

    return lines, word_height


def create_video_from_subtitles(videofilename, timestamps, **kwargs):
    portions = split_text_into_lines(timestamps, **kwargs)
    input_video = VideoFileClip(videofilename)
    frame_size = input_video.size
    max_width, max_height = frame_size
    all_linelevel_splits = []
    height_perc = kwargs.get('location', 0.5)
    scale = kwargs.get('bg_scaling_factor', 1.1)
    x_padding = int(kwargs.get('x_padding', 25) * scale)
    y_padding = int(kwargs.get('y_padding', 15) * scale)

    for portion in portions:
        lines, word_height = create_caption(portion, frame_size, **kwargs)
        portion_height = len(lines) * (word_height + y_padding)
        available_height = max_height - portion_height - y_padding
        pos_y = available_height * height_perc
        for line_num, line in enumerate(lines):
            out_clips, width, height = line["line"], line["width"], line["height"]
            pos_x = (max_width - (width + x_padding))//2
            pos_y += height
            clip_to_overlay = CompositeVideoClip(out_clips, size=(
                width + x_padding, height + y_padding + 20)).set_position((pos_x, pos_y))
            all_linelevel_splits.append(clip_to_overlay)

    input_video_duration = input_video.duration
    final_video = CompositeVideoClip([input_video] + all_linelevel_splits)
    final_video = final_video.set_audio(input_video.audio)
    output_filename = videofilename.replace(".mp4", "_output.mp4")

    final_video.write_videofile(
        output_filename, fps=input_video.fps, codec="libx264", audio_codec="aac")
    return output_filename
