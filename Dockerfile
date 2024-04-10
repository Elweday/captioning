FROM dkarchmervue/moviepy

LABEL AUTHOR="Nasser"
LABEL DESCRIPTION="Studyio Docker Image for creating subtitles for videos. Based on dkarchmervue/moviepy"
# ============================================================================
# As an example, create a clip with a 'Hello World' title
#
# ~~~~
# # Pull image
# docker pull dkarchmervue/moviepy
#
# # Get example files and build new image
# git clone https://github.com/ampervue/docker-ffmpeg-moviepy
# cd example
# docker build -t example .
#
# # Mount current directory on container so that file can be written back to host
# # Assuming videos are on current directory
# docker run --rm -ti -v ${PWD}:/code example
# ls hello_world.mp4
# ~~~~
# ============================================================================

# Installing Python packages

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt

# Copy Python script
ADD app /code/app

# Entrypoint configuration
CMD           ["-h"]
ENTRYPOINT    ["python", "/code/app/script.py"]