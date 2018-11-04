Quality Assurance (QA) for OpenTravelData (OPTD) - Docker images
================================================================

# Overview
That directory structure contains the Docker specification files
(``Dockerfile``) to produce the various Docker images for this project:
* A [base Docker image](base/),
  cloning [that Git repository](https://hub.docker.com/r/opentraveldata/quality-assurance)
  and configuring a Python virtual environment with ``pipenv``
* A [Docker image to run the QA checkers](run-checkers/)
  and producing JSON-formatted issue records
* A [Docker image to operate a Web application hosting the OPTD QA dashboard](dashboard/)
  (yet to be developed; see just below)

Though it is not there yet, that project should produce
a Quality Assurance (QA) dashboard, much like
[Geonames' one](http://qa.geonames.org/qa/).

All the Docker images are hosted on the
[Docker Hub OpenTravelData (OPTD) organization](https://hub.docker.com/r/opentraveldata/quality-assurance/builds/),
and generated thanks to that repository.

## See also
* [Open Travel Data (OPTD) Quality Assurance (QA) project](../)
* [Geonames' QA dashboard](http://qa.geonames.org/qa/)
* [Quality Assurance (QA) images on Docker Hub](https://hub.docker.com/r/opentraveldata/quality-assurance)

# Manual build

## Base image
```bash
$ docker build -t opentraveldata/quality-assurance:mybaseimg base/
$ docker run --rm -it opentraveldata/quality-assurance:mybaseimg bash
```

## Checker runner
```bash
$ docker build -t opentraveldata/quality-assurance:mycheckerrunnerimg run-checkers/
$ docker run --rm -it -v ${PWD}/notebook/induction:/notebook -v ${PWD}/data/induction:/data opentraveldata/quality-assurance:mycheckerrunnerimg bash
```

