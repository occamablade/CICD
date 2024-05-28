FROM python:3.11-slim

RUN apt-get update && apt-get install gcc libsnmp-dev iputils-ping -y  \
    && pip install --upgrade pip && apt-get -y install curl && apt-get clean

ENV VENV="/venv"

WORKDIR /HS

COPY . /HS

RUN pip3 install -r requirements.txt

CMD ["/bin/bash"]
