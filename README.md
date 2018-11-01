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
$ ./check-airline-bases.py
```

If the script does not return anything, then the check (successfully) passes.


