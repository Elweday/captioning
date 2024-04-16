FROM tburrows13/moviepy

LABEL AUTHOR="Nasser"
LABEL DESCRIPTION="Studyio Docker Image for creating subtitles for videos."

ENV PYTHONUNBUFFERED 1
RUN mkdir /home/code
COPY . /home/code
RUN pip install --upgrade pip
RUN pip install -r /home/code/requirements.txt


# Entrypoint configuration
CMD    ["python", "/home/code/server.py"]
