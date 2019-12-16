#!/bin/bash

#
echo "DATA_DIR_BASE=${DATA_DIR_BASE}"

if [ "${DATA_DIR_BASE}" == "" ]
then
	export DATA_DIR_BASE="/var/www/data/optd/qa"
fi

#
export TODAY_DATE="$(date +%Y-%m-%d)"
export DATA_DIR="${DATA_DIR_BASE}/${TODAY_DATE}"

#
echo "TODAY_DATE=${TODAY_DATE} - DATA_DIR=${DATA_DIR}"

#
echo "Creating ${DATA_DIR} on to qa@tits"
ssh qa@titsc "mkdir -p ${DATA_DIR}"

#
echo "Synchronizing results/ onto qa@titsc..."
time rsync -rav -e ssh results qa@titsc:${DATA_DIR}/
echo "... done"

#
echo "Synchronizing results/ onto qa@titsc..."
time rsync -rav -e ssh to_be_checked qa@titsc:${DATA_DIR}/
echo "... done"

#
echo "Compressing all the CSV files in results/ on qa@titsc"
time ssh qa@titsc "bzip2 ${DATA_DIR}/to_be_checked/*.csv"
echo "... done"

