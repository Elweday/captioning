from moviepy.editor import TextClip, CompositeVideoClip, ColorClip

duration = 0.5
width = 400
height = 400
bg_clip = ColorClip(size=(width, height), color=(0,0,0)).set_duration(duration)
txt_clip = TextClip("Ramsri", fontsize=100, color='yellow')
txt_clip = txt_clip.set_duration(duration)
textclip_width, textclip_height = txt_clip.size

def resizeFunc(scale, duration):
    def updater(t):
        start_scale = 1
        scale = 1.4
        damping = 0.8  # Damping factor for the spring
        stiffness = 0.6  # Stiffness of the spring
        delta_scale = scale - start_scale
        spring_force = -stiffness * delta_scale
        damping_force = -damping * t * delta_scale / duration
        acceleration = (spring_force + damping_force) / duration
        scale_factor = start_scale + t/duration * (scale - start_scale) + acceleration * t
        return scale_factor
    return updater

txt_moving_resized = txt_clip.resize(resizeFunc(2, duration))
video = CompositeVideoClip([bg_clip, txt_moving_resized])
video.write_videofile("scaling_text.mp4", fps=60)
