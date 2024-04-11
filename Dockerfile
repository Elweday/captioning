FROM tburrows13/moviepy

LABEL AUTHOR="Nasser"
LABEL DESCRIPTION="Studyio Docker Image for creating subtitles for videos. Based on dkarchmervue/moviepy"

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt


# Copy Python script
ADD app /code/app

# Entrypoint configuration
CMD    ["python", "/code/app/main.py"]
