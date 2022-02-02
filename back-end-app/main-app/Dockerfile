FROM python:3.8-slim

#RUN apt-get update -y && \
#    apt-get install -y python3-pip python3-dev

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt
RUN ["chmod", "+x", "/app/start.sh"]

ENTRYPOINT [ "python3" ]

CMD ["/app/run.py"]