Quality Assurance (QA) for OpenTravelData (OPTD)
================================================

# Overview
That repository features scripts to check the quality of the data files
produced by the Open Travel Data (OPTD) project.

Though it is not there yet, that project should produce
a Quality Assurance (QA) dashboard, much like
[Geonames' one](http://qa.geonames.org/qa/).

And, hopefully, that dashboard will be powered by [Docker images](docker/)
generated thanks to that repository as well.

The scripts should generate CSV data files, which can then be uploaded
in databases, or served through standard Web applications.
For historical reasons, however, most of the scripts still generate JSON
structures on the standard output. JSON should be used only for metadata,
not for the data itself.

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
$ docker pull opentraveldata/quality-assurance:base
```

* Launch the Docker-powered scripts:
```bash
$ docker run --rm -it opentraveldata/quality-assurance:base bash
[root@8ce25cc20a10 opentraveldata-qa (master)] exit
```

### Docker image manual build
* See [the Docker section for more details](docker/)

## Through a local cloned Git repository
* Clone the [OpenTravelData (OPTD) Quality Assurance (QA) Git repository](https://github.com/opentraveldata/quality-assurance)
```bash
$ mkdir -p ~/dev/geo && cd ~/dev/geo
$ git clone https://github.com/opentraveldata/quality-assurance.git opentraveldata-qa
$ cd opentraveldata-qa
$ ./mkLocalDir.sh
```

* Install supplementary Python packages through ``pipenv``.
  References:
  + [``pyproj`` compilation](https://stackoverflow.com/questions/51963619/pyproj-fails-to-compile-when-i-pip-install-it-and-its-not-about-gcc)
```bash
$ pipenv install numpy matplotlib networkx cython \
         git+https://github.com/jswhit/pyproj.git#egg=pyproj \
         git+https://github.com/matplotlib/basemap.git#egg=basemap
```

## Launch the Python checkers
* Use ``pipenv`` to launch the Python scripts. For instance:
```bash
$ pipenv run checkers/check-por-cmp-optd-unlc.py
```

# Checks

## Points of Reference (POR)

### OPTD vs UN/LOCODE
* That script compares the
  [OPTD-referenced POR](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_unlc.csv)
  with the ones referenced by
  [UN/LOCODE](http://github.com/opentraveldata/opentraveldata/blob/master/data/unlocode).
  It generates two CSV files:
  + ``results/optd-qa-por-optd-not-in-unlc.csv``, exhibiting the POR
    referenced by OPTD but not by UN/LOCODE
  + ``iresults/optd-qa-por-unlc-not-in-optd.csv``, exhibiting the POR
    referenced by UN/LOCODE but not by OPTD
```bash
$ pipenv run checkers/check-por-cmp-optd-unlc.py
$ wc -l results/optd-qa-por-unlc-not-in-optd.csv
10351 results/optd-qa-por-unlc-not-in-optd.csv
$ ls -lFh results/optd-qa-por-*.csv
-rw-r--r-- 1 root root 4.7M Nov  4 18:22 results/optd-qa-por-optd-not-in-unlc.csv
-rw-r--r-- 1 root root 763K Nov  4 18:22 results/optd-qa-por-unlc-not-in-optd.csv
```

* In order to get the IATA-referenced POR out of UN/LOCODE-referenced ones:
```bash
$ awk -F'^' '{if ($2 != "") {print $0}}' results/optd-qa-por-unlc-not-in-optd.csv | wc -l
22
```

## Airlines

### Airport Bases / Hubs
Check, for every airline of the
[optd_airlines.csv file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv),
that the airport bases/hubs are appearing in the
[optd_airline_por.csv file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por.csv).

Note that both files ([optd_airlines.csv](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv)
and [optd_airline_por.csv](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por.csv))
will be downloaded from the
[OpenTravelData project](http://github.com/opentraveldata/opentraveldata)
and stored within the ``to_be_checked`` directory. If those files are too old,
they should be removed (a newer version will be automatically downloaded
and stored again).

* The following script displays all the missing airport bases/hubs:
```bash
$ ./mkLocalDir.sh
$ pipenv run checkers/check-airline-bases.py | tee results/optd-qa-airline-bases.json
```

If the script does not return anything, then the check (successfully) passes.

### Airline networks
* For every airline of the
  [optd_airlines.csv file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv),
  perform some basic statistics on their network, modelled as graph (where
  POR are nodes and flight segments/legs are edges):  
```bash
$ pipenv run checkers/check-airline-networks.py > results/optd-qa-airline-networks.json
```


