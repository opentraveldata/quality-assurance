#!/usr/bin/env python3

import csv, datetime, re
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) POR-related CSV " \
    "files\nand reports POR with wrong ICAO codes (not made of strictly " \
    "four letters)"
  verboseFlag = dq.handle_opt(usageStr)

  ## Input
  # OPTD-maintained list of POR having wrong ICAO codes, generated file
  optd_por_wrong_icao_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_wrong_icao.csv?raw=true'
  optd_por_wrong_icao_file = 'to_be_checked/optd_por_wrong_icao.csv'

  ## Output
  # Copy of the input file
  output_por_wrong_icao_file = 'results/optd-qa-por-wrong-icao.csv'
  optd_por_wrong_icao_list = [dq.k_optd_std_hdr]
  
  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_wrong_icao_url, optd_por_wrong_icao_file,
                           verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_wrong_icao_file)

  # OPTD main reference data file for POR
  # iata_code^icao_code^faa_code^is_geonames^geoname_id^envelope_id^name^asciiname^latitude^longitude^fclass^fcode^page_rank^date_from^date_until^comment^country_code^cc2^country_name^continent_name^adm1_code^adm1_name_utf^adm1_name_ascii^adm2_code^adm2_name_utf^adm2_name_ascii^adm3_code^adm4_code^population^elevation^gtopo30^timezone^gmt_offset^dst_offset^raw_offset^moddate^city_code_list^city_name_list^city_detail_list^tvl_por_list^state_code^location_type^wiki_link^alt_name_section^wac^wac_name^ccy_code^unlc_list^uic_list^geoname_lat^geoname_lon
  with open (optd_por_wrong_icao_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      reportStruct = tuple (row.values())
      # DEBUG
      #print (f"Record: {reportStruct}")
      
      # Register the OPTD details for the POR
      optd_por_wrong_icao_list.append (reportStruct)

  ## Write the output lists into CSV files
  # POR having wrong ICAO codes (not made of strictly four letters)
  with open (output_por_wrong_icao_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_por_wrong_icao_list:
      file_writer.writerow (record)

