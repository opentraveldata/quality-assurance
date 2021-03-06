
# Python
PY_EXEC=pipenv run python

# Points of Reference (POR)

## OPTD (Open Travel Data) vs IATA
por_optd_vs_it=results/optd-qa-state-optd-it-diff.csv \
  results/optd-qa-por-optd-no-it.csv \
  results/optd-qa-por-it-not-optd.csv \
  results/optd-qa-por-it-no-valid-in-optd.csv \
  results/optd-qa-por-it-in-optd-as-city-only.csv

## Duplicated IATA codes (not working yet)
por_dup_iata=results/optd-qa-por-dup-iata.csv

## PageRank (PR) values set explicitly to zero (0)
por_zero_pr=results/optd-qa-por-optd-zero-pagerank.csv

## Inconsistency in validity dates and/or envelope ID
por_data_incsty=results/optd-qa-por-date-inconsistency.csv

## Wrong ICAO codes (not made of strictly four letters)
por_wrong_icao=results/optd-qa-por-wrong-icao.csv

## UN/LOCODE 
por_unlc=results/optd-qa-por-unlc-not-in-optd.csv \
  results/optd-qa-por-optd-not-in-unlc.csv

## Geonames vs OPTD (Open Travel Data)
por_geo_in_optd=results/optd-qa-por-best-not-in-geo.csv \
  results/optd-qa-por-best-incst-code.csv \
  results/optd-qa-por-dup-geo-id.csv \
  results/optd-qa-por-cmp-geo-id.csv

## Geonames vs OPTD
por_optd_geo_dist=results/optd-qa-por-optd-geo-diff.csv

## Flight legs vs OPTD
por_sched_vs_optd=results/optd-qa-por-sched-not-in-optd.csv

## Missing geo-location
por_no_geoloc=results/optd-qa-por-optd-no-geocoord.csv

## City
por_city_not_in_optd=results/optd-qa-por-city-not-in-optd.csv
por_multi_city=results/optd-qa-por-multi-city.csv \
  results/optd-qa-por-multi-city-not-std.csv
por_missing_close_city=results/optd-qa-por-big-city-around.csv

# Airlines

## Bases
air_bases=results/optd-qa-airline-bases-not-in-flight-legs.csv

## Networks
air_net=results/optd-qa-airline-network-far-nodes.csv \
  results/optd-qa-airline-network-zero-distance.csv \
  results/optd-qa-airline-network-zero-edges.csv \
  results/optd-qa-airline-por-not-in-optd.csv \
  results/optd-qa-airline-zero-coord-por-in-optd.csv

## Schedules
air_schd_not_optd=results/optd-qa-airline-schd-not-in-optd.csv

# All output CSV
all_por_csv=$(por_optd_vs_it) $(por_zero_pr) $(por_data_incsty) \
 $(por_wrong_icao) $(por_unlc) $(por_geo_in_optd) \
 $(por_optd_geo_dist) $(por_sched_vs_optd) $(por_no_geoloc) \
 $(por_city_not_in_optd) $(por_multi_city) \
 $(por_missing_close_city)
all_air_csv=$(air_bases) $(air_net) $(air_schd_not_optd)
all_csv=$(all_por_csv) $(all_air_csv)

# Main target
checkers: $(all_csv)

# Temporary directories
tmpdirs=to_be_checked results

tmpdir: $(tmpdirs)

$(tmpdirs):
	mkdir -p $(tmpdirs)

# Cleaning
clean: tmpdir
	\rm -f to_be_checked/*.csv $(all_csv)

# Specific targets
$(por_optd_vs_it): tmpdir
	$(PY_EXEC) checkers/check-por-cmp-optd-it.py && \
	wc -l $(por_optd_vs_it) && head -3 $(por_optd_vs_it)

$(por_dup_iata): tmpdir
	$(PY_EXEC) checkers/check-por-duplicate-iata.py && \
	wc -l $(por_dup_iata) && head -3 $(por_dup_iata)

$(por_data_incsty): tmpdir
	$(PY_EXEC) checkers/check-por-date-consistency.py && \
	wc -l $(por_data_incsty) && head -3 $(por_data_incsty)

$(por_wrong_icao): tmpdir
	$(PY_EXEC) checkers/check-por-geo-wrong-icao.py && \
	wc -l $(por_wrong_icao) && head -3 $(por_wrong_icao)

$(por_zero_pr): tmpdir
	$(PY_EXEC) checkers/check-por-optd-zero-pagerank.py && \
	wc -l $(por_zero_pr) && head -3 $(por_zero_pr)

$(por_unlc): tmpdir
	$(PY_EXEC) checkers/check-por-cmp-optd-unlc.py && \
	wc -l $(por_unlc) && head -3 $(por_unlc)

$(por_geo_in_optd): tmpdir
	$(PY_EXEC) checkers/check-por-geo-id-in-optd.py && \
	wc -l $(por_geo_in_optd) && head -3 $(por_geo_in_optd)

$(por_optd_geo_dist): tmpdir
	$(PY_EXEC) checkers/check-por-cmp-optd-geo.py && \
	wc -l $(por_optd_geo_dist) && head -3 $(por_optd_geo_dist)

$(por_sched_vs_optd): tmpdir
	$(PY_EXEC) checkers/check-por-sched-in-optd.py && \
	wc -l $(por_sched_vs_optd) && head -3 $(por_sched_vs_optd)

$(por_no_geoloc): tmpdir
	$(PY_EXEC) checkers/check-por-optd-no-geocoord.py && \
	wc -l $(por_no_geoloc) && head -3 $(por_no_geoloc)

$(por_city_not_in_optd): tmpdir
	$(PY_EXEC) checkers/check-por-city-not-in-optd.py && \
	wc -l $(por_city_not_in_optd) && head -3 $(por_city_not_in_optd)

$(por_multi_city): tmpdir
	$(PY_EXEC) checkers/check-por-multiple-cities.py && \
	wc -l $(por_multi_city) && head -3 $(por_multi_city)

$(por_missing_close_city): tmpdir
	$(PY_EXEC) checkers/check-por-missing-cities.py && \
	wc -l $(por_missing_close_city) && head -3 $(por_missing_close_city)

$(air_bases): tmpdir
	$(PY_EXEC) checkers/check-airline-bases.py && \
	wc -l $(air_bases) && head -3 $(air_bases)

$(air_net): tmpdir
	GDAL_DATA=`$(PY_EXEC) -mpip show fiona|grep "^Location"|cut -d' ' -f2,2`/fiona/gdal_data \
	$(PY_EXEC) checkers/check-airline-networks.py && \
	wc -l $(air_net) && head -3 $(air_net)

$(air_schd_not_optd): tmpdir
	$(PY_EXEC) checkers/check-airline-sched-in-optd.py && \
	wc -l $(air_schd_not_optd) && head -3 $(air_schd_not_optd)

