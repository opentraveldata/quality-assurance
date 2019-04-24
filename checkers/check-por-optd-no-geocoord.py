#!/usr/bin/env python3

import csv, json, re
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) POR-related CSV file\nand reports POR with no geo-location"
  verboseFlag = dq.handle_opt(usageStr)

  ## Input
  # OPTD-maintained list of POR, generated file
  optd_por_public_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_public.csv'

  ## Output
  # OPTD points of reference (POR) with no geo-location
  output_por_optd_no_geocoord_file = 'results/optd-qa-por-optd-no-geocoord.csv'
  optd_por_no_geocoord_list = [('iata_code', 'geo_id', 'loc_type')]
  
  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file,
                           verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_public_file)

  # OPTD main reference data file for POR
  # iata_code^icao_code^faa_code^is_geonames^geoname_id^envelope_id^name^asciiname^latitude^longitude^fclass^fcode^page_rank^date_from^date_until^comment^country_code^cc2^country_name^continent_name^adm1_code^adm1_name_utf^adm1_name_ascii^adm2_code^adm2_name_utf^adm2_name_ascii^adm3_code^adm4_code^population^elevation^gtopo30^timezone^gmt_offset^dst_offset^raw_offset^moddate^city_code_list^city_name_list^city_detail_list^tvl_por_list^state_code^location_type^wiki_link^alt_name_section^wac^wac_name^ccy_code^unlc_list^uic_list
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

      # Keep only the active record
      if optd_env_id:
          continue
      
      # Report if missing geo-coordinates (latitude and/or longitude)
      if not optd_coord_lat or not optd_coord_lon:
        reportStruct = (optd_iata_code, optd_geo_id, optd_loc_type)
        optd_por_no_geocoord_list.append (reportStruct)
          
  ## Write the output lists into CSV files
  # OPTD points of reference (POR) with no geo-location
  with open (output_por_optd_no_geocoord_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_por_no_geocoord_list:
      file_writer.writerow (record)
     
