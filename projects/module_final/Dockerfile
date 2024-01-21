FROM python:3.10.13-slim-bullseye

RUN apt update &&  apt install -y gcc

COPY requirements.txt /

RUN pip3 install --upgrade pip

RUN pip3 install -r /requirements.txt

EXPOSE 8080

WORKDIR /opt/app

COPY webservice .
COPY export ./data

ENTRYPOINT ["waitress-serve", "--host", "0.0.0.0", "app:app"]
