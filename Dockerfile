FROM python:3.9
MAINTAINER Dang Hoang Tuan "danghoangtuan526@proton.me"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN ./run_server.sh
