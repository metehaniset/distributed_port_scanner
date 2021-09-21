
# Linux x64
FROM python:3.8
RUN pip3 install --upgrade pip
# Set PYTHONPATH
ENV PYTHONPATH="/app/"
ENV FLASK_APP="/app/webui/webui.py"

WORKDIR /tmp
COPY requirements.txt .
# install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt


# Set timezone
ENV TZ=Europe/Istanbul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ADD . /app

WORKDIR /app
RUN rm Dockerfile docker-compose.yml
RUN rm -rf deployment

WORKDIR /app/webui
RUN rm app.db
