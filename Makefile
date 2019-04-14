
# Points of Reference (POR)

# UN/LOCODE 
por_unlc_csv=results/optd-qa-por-unlc-not-in-optd.csv results/optd-qa-por-optd-not-in-unlc.csv

# Geonames in OPTD (Open Travel Data)
por_geo_in_optd=results/optd-qa-por-best-not-in-optd.csv results/optd-qa-por-cmp-geo-id.csv

# City
por_city_not_in_optd=results/optd-qa-por-city-not-in-optd.csv
por_multi_city=results/optd-qa-por-multi-city.csv results/optd-qa-por-multi-city-not-std.csv

# Airlines
air_net=results/optd-qa-airline-network-far-nodes.csv


# Main target
checkers: $(por_unlc_csv) $(por_geo_in_optd) $(por_city_not_in_optd) $(por_multi_city) \
	$(air_net)

# Specific targets
$(por_unlc_csv):
	python checkers/check-por-cmp-optd-unlc.py && wc -l $(por_unlc_csv) && head -3 $(por_unlc_csv)

$(por_geo_in_optd):
	python checkers/check-por-geo-id-in-optd.py && wc -l $(por_geo_in_optd) && head -3 $(por_geo_in_optd)

$(por_city_not_in_optd):
	python checkers/check-por-city-not-in-optd.py && wc -l $(por_city_not_in_optd) && head -3 $(por_city_not_in_optd)

$(por_multi_city):
	python checkers/check-por-multiple-cities.py && wc -l $(por_multi_city) && head -3 $(por_multi_city)

$(air_net):
	pipenv run python checkers/check-airline-networks.py && wc -l $(air_net) && head -3 $(air_net)


