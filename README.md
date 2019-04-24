Quality Assurance (QA) for OpenTravelData (OPTD)
================================================

[![Build Status](https://travis-ci.com/opentraveldata/quality-assurance.svg?branch=master)](https://travis-ci.com/opentraveldata/quality-assurance)

# Overview
[That repository](http://github.com/opentraveldata/quality-assurance)
features scripts to check the quality of the data files
produced by the Open Travel Data (OPTD) project.

Though it is not there yet, that project should produce
a Quality Assurance (QA) dashboard, much like
[Geonames' one](http://qa.geonames.org/qa/).

And, hopefully, that dashboard will be powered by
[Docker images](http://github.com/opentraveldata/quality-assurance/blob/master/docker/)
generated thanks to that repository as well.

[Travis CI](https://travis-ci.com) builds are partially covering the tests
in https://travis-ci.com/opentraveldata/quality-assurance

Most of the scripts generate CSV data files, which can then be uploaded
in databases, or served through standard Web applications.
For historical reasons, some scripts may still generate JSON structures
on the standard output. In the future, JSON should be used only for metadata,
not for the data itself.

## See also
* [Service Delivery Quality (SDQ) GitHub organization](https://github.com/service-delivery-quality)
  + [Quality Assurance samples](https://github.com/service-delivery-quality/quality-assurance)
* [Geonames' QA dashboard](http://qa.geonames.org/qa/)
* [Quality Assurance (QA) images on Docker Cloud](https://cloud.docker.com/u/opentraveldata/repository/docker/opentraveldata/quality-assurance)
* [How to set up a Python virtual environment](https://github.com/machine-learning-helpers/induction-python/tree/master/installation/virtual-env)

# Quick starter

## Through a pre-built Docker image
* Retrieve the Docker image:
```bash
$ docker pull opentraveldata/quality-assurance:base
```

* Launch the Docker-powered scripts:
```bash
$ docker run --rm -it opentraveldata/quality-assurance:base bash
[build@8ce25cc20a10 opentraveldata-qa (master)] make checkers
[build@8ce25cc20a10 opentraveldata-qa (master)] exit
```


# Installation

## With a manually built Docker image
* See
  [the Docker section for more details](http://github.com/opentraveldata/quality-assurance/blob/master/docker/)

## Through a local cloned Git repository (without Docker)
* Clone the [OpenTravelData (OPTD) Quality Assurance (QA) Git repository](https://github.com/opentraveldata/quality-assurance):
```bash
$ mkdir -p ~/dev/geo
$ git clone https://github.com/opentraveldata/quality-assurance.git ~/dev/geo/opentraveldata-qa
$ pushd ~/dev/geo/opentraveldata-qa
$ ./mkLocalDir.sh
$ popd
```

## On the local environment (without Docker)
As detailed in the
[online guide on how to set up a Python virtual environment](http://github.com/machine-learning-helpers/induction-python/tree/master/installation/virtual-env),
[Pyenv](https://github.com/pyenv/pyenv) and
[`pipenv`](http://pypi.org/project/pipenv) should be installed,
and Python 3.7 installed thanks to Pyenv.
Then all the Python scripts will be run thanks to `pipenv`.

### Pyenv and `pipenv`
* As a summary of what has been detailed in above-mentioned how-to (and which
  only be done once and for all):
```bash
$ if [ ! -d ${HOME}/.pyenv ]; then pushd ${HOME} && git clone https://github.com/pyenv/pyenv.git $HOME/.pyenv && popd; else pushd ${HOME}/.pyenv && git pull && popd; fi
$ export PYENV_ROOT="${HOME}/.pyenv"; export PATH="${PYENV_ROOT}/.pyenv/shims:${PATH}"; if command -v pyenv 1>/dev/null 2>&1; then eval "$(pyenv init -)"; fi
$ pyenv install 3.7.2 && pyenv global 3.7.2 && pip install -U pip pipenv && pyenv global system
$ pushd ~/dev/geo/opentraveldata-qa
$ pipenv install
$ popd
```

* To update the Python dependencies:
```bash
$ pushd ~/dev/geo/opentraveldata-qa
$ pipenv update
$ popd
```

## Launch the Python checkers
* Use the `Makefile` to launch all the checkers:
```bash
$ make checkers
```

* Use `pipenv` to launch specific Python scripts. For instance:
```bash
$ pipenv run checkers/check-por-cmp-optd-unlc.py
```

# Checks

## Points of Reference (POR)

### OPTD consistency and Geonames ID
* [That script](http://github.com/opentraveldata/quality-assurance/blob/master/checkers/check-por-geo-id-in-optd.py)
  compares the
  [OPTD public POR file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv)
  with the
  [curated file of best known POR](https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_best_known_so_far.csv).
  It generates two CSV files:
  + `results/optd-qa-por-best-not-in-optd.csv`, exhibiting the POR manually
    curated in the 
	[file of best known POR](https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_best_known_so_far.csv)
	but not present in the
    [generated OPTD public file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv)
  + `results/optd-qa-por-cmp-geo-id.csv`, reporting POR having a
    [Geonames](http://github.com/opentraveldata/opentraveldata/blob/master/data/geonames)
	ID inconsistent among the
	[curated file of best known POR](https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_best_known_so_far.csv)
	and the
    [generated OPTD public file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv)

* Note that a CSV file has a single row, it is the header. So, it can be
  considered as empty.
```bash
$ pushd ~/dev/geo/opentraveldata-qa
$ pipenv run checkers/check-por-geo-id-in-optd.py
$ wc -l results/optd-qa-por-best-not-in-optd.csv results/optd-qa-por-cmp-geo-id.csv
11 results/optd-qa-por-best-not-in-optd.csv
 1 results/optd-qa-por-cmp-geo-id.csv
$ ls -lFh results/optd-qa-por-best-not-in-optd.csv results/optd-qa-por-cmp-geo-id.csv
-rw-r--r--  1 user staff 400B Jan 10 15:54 results/optd-qa-por-best-not-in-optd.csv
-rw-r--r--  1 user staff  60B Jan 10 15:54 results/optd-qa-por-cmp-geo-id.csv
$ popd
```

### POR having no geo-location in OPTD
* [That script](http://github.com/opentraveldata/quality-assurance/blob/master/checkers/check-por-optd-no-geocoord.py)
  spots POR missing geo-location in the
  [OPTD public POR file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv).
  It generates a CSV file:
  + `results/optd-qa-por-optd-no-geocoord.csv`, reporting the POR having no
  geo-location (geo-coordinates)

* Note that if a CSV file has a single row, it is the header. So, it can be
  considered as empty.
```bash
$ pushd ~/dev/geo/opentraveldata-qa
$ pipenv run checkers/check-por-optd-no-geocoord.py
$ wc -l results/optd-qa-por-optd-no-geocoord.csv
 1 results/optd-qa-por-optd-no-geocoord.csv
$ ls -lFh results/optd-qa-por-optd-no-geocoord.csv
-rw-r--r--  1 user staff 27B Apr 24 08:20 results/optd-qa-por-optd-no-geocoord.csv
$ popd
```

### City POR not in OPTD
* [That script](http://github.com/opentraveldata/quality-assurance/blob/master/checkers/check-por-city-not-in-optd.py)
  compares the
  [OPTD public POR file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv)
  with the
  [curated file of best known POR](https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_best_known_so_far.csv).
  It generates a CSV file:
  + `results/optd-qa-por-city-not-in-optd.csv`, reporting the POR in the curated 
  [file of best known POR](https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_best_known_so_far.csv)
  with cities not referenced as a city in the
  [generated OPTD public file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv)

* Note that if a CSV file has a single row, it is the header. So, it can be
  considered as empty.
```bash
$ pushd ~/dev/geo/opentraveldata-qa
$ pipenv run checkers/check-por-city-not-in-optd.py
$ wc -l results/optd-qa-por-city-not-in-optd.csv
 3 results/optd-qa-por-city-not-in-optd.csv
$ ls -lFh results/optd-qa-por-city-not-in-optd.csv
-rw-r--r--  1 user staff 113B Jan 10 15:54 results/optd-qa-por-city-not-in-optd.csv
$ popd
```

### Multi-city POR in OPTD
* [That script](http://github.com/opentraveldata/quality-assurance/blob/master/checkers/check-por-multiple-cities.py)
  compares the
  [OPTD public POR file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv)
  with the
  [curated file of best known POR](https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_best_known_so_far.csv).
  It generates two CSV files:
  + `results/optd-qa-por-multi-city.csv`, reporting POR with multiple cities
  + `results/optd-qa-por-multi-city-not-std.csv`, reporting POR
    with multiple cities not following the sorting order of PageRank values

* Note that if a CSV file has a single row, it is the header. So, it can be
  considered as empty.
```bash
$ pushd ~/dev/geo/opentraveldata-qa
$ pipenv run checkers/check-por-multiple-cities.py
$ wc -l results/optd-qa-por-multi-city.csv results/optd-qa-por-multi-city-not-std.csv
91 results/optd-qa-por-multi-city.csv
30 results/optd-qa-por-multi-city-not-std.csv
$ ls -lFh results/optd-qa-por-multi-city.csv results/optd-qa-por-multi-city-not-std.csv
-rw-r--r--  1 user staff 2.2K Jan 10 15:54 results/optd-qa-por-multi-city-not-std.csv
-rw-r--r--  1 user staff 6.1K Jan 10 15:54 results/optd-qa-por-multi-city.csv
$ popd
```

### OPTD vs IATA
* [That script](http://github.com/opentraveldata/quality-assurance/blob/master/checkers/check-por-cmp-optd-it.py)
  compares the
  [OPTD-referenced POR having a UN/LOCODE code](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_unlc.csv)
  with the
  [ones referenced by IATA](http://github.com/opentraveldata/opentraveldata/blob/master/data/IATA).
  It has to be noted that the Python script first downloads the
  [`iata_airport_list_latest.csv` file](http://github.com/opentraveldata/opentraveldata/blob/master/data/IATA/iata_airport_list_latest.csv),
  which is actually a symbolic link. Then, the Python script downloads
  the actual data file, say for instance
  [`archives/iata_airport_list_20190418.csv`](http://github.com/opentraveldata/opentraveldata/blob/master/data/IATA/archives/iata_airport_list_20190418.csv).
  The script then generates a few CSV files:
  + `results/optd-qa-por-optd-no-it.csv`, exhibiting the POR
    referenced by OPTD but not by IATA
  + `results/optd-qa-por-it-not-optd.csv`, exhibiting the POR
    referenced by IATA but not by OPTD

* Note that if a CSV file has a single row, it is the header. So, it can be
  considered as empty.
```bash
$ pushd ~/dev/geo/opentraveldata-qa
$ pipenv run checkers/check-por-cmp-optd-it.py
$ wc -l results/optd-qa-por-optd-no-it.csv
66 results/optd-qa-por-optd-no-it.csv
$ head -3 results/optd-qa-por-optd-no-it.csv
iata_code^geoname_id^iso31662^country_code^city_code_list^location_type^fclass^fcode^page_rank
AED^5879155^AK^US^AED^CA^P^PPL^
AYE^7257567^MA^US^AYE^CH^P^PPL^
$ wc -l results/optd-qa-por-it-not-optd.csv
3 results/optd-qa-por-it-not-optd.csv
$ head -3 results/optd-qa-por-it-not-optd.csv
iata_code
EWS
VSN
$ popd
```

### OPTD vs UN/LOCODE
* [That script](http://github.com/opentraveldata/quality-assurance/blob/master/checkers/check-por-cmp-optd-unlc.py)
  compares the
  [OPTD-referenced POR having a UN/LOCODE code](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_unlc.csv)
  with the
  [ones referenced by UN/LOCODE](http://github.com/opentraveldata/opentraveldata/blob/master/data/unlocode).
  It generates two CSV files:
  + `results/optd-qa-por-optd-not-in-unlc.csv`, exhibiting the POR
    referenced by OPTD but not by UN/LOCODE
  + `iresults/optd-qa-por-unlc-not-in-optd.csv`, exhibiting the POR
    referenced by UN/LOCODE but not by OPTD

* Note that if a CSV file has a single row, it is the header. So, it can be
  considered as empty.
```bash
$ pushd ~/dev/geo/opentraveldata-qa
$ pipenv run checkers/check-por-cmp-optd-unlc.py
$ wc -l results/optd-qa-por-unlc-not-in-optd.csv
10349 results/optd-qa-por-unlc-not-in-optd.csv
$ ls -lFh results/optd-qa-por-*unlc*.csv
-rw-r--r-- 1 user staff 4.7M Dec 13 18:22 results/optd-qa-por-optd-not-in-unlc.csv
-rw-r--r-- 1 user staff 763K Dec 13 18:22 results/optd-qa-por-unlc-not-in-optd.csv
$ popd
```

* In order to get the IATA-referenced POR out of UN/LOCODE-referenced ones:
```bash
$ pushd ~/dev/geo/opentraveldata-qa
$ awk -F'^' '{if ($2 != "") {print $0}}' results/optd-qa-por-unlc-not-in-optd.csv | wc -l
21
$ popd
```

## Airlines

### Airport Bases / Hubs
* [That script](http://github.com/opentraveldata/quality-assurance/blob/master/checkers/check-airline-bases.py)
  checks, for every airline of the
  [`optd_airlines.csv` file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv),
  that the airport bases/hubs are appearing in the
  [`optd_airline_por_rcld.csv` file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por_rcld.csv).

* Note that both files
  ([`optd_airlines.csv`](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv)
  and [`optd_airline_por_rcld.csv`](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por_rcld.csv))
  will be downloaded from the
  [OpenTravelData project](http://github.com/opentraveldata/opentraveldata)
  and stored within the `to_be_checked` directory. If those files are too old,
  they should be removed (a newer version will then be automatically downloaded
  and stored again).

* Note that a CSV file has a single row, it is the header. So, it can be
  considered as empty.

* The following script displays all the missing airport bases/hubs:
```bash
$ pushd ~/dev/geo/opentraveldata-qa
$ ./mkLocalDir.sh
$ pipenv run python checkers/check-airline-bases.py
$ wc -l results/optd-qa-airline-bases-not-in-flight-legs.csv
22 results/optd-qa-airline-bases-not-in-flight-legs.csv
$ head -3 results/optd-qa-airline-bases-not-in-flight-legs.csv
airline_3char_code^airline_2char_code^airline_name^base_iata_code
ABG^RL^Royal Flight^VKO
RUN^9T^MyCargo Airlines^IST
$ popd
```

If the script does not return anything, then the check (successfully) passes.

### Airline networks
* [That script](http://github.com/opentraveldata/quality-assurance/blob/master/checkers/check-airline-networks.py)
  performs, for every airline of the
  [`optd_airlines.csv` file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv),
  some basic statistics on their network, modelled as graph (where
  POR are nodes and flight segments/legs are edges):
```bash
$ pushd ~/dev/geo/opentraveldata-qa
$ pipenv run checkers/check-airline-networks.py
$ wc -l results/optd-qa-airline-network-far-nodes.csv
7 results/optd-qa-airline-network-far-nodes.csv
$ ls -lFh results/optd-qa-airline-*.csv
-rw-r--r--  1 user  staff   8.8K Dec 13 18:47 results/optd-qa-airline-network-far-nodes.csv
-rw-r--r--  1 user  staff    34B Dec 13 18:47 results/optd-qa-airline-network-zero-distance.csv
-rw-r--r--  1 user  staff    87B Dec 13 18:47 results/optd-qa-airline-network-zero-edges.csv
-rw-r--r--  1 user  staff    70B Dec 13 18:47 results/optd-qa-airline-por-not-in-optd.csv
-rw-r--r--  1 user  staff   136B Dec 13 18:47 results/optd-qa-airline-zero-coord-por-in-optd.csv
$ cut -d'^' -f1,1 results/optd-qa-airline-network-far-nodes.csv | grep -v "^airline"
9W
B5
KD
NS
P2
X3
$ cat results/optd-qa-airline-network-zero-edges.csv | grep -v "^airline"
BY^MAN^MAN^1.0
MT^BHX^BHX^1.0
ZB^LBA^LBA^1.0
$ popd
```

### Airline appearing in schedules but not in OPTD
* [That script](http://github.com/opentraveldata/quality-assurance/blob/master/checkers/check-airline-sched-in-optd.py)
  checks, for every airline appearing in the
  [`optd_airline_por_rcld.csv` file](http://github.com/opentraveldata/opentraveldata/blob/master/optd_airline_por_rcld.csv),
  whether they are also referenced by OpenTravelData (OPTD) in the
  [`optd_airlines.csv` file](http://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv):
```bash
$ pushd ~/dev/geo/opentraveldata-qa
$ pipenv run check-airline-sched-in-optd.py
$ wc -l results/optd-qa-airline-schd-not-in-optd.csv
28 results/optd-qa-airline-schd-not-in-optd.csv
$ head -3 results/optd-qa-airline-schd-not-in-optd.csv
airline_code
9Y
AJA
$ popd
```


