FROM python:3.5

ADD . /app
WORKDIR /app


# install viennarna + ghostscript
RUN apt-get update && apt-get install -y libgsl2
RUN curl https://www.tbi.univie.ac.at/RNA/download/debian/debian_9_0/viennarna_2.4.11-1_amd64.deb --output viennarna.deb
RUN dpkg -i viennarna.deb
RUN apt-get install -f -y
RUN apt-get install -y texlive-extra-utils

# install python requirements
RUN pip install -r requirements.txt

RUN mkdir -p /var/log/celery
RUN mkdir -p /var/run/celery

ENTRYPOINT ["sh", "start_script.sh"]