<p align="center">
  <img src="https://i.imgur.com/1yoLM55.png" />
  <br>
  <i>RNA Conserved Non-coding Elements Retrieval and Analysis Tool</i>
</p>

---

[![Build Status](https://travis-ci.com/Phil-Holland/CNE-RAT.svg?token=pzRsFpf4SapMeqEcEqKd&branch=master)](https://travis-ci.com/Phil-Holland/CNE-RAT)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

**An all-inclusive tool to locate conserved non-coding elements in RNA sequences and help further prediction of RNA CNE function through interaction prediction.**

<p align="center">
  <img src="https://i.imgur.com/ScEuAHk.png" />
</p>

## What's Included

CNE-RAT includes two sub-tools, **CNE-Finder** and **CNEAT**. CNE-Finder provides an interface to locate and extract conserved non-coding sequences from whole genome data. CNEAT, (*the CNE analysis tool*), provides an interface for three distinct analysis pipelines, aiming to predict CNE function through RNA interactions. The three pipelines are as follows:

- Evaluation of RNA-protein interactions, using [the CISBP-RNA database](http://cisbp-rna.ccbr.utoronto.ca).
- Evaluation of RNA-RNA interactions, using the [ViennaRNA package](https://www.tbi.univie.ac.at/RNA/).
- Evaluation of RNA-RNA interactions, using [IntaRNA](https://github.com/BackofenLab/IntaRNA).

## Getting Started

These instructions will get you a copy of CNE-RAT up and running on your local machine for personal use or development purposes. See deployment for notes on how to deploy the project on a live system.

The project code can be downloaded using **Git**, from this very repository using the following command:

```bash
git clone --recursive https://github.com/Phil-Holland/CNE-RAT.git
```

### Prerequisites

This application has been developed using **Docker** - all important requirements are downloaded automatically by the Docker build script. Please install the following on your machine:

- **Docker** https://www.docker.com/
- **Docker Compose** https://docs.docker.com/compose/

Additional files for RNA-Protein interaction prediction pipeline must be downloaded from the CISBP-RNA 
database. These cannot be bundled with the application's source code. Download the latest *"entire datasets archive"* zip file from the following link, and unzip its contents into the directory `./tasks/data/cisbp_rna`:

- http://cisbp-rna.ccbr.utoronto.ca/bulk.php

### Installing

Before the application can be built, some environment variables must be defined.

**Step 1:** Copy the `.env-template` file to a file named `.env`.

```bash
cp .env-template .env
```

**Step 2 (optional):** Edit the `.env` file, and set the contained environment variables for your needs. This step is not necessary if you are just running the application locally (i.e. not exposing over a network).

- `CELERY_WORKERS`: set to the desired number of concurrently running background task queue workers.
- `FLOWER_USER`: set to the desired username for the task queue management interface.
- `FLOWER_PASSWORD`: set to the desired password for the task queue management interface.
- `REDIS_PASSWORD`: set to the desired password for database access.

**Step 3:** Finally, the application can be built by running the following Docker compose command:

```bash
docker-compose build
```

This may take a few minutes the first time it is executed, as Docker must collect and build all of the necessary requirements.

### Running Locally

To run the application on your local machine, run the following Docker compose command:

```bash
docker-compose -f docker-compose.yml -f docker-compose.local.yml up
```

This will take a few seconds to initiate successfully. Once up and running, the web interface can be viewed through a web browser at [http://localhost:6565](http://localhost:6565).

***Note:*** *this may be different if you are using Docker Toolbox on Windows. If the default Docker Toolbox IP is being used for the VM, CNE-RAT will be accesible at* [http://192.168.99.100:6565](192.168.99.100:6565) *- see [this StackOverflow question](https://stackoverflow.com/questions/42866013/docker-toolbox-localhost-not-working) for more info.*

To view the task queue management interface, [Celery Flower](https://flower.readthedocs.io/en/latest/), navigate to [http://localhost:5555](http://localhost:5555). The redis database is accessible through port `6379`, and can be managed/viewed with a [suitable redis client](https://redislabs.com/blog/so-youre-looking-for-the-redis-gui/).

## Running the tests

An additional Docker compose configuration is provided to run the included integration tests. This can be built and executed using the following two Docker compose commands:

```bash
docker-compose -f docker-compose.yml -f docker-compose.test.yml build
```

```bash
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit
```

The `--abort-on-container-exit` tells Docker to exit once the tests have completed.

## Using the API

CNE-RAT exposes a **REST API** for advanced usage of the application. For more information, please read [API.md](documentation/API.md).

## Deployment

To deploy CNE-RAT on a live system, the passwords within the `.env` file should be set to secure strings. Then use the following command to run the application in "production" mode.

```bash
docker-compose -f docker-compose.yml -f docker-compose.production.yml up
```

In production mode, the web interface is accessible through port `80` by default. This can be changed by editing the `docker-compose.production.yml` file, and modifying the port mappings. 

## Built With

- [Docker](https://www.docker.com/) - used for application containerisation.
- [Flask](http://flask.pocoo.org) - used for the web application server.
- [Celery](http://www.celeryproject.org/) - used to implement the task queue.
- [Celery Flower](https://flower.readthedocs.io/en/latest/) - used to monitor the task queue.
- [Redis](https://redis.io/) - used for the application database
- [JSON Schema](https://json-schema.org/) - used to validate request objects.
- [jsonschema2md](https://github.com/adobe/jsonschema2md) - used to generate documentation from JSON schemas.
- [The CISBP-RNA database](http://cisbp-rna.ccbr.utoronto.ca) - used for the RNA-protein interaction analysis pipeline.
- [ViennaRNA](https://www.tbi.univie.ac.at/RNA/) - used for the ViennaRNA RNA-RNA interaction analysis pipeline.
- [IntaRNA](https://github.com/BackofenLab/IntaRNA) - used for the IntaRNA RNA-RNA interaction analysis pipeline.
- [Pytest](https://docs.pytest.org/en/latest/) - used to run the integration tests.
- [Requests](https://2.python-requests.org//en/master/) - used within tests to send test HTTP requests.

## Authors

- **Philip Holland** - *CNEAT* + *application framework*
- **Matthew Reggler** - *CNE Finder*
- **Liam Burke** - *RNA-protein analysis pipeline*
- **Cristina Smeu** - *IntaRNA analysis pipeline*
- **Jack Mason**

This project has been developed as part of a masters degree project at the University of Warwick. 

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.
