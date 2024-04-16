import moviepy.editor as mpe
import tempfile

fo = tempfile.NamedTemporaryFile(dir="", delete=False)
print("file name: ", fo.name)


with open("sample_output.mp4", "rb") as f:
    content = f.read()
    fo.write(content)


  
video_clip = mpe.VideoFileClip(fo.name)
text_clip = mpe.TextClip("Watermark", fontsize=70, color='white').set_duration(2)
text_clip = text_clip.set_position('center')
watermarked_video = mpe.CompositeVideoClip([video_clip, text_clip])
watermarked_video.write_videofile(fo.name,  codec='libx264')

with open("test_file_test.mp4", "wb") as output_file:
    print("should have been written")
    f.write(fo.read())



fo.close()