<p align="center">
  <img src="https://i.imgur.com/1yoLM55.png" />
  <br>
  <i>The Conserved Non-coding Elements Retrieval and Analysis Tool</i>
</p>

---

[![Build Status](https://travis-ci.com/Phil-Holland/CNEAT.svg?token=pzRsFpf4SapMeqEcEqKd&branch=master)](https://travis-ci.com/Phil-Holland/CNEAT)

**An all-inclusive tool to locate conserved non-coding elements and help further prediction of CNE function through evaluation of RNA interactions.**

![](https://i.imgur.com/Qq1wnmm.png)

## What's Included

CNE-RAT includes two sub-tools, **CNE-Finder** and **CNEAT**. CNE-Finder provides an interface to locate and extract conserved non-coding sequences from whole genome data. CNEAT, (*the CNE analysis tool*), provides an interface for three distinct analysis pipelines, aiming to predict CNE function through RNA interactions. The three pipelines are as follows:

- Evaluation of RNA-protein interactions, using [the CISBP-RNA database](http://cisbp-rna.ccbr.utoronto.ca).
- Evaluation of RNA-RNA interactions, using the [ViennaRNA package](https://www.tbi.univie.ac.at/RNA/).
- Evaluation of RNA-RNA interactions, using [IntaRNA](https://github.com/BackofenLab/IntaRNA).

## Getting Started

These instructions will get you a copy of CNE-RAT up and running on your local machine for personal use or development purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This application has been developed using **Docker** - all important requirements are downloaded automatically by the Docker build script. Please install the following on your machine:

- **Docker** https://www.docker.com/
- **Docker Compose** https://docs.docker.com/compose/

Additional files for RNA-Protein interaction prediction pipeline must be downloaded from the CISBP-RNA 
database. These cannot be bundled with the application's source code. Download the latest zip file from the following link, and unzip its contents into the directory `./tasks/data/cisbp_rna`:

- http://cisbp-rna.ccbr.utoronto.ca/bulk.php

### Installing

Before the application can be built, you must define some environment variables.

**Step 1:** Copy the `.env-template` file to a file named `.env`.

```bash
cp `.env-template` `.env`
```

**Step 2:** Edit the `.env` file, and set the contained environment variables for your needs. This step it not necessary if you are just running the application locally (i.e. not exposing over a network or developing).

- `DEBUG`: set to `0` to run in "production" mode, or `1` to run in "development" mode.
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
docker-compose up
```

This will take a few seconds to initiate successfully. Once up and running, the web interface can be viewed through a web browser at [http://localhost:6565](http://localhost:6565).

***Note:*** *this may be different if you are using Docker Toolbox on Windows. If the default Docker Toolbox IP is being used for the VM, CNE-RAT will be accesible at* [http://192.168.99.100:6565](192.168.99.100:6565) *- see [this StackOverflow question](https://stackoverflow.com/questions/42866013/docker-toolbox-localhost-not-working) for more info.*

## Running the tests

An additional Docker compose configuration is provided to run the included integration tests. This can be built and executed using the following two Docker compose commands:

```bash
docker-compose -f docker-compose.yml -f docker-compose.test.yml build
```

```bash
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit
```

## Deployment

To deploy CNE-RAT on a live system, the password within the `.env` file should be set as secure strings. Also ensure that the `DEBUG` variable is set to `0`.

## Built With

- [Docker](https://www.docker.com/) - used for application containerisation.
- [Flask](http://flask.pocoo.org) - used for the web application server.
- [Celery](http://www.celeryproject.org/) - used to implement the task queue.
- [Celery Flower](https://flower.readthedocs.io/en/latest/) - used to monitor the task queue.
- [Redis](https://redis.io/) - used for the application database
- [The CISBP-RNA database](http://cisbp-rna.ccbr.utoronto.ca) - used for the RNA-protein interaction analysis pipeline.
- [ViennaRNA](https://www.tbi.univie.ac.at/RNA/) - used for the ViennaRNA RNA-RNA interaction analysis pipeline.
- [IntaRNA](https://github.com/BackofenLab/IntaRNA) - used for the IntaRNA RNA-RNA interaction analysis pipeline.
- [Pytest](https://docs.pytest.org/en/latest/) - used to write the integration tests.

## Authors

- **Philip Holland** - *CNEAT* + *application framework*
- **Matthew Reggler** - *CNE Finder*
- **Liam Burke** - *RNA-protein analysis pipeline*
- **Cristina Smeu** - *IntaRNA analysis pipeline*
- **Jack Mason**

This project has been developed as part of a masters degree project at the University of Warwick. 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
