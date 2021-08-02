Quality Assurance (QA) for OpenTravelData (OPTD) - Container images
===================================================================

[![Docker Cloud build status](https://img.shields.io/docker/cloud/build/infrahelpers/cpppython)](https://hub.docker.com/repository/docker/infrahelpers/optd-qa/general)
[![Container repository on Quay](https://quay.io/repository/opentraveldata/quality-assurance/status "Container repository on Quay")](https://quay.io/repository/opentraveldata/quality-assurance)

# Overview
That directory structure contains the container (_e.g._, Docker) specification
files (`Dockerfile`) to produce the various container images for this project:
* A [container image to run the QA checkers](run-checkers/), cloning
  [that Git repository](https://github.com/opentraveldata/quality-assurance),
  configuring a Python virtual environment with `pipenv` and producing
  CSV-formatted issue records.
  That image inherits from a
  [generic C++/Python Docker image](https://cloud.docker.com/u/optd-qa/repository/docker/optd-qa/base)
  (built thanks to the
  [C++ showcase Docker image project](https://github.com/cpp-projects-showcase/docker-images))
* A [container image to operate a Web application hosting the OPTD QA dashboard](dashboard/)
  (yet to be developed; see just below)

Though it is not there yet, that project should produce a Quality Assurance (QA)
dashboard, much like [Geonames' one](http://qa.geonames.org/qa/).

All the container images are hosted on the
[Docker Cloud OpenTravelData (OPTD) organization](https://cloud.docker.com/u/opentraveldata/repository/docker/opentraveldata/quality-assurance),
and generated thanks to that repository.

## See also
* [Open Travel Data (OPTD) Quality Assurance (QA) project](https://github.com/opentraveldata/quality-assurance)
* [Geonames' QA dashboard](http://qa.geonames.org/qa/)
* [Quality Assurance (QA) images on Docker Cloud](https://cloud.docker.com/u/infrahelpers/repository/docker/infrahelpers/optd-qa)

# Contribute

## Build the checker runner image
* Build the container image:
```bash
$ docker build -t infrahelpers/optd-qa:latest docker/run-checkers/
```

* Launch the container image and enter into it:
```bash
$ docker run --rm -it infrahelpers/optd-qa:latest bash
[build@8ce25cc20a10 opentraveldata-qa (master)] make checkers
[build@8ce25cc20a10 opentraveldata-qa (master)] exit
```

## Upload the checker runner image to container repositories
* Submit the image to Docker Hub:
  + If not already done, log in to Docker Hub:
```bash
$ docker login docker.io
```
  + Upload the image:
```bash
$ docker push infrahelpers/optd-qa:latest
```

* Submit the image to Docker Hub:
  + If not already done, log in to Quay.io:
```bash
$ docker login quay.io
```
  + Tag the image for Quay.io:
```bash
$ docker tag infrahelpers/optd-qa:latest quay.io/opentraveldata/quality-assurance
```
  + Upload the image:
```bash
$ docker push quay.io/opentraveldata/quality-assurance
```

