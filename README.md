# Team Origene

This project includes two tools used for the identification and analysis of conserved non-coding elements.

- **CNE Finder**
	- Processes whole genome sequence data, to locate potential CNEs.
- **CNEAT**
	- The **C**onserved **N**on-coding **E**lement **A**nalysis **T**ool.
	- Attempts to predict potential RNA interactions involving the CNE sequence.


## Running

- This application has been written using *Docker*.
- Once *Docker* + *Docker compose* have been installed, running the following commands in the project root will build and start the application:

```
docker-compose build

docker-compose up
```

- Redis is used internally for analysis job storage, and as a task broker (see http://www.celeryproject.org/). 
	- A redis client can be used to inspect the data store.
	- By default, this can be accessed through port `9736`.
	- See the file `docker-compose.yml` for more information on exposed ports.
- Celery is used to process jobs. *Flower* is a web interface to monitor task progress + worker status.
	- By default, this can be accessed through port `5555`.
