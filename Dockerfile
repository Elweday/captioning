FROM tburrows13/moviepy

LABEL AUTHOR="Nasser"
LABEL DESCRIPTION="Studyio Docker Image for creating subtitles for videos."

ENV PYTHONUNBUFFERED 1
RUN mkdir /home/app
COPY ./app /home/app
COPY ./requirements.txt /home/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /home/requirements.txt

CMD    ["python", "/home/app/server.py"]

