#!/usr/bin/env python3

import csv, datetime
import DeliveryQuality as dq


# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) airline-related CSV files\nand check that the state is specified for all the OPTD POR\nin a few selected countries"
  verboseFlag = dq.handle_opt(usageStr)

  # OPTD-maintained list of POR
  optd_por_public_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_public.csv'

  # OPTD-maintained list of country states
  optd_country_states_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_country_states.csv?raw=true'
  optd_country_states_file = 'to_be_checked/optd_country_states.csv'
  

  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_country_states_url, optd_country_states_file,
                        verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_public_file)
    dq.displayFileHead (optd_country_states_file)


  # List of countries for which a state should be specified
  optd_states_dict = dict()
  with open (optd_country_states_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      ctry_code = row['ctry_code']
      adm1_code = row['adm1_code']
      state_code = row['abbr']
      if not ctry_code in optd_states_dict:
        optd_states_dict[ctry_code] = (adm1_code, state_code)

  #
  # iata_code^icao_code^faa_code^is_geonames^geoname_id^envelope_id^name^asciiname^latitude^longitude^fclass^fcode^page_rank^date_from^date_until^comment^country_code^cc2^country_name^continent_name^adm1_code^adm1_name_utf^adm1_name_ascii^adm2_code^adm2_name_utf^adm2_name_ascii^adm3_code^adm4_code^population^elevation^gtopo30^timezone^gmt_offset^dst_offset^raw_offset^moddate^city_code_list^city_name_list^city_detail_list^tvl_por_list^state_code^location_type^wiki_link^alt_name_section^wac^wac_name
  with open (optd_por_public_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      optd_iata_code = row['iata_code']
      optd_loc_type = row['location_type']
      optd_geo_id = row['geoname_id']
      optd_env_id = row['envelope_id']
      optd_coord_lat = row['latitude']
      optd_coord_lon = row['longitude']
      optd_page_rank = row['page_rank']
      optd_ctry_code = row['country_code']
      optd_adm1_code = row['adm1_code']
      city_code_list_str = row['city_code_list']

      optd_state_code = row['state_code']

      # Check whether there should be a state for that country
      is_adm1_specified = 1
      if (optd_adm1_code == ""): is_adm1_specified = 0
      is_state_specified = 1
      if (optd_state_code == ""): is_state_specified = 0
      if optd_ctry_code in optd_states_dict and (optd_geo_id != "0") and (not is_state_specified or not is_adm1_specified):
        # The state (or administrative level 1) is not specified
        reportStruct = {'iata_code': optd_iata_code, 'geo_id': optd_geo_id,
                        'country_code': optd_ctry_code, 'adm1_code': optd_adm1_code,
                        'state_code': optd_state_code, 'page_rank': optd_page_rank}
        print (str(reportStruct))


  # DEBUG
  if verboseFlag:
    print ("OPTD states full dictionary:\n" + str(optd_states_dict))
