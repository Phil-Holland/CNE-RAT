FROM python:3.5

ADD . /app
WORKDIR /app


# install viennarna + ghostscript
RUN apt-get update && apt-get install -y libgsl2
RUN curl https://www.tbi.univie.ac.at/RNA/download/debian/debian_9_0/viennarna_2.4.11-1_amd64.deb --output viennarna.deb
RUN dpkg -i viennarna.deb
RUN apt-get install -f -y
RUN apt-get install -y texlive-extra-utils

# install conda
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH
 
RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion
 
RUN wget --quiet https://repo.anaconda.com/archive/Anaconda2-2018.12-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /opt/conda && \
    rm ~/anaconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc
 
#install inta
RUN conda install -c conda-forge -c bioconda intarna

# install python requirements
RUN pip install -r requirements.txt

RUN mkdir -p /var/log/celery
RUN mkdir -p /var/run/celery

ENTRYPOINT ["sh", "start_script.sh"]