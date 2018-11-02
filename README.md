Quality Assurance (QA) for OpenTravelData (OPTD)
================================================

# Overview
That repository features scripts to check the quality of the data files
produced by the Open Travel Data (OPTD) project.

Though it is not there yet, that project should produce
a Quality Assurance (QA) dashboard, much like
[Geonames' one](http://qa.geonames.org/qa/).

And, hopefully, that dashboard will be powered by
a [Docker image](https://hub.docker.com/r/opentraveldata/quality-assurance/builds/)
generated thanks to that repository as well.

## See also
* [Service Delivery Quality (SDQ) GitHub organization](https://github.com/service-delivery-quality)
  + [Quality Assurance samples](https://github.com/service-delivery-quality/quality-assurance)
* [Geonames' QA dashboard](http://qa.geonames.org/qa/)
* [Quality Assurance (QA) images on Docker Hub](https://hub.docker.com/r/opentraveldata/quality-assurance)
* [How to set up a Python virtual environment](http://github.com/machine-learning-helpers/induction-python/tree/master/installation/virtual-env)

# Installation

## Through a pre-built Docker image
* Retrieve the Docker image:
```bash
$ docker pull opentraveldata/quality-assurance
```

* Launch the Docker-powered scripts:
```bash
$ docker run --rm -it opentraveldata/quality-assurance:latest bash
$ pipenv run checker/checkers/check-por-cmp-optd-unlc.py > results/optd-qa-por-optd-vs-unlc.json
```

### Docker image manual build
* If, for some reason (for instance to customize the Docker image),
  the Docker image needs to be manually rebuilt:
```bash
$ docker build -t opentraveldata/quality-assurance:myownimg .
$ docker run --rm -it opentraveldata/quality-assurance:myownimg bash
$ pipenv run checker/checkers/check-por-cmp-optd-unlc.py > results/optd-qa-por-optd-vs-unlc.json
```

## Through a local cloned Git repository
* Clone the [OpenTravelData (OPTD) Quality Assurance (QA) Git repository](https://github.com/opentraveldata/quality-assurance)
```bash
$ mkdir -p ~/dev/geo && cd ~/dev/geo
$ git clone https://github.com/opentraveldata/quality-assurance.git opentraveldata-qa
$ cd opentraveldata-qa
$ ./mkLocalDir.sh
```

* Install supplementary Python packages through ``pipenv``:
```bash
$ pipenv install numpy networkx
```

## Launch the Python checkers
* Use ``pipenv`` to launch the Python scripts. For instance:
```bash
$ pipenv run python ./checkers/check-por-cmp-optd-unlc.py > results/optd-qa-por-optd-vs-unlc.json
$ wc -l results/optd-qa-por-optd-vs-unlc.json 
110001 results/optd-qa-por-optd-vs-unlc.json
$ ls -lFh to_be_checked/
total 14M
-rw-r--r-- 1 root root 4.7M Nov  2 14:02 optd_por_unlc.csv
-rw-r--r-- 1 root root 8.6M Nov  2 14:02 unlocode-code-list-latest.csv
```

# Checks
## Airlines - Airport Bases / Hubs
Check, for every airline of the
[optd_airlines.csv file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv),
that the airport bases/hubs are appearing in the
[optd_airline_por.csv file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por.csv).

Note that both files ([optd_airlines.csv](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv)
and [optd_airline_por.csv](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por.csv))
will be downloaded from the
[OpenTravelData project](http://github.com/opentraveldata/opentraveldata)
and stored within the 'to_be_checked' directory. If those files are too old,
they should be removed (a newer version will be automatically downloaded
and stored again).

* The following script displays all the missing airport bases/hubs:
```bash
$ ./mkLocalDir.sh
$ pipenv run python checkers/check-airline-bases.py | tee results/optd-qa-airline-bases.json
```

If the script does not return anything, then the check (successfully) passes.


