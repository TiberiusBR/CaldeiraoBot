FROM python:3.8.15-slim

# Update repository cache & install ffmpeg
RUN apt-get update
RUN apt-get -y install ffmpeg

# Copy project files over to directory
RUN mkdir -p /usr/src/bot
COPY . /usr/src/bot

WORKDIR /usr/src/bot

RUN python -m pip install -r requirements.txt

EXPOSE 8000

CMD ["python3", "index.py"]