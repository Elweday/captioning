FROM jarrodhroberson/moviepy

LABEL AUTHOR="Nasser"
LABEL DESCRIPTION="Studyio Docker Image for creating subtitles for videos. Based on dkarchmervue/moviepy"

# Installing Python packages

ENV PYTHONUNBUFFERED 1
ADD . .
RUN pip install -r requirements.txt

# Entrypoint configuration
CMD           ["python", "server.py"]