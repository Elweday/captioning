from moviepy.editor import TextClip, CompositeVideoClip, ColorClip

duration = 0.5
width = 400
height = 400
bg_clip = ColorClip(size=(width, height), color=(0,0,0)).set_duration(duration)
txt_clip = TextClip("Ramsri", fontsize=100, color='yellow')
txt_clip = txt_clip.set_duration(duration)
textclip_width, textclip_height = txt_clip.size

txt_moving_resized = txt_clip.resize(resizeFunc(2, duration))
video = CompositeVideoClip([bg_clip, txt_moving_resized])
video.write_videofile("scaling_text.mp4", fps=60)