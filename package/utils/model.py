from faster_whisper import WhisperModel

def transcribe(audiofilename):
    model_size = "medium"
    model = WhisperModel(model_size)
    segments, info = model.transcribe(audiofilename, word_timestamps=True)
    return list(segments)
