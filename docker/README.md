Quality Assurance (QA) for OpenTravelData (OPTD) - Docker images
================================================================

# Overview
That directory structure contains the Docker specification files
(`Dockerfile`) to produce the various Docker images for this project:
* A [base Docker image](base/), cloning
  [that Git repository](http://github.com/opentraveldata/quality-assurance)
  and configuring a Python virtual environment with `pyenv` and `pipenv`
* A [Docker image to run the QA checkers](run-checkers/)
  and producing JSON-formatted issue records
* A [Docker image to operate a Web application hosting the OPTD QA dashboard](dashboard/)
  (yet to be developed; see just below)

Though it is not there yet, that project should produce a Quality Assurance (QA)
dashboard, much like [Geonames' one](http://qa.geonames.org/qa/).

All the Docker images are hosted on the
[Docker Cloud OpenTravelData (OPTD) organization](https://cloud.docker.com/u/opentraveldata/repository/docker/opentraveldata/quality-assurance),
and generated thanks to that repository.

## See also
* [Open Travel Data (OPTD) Quality Assurance (QA) project](../)
* [Geonames' QA dashboard](http://qa.geonames.org/qa/)
* [Quality Assurance (QA) images on Docker Cloud](https://cloud.docker.com/u/opentraveldata/repository/docker/opentraveldata/quality-assurance)

# Manual build

## Base image
```bash
$ docker build -t opentraveldata/quality-assurance:base-beta docker/base/
$ docker run --rm -it opentraveldata/quality-assurance:base-beta bash
```

## Checker runner
```bash
$ docker build -t opentraveldata/quality-assurance:checker-runner-beta docker/run-checkers/
$ docker run --rm -it -v ${PWD}/to_be_checked:/root/dev/geo/opentraveldata-qa/to_be_checked -v ${PWD}/results:/root/dev/geo/opentraveldata-qa/results opentraveldata/quality-assurance:checker-runner-beta bash
```

