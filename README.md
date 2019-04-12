# CNE Finder + CNEAT

This project includes two tools used for the identification and analysis of conserved non-coding elements.

- **CNE Finder**
	- Processes whole genome sequence data, to locate potential **C**onserved **N**on-coding **E**lements.
- **CNEAT**
	- The **C**onserved **N**on-coding **E**lement **A**nalysis **T**ool.
	- Investigates potential RNA interactions involving the CNE sequence.

## Usage Guide

### Setup

**IMPORTANT!**

- This application has been written using **Docker**.
	- Please visit https://www.docker.com/get-started to install Docker on your system.
- Additionally, **Docker Compose** is also required 
	- Please visit https://docs.docker.com/compose/install/ to install Docker compose on your system
- Create a new file named `.env` in the project's root directory, using the `.env-template` file as a template.
	- Change the username/password values to secure your application (necessary if the tool is not being used privately).
- Some additional files must be downloaded to allow the RNA-protein analysis pipeline to execute successfully, which cannot be distributed with this project.
	- Please go to the following URL: http://cisbp-rna.ccbr.utoronto.ca/bulk.php
	- Click on the "Download Entire Datasets Archive" button, and download the linked zip file. 
	- Extract the contents of this archive into the directory `./tasks/data/cisbp_rna`.

### Running

- Once the prerequisite setup has been completed, running the following `docker-compose` commands in the project root will build and start the application:
 
```
docker-compose build

docker-compose up
```

- `docker-compose build` may take a long time to complete on first run.
- Once the application has started successfully, the web interface can be accessed at [http://localhost:6565](http://localhost:6565).
	- *This may be different if using Docker toolbox, see: https://stackoverflow.com/questions/42866013/docker-toolbox-localhost-not-working*

### Configuration/Monitoring

- By default, the application is set to run in **production** mode, using the Python WSGI HTTP Server ["Gunicorn"](https://gunicorn.org/). To run in **development** mode, modify the `.env` file to set `DEBUG=1`.
- Redis is used internally for analysis data storage, and as a task broker (see http://www.celeryproject.org/). 
	- A redis client can be used to inspect the data store.
	- By default, this can be accessed through port `9736`.
	- See the file `docker-compose.yml` for more information on exposed ports.
- Celery is used to process jobs. *Flower* is a web interface to monitor task progress + worker status.
	- By default, this can be accessed through port `5555`.
	- This monitoring interface is protected with simple authentication. To set the admin username + password, change the `FLOWER_USER` and `FLOWER_PASSWORD` environment variables in the `.env` file.