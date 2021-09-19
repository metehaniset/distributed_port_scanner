# Linux x64
FROM python:3
RUN pip3 install --upgrade pip


WORKDIR /tmp
COPY requirements.txt .
# install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt


ADD receive.py /
ADD send.py /
ADD run.py /


CMD [ "python3", "./run.py" ]

