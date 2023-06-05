FROM python:3.11.1-slim

RUN apt-get -y update
RUN apt-get install -y ffmpeg

WORKDIR /converter

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install gunicorn

COPY ./converter/app app
COPY ./converter/migrations ./migrations
COPY ./converter/.flaskenv ./converter/config.py ./converter/converter.py ./converter/boot.sh ./
RUN chmod +x boot.sh

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]