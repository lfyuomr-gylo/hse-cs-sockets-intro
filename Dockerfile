FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3.8

COPY echo.py /server/server.py
COPY static_data/ /server/static_data

ENTRYPOINT ["python3.8", "/server/server.py"]
