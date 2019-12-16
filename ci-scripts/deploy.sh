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
echo "Injecting a few host keys into ~/.ssh/known_hosts"
cat >> ~/.ssh/known_hosts << _EOF
www2-int2.transport-search.org ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBDmslzunyRnmtrJSwaP1vGuS+vTFBoodZRY1Ri+VIXR8qBKa4MGNgX5WfwQIEOCsbme4gzJ4BZHFNY8WAwNl500=
www-int2.transport-search.org ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBKuH70tG6Ep2ibfqkZMnhPhXan9uIEXuQXUMdNG7N8ZSTv713tO1moU/nVl/drrN68Z4bLD+Nj49OIhj/9OM/W8=
_EOF
chmod 600 ~/.ssh/known_hosts

#
echo "Content of ~/.ssh/config"
cat ~/.ssh/config
echo "--"

#
echo "Creating ${DATA_DIR} on to qa@tits"
ssh -o StrictHostKeyChecking=no qa@titsc "mkdir -p ${DATA_DIR}"

#
echo "Synchronizing results/ onto qa@titsc..."
time rsync -rav -e "ssh -o StrictHostKeyChecking=no" results qa@titsc:${DATA_DIR}/
echo "... done"

#
echo "Synchronizing results/ onto qa@titsc..."
time rsync -rav -e "ssh -o StrictHostKeyChecking=no" to_be_checked qa@titsc:${DATA_DIR}/
echo "... done"

#
echo "Compressing all the CSV files in results/ on qa@titsc"
time "ssh -o StrictHostKeyChecking=no" qa@titsc "bzip2 ${DATA_DIR}/to_be_checked/*.csv"
echo "... done"


