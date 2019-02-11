FROM python:3.5

ADD . /app
WORKDIR /app

# install python requirements
RUN pip install -r requirements.txt

RUN mkdir -p /var/log/celery
RUN mkdir -p /var/run/celery
ENTRYPOINT ["sh", "start_script.sh"]