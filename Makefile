por_unlc_csv=results/optd-qa-por-unlc-not-in-optd.csv results/optd-qa-por-optd-not-in-unlc.csv

checkers: $(por_unlc_csv)

$(por_unlc_csv):
	python checkers/check-por-cmp-optd-unlc.py && wc -l $(por_unlc_csv) && head -3 $(por_unlc_csv)

