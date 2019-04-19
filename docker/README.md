Quality Assurance (QA) for OpenTravelData (OPTD) - Docker images
================================================================

# Overview
That directory structure contains the Docker specification files
(`Dockerfile`) to produce the various Docker images for this project:
* A [Docker image to run the QA checkers](run-checkers/), cloning
  [that Git repository](https://github.com/opentraveldata/quality-assurance),
  configuring a Python virtual environment with `pipenv` and producing
  CSV-formatted issue records.
  That image inherits from a
  [generic C++/Python Docker image](https://cloud.docker.com/u/cpppythondevelopment/repository/docker/cpppythondevelopment/base)
  (built thanks to the
  [C++ showcase Docker image project](https://github.com/cpp-projects-showcase/docker-images))
* A [Docker image to operate a Web application hosting the OPTD QA dashboard](dashboard/)
  (yet to be developed; see just below)

Though it is not there yet, that project should produce a Quality Assurance (QA)
dashboard, much like [Geonames' one](http://qa.geonames.org/qa/).

All the Docker images are hosted on the
[Docker Cloud OpenTravelData (OPTD) organization](https://cloud.docker.com/u/opentraveldata/repository/docker/opentraveldata/quality-assurance),
and generated thanks to that repository.

## See also
* [Open Travel Data (OPTD) Quality Assurance (QA) project](https://github.com/opentraveldata/quality-assurance)
* [Geonames' QA dashboard](http://qa.geonames.org/qa/)
* [Quality Assurance (QA) images on Docker Cloud](https://cloud.docker.com/u/opentraveldata/repository/docker/opentraveldata/quality-assurance)

# Manual build

## Checker runner
```bash
$ docker build -t opentraveldata/quality-assurance:run-checkers-beta docker/run-checkers/
$ docker run --rm -it opentraveldata/quality-assurance:run-checkers-beta bash
```

