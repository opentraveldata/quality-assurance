#!/usr/bin/env python3

import csv, datetime, re
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) POR-related CSV " \
    "files\nand check that the validity dates are consistent"
  verboseFlag = dq.handle_opt(usageStr)

  ## Input
  # OPTD-maintained list of POR, generated file
  optd_por_public_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_public.csv'

  ## Output
  # Points of reference (POR) having a consistency issue with respect to (wrt)
  # the validity dates, for instance the envelope ID is non empty but there
  # is no validity period end date, or vice versa, or the dates themselves
  # are not in the valid format/not parsable
  k_exp_format = '%Y-%m-%d'
  output_por_date_inconsistency_file = 'results/optd-qa-por-date-inconsistency.csv'
  optd_por_date_inconsistency_list = [('iata_code', 'loc_type', 'geo_id',
                                       'env_id', 'date_from', 'date_until',
                                       'reason')]

  
  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file,
                           verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_public_file)

  # OPTD main reference data file for POR
  # iata_code^icao_code^faa_code^is_geonames^geoname_id^envelope_id^name^asciiname^latitude^longitude^fclass^fcode^page_rank^date_from^date_until^comment^country_code^cc2^country_name^continent_name^adm1_code^adm1_name_utf^adm1_name_ascii^adm2_code^adm2_name_utf^adm2_name_ascii^adm3_code^adm4_code^population^elevation^gtopo30^timezone^gmt_offset^dst_offset^raw_offset^moddate^city_code_list^city_name_list^city_detail_list^tvl_por_list^state_code^location_type^wiki_link^alt_name_section^wac^wac_name^ccy_code^unlc_list^uic_list^geoname_lat^geoname_lon
  with open (optd_por_public_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      iata_code = row['iata_code']
      loc_type = row['location_type']
      geo_id = int(row['geoname_id'])
      env_id = row['envelope_id']
      date_from_str = row['date_from']
      date_from = None
      date_until_str = row['date_until']
      date_until = None
      reason_str = ''

      # 1. At least one of the validity period dates is not in a valid format.
      #    The valid date format is expected to be YYYY-MM-DD
      try:
        
        if date_from_str != '':
          date_from = datetime.datetime.strptime (date_from_str, k_exp_format)
          
        if date_until_str != '':
          date_until = datetime.datetime.strptime (date_until_str, k_exp_format)
        
      except ValueError as err:
        reason_str = 'date-not-valid'
        reportStruct = (iata_code, loc_type, geo_id, env_id,
                        date_from_str, date_until_str, reason_str)
        optd_por_date_inconsistency_list.append (reportStruct)
      
      # 2. The envelope ID is non empty (i.e., the POR is no longer valid
      #    wrt IATA assignment), but the validity period end date is not set
      if env_id != '' and not date_until:
        reason_str = 'not-valid-but-no-end-date'
        reportStruct = (iata_code, loc_type, geo_id, env_id,
                        date_from_str, date_until_str, reason_str)
        optd_por_date_inconsistency_list.append (reportStruct)
        
      # 3. The envelope ID is empty (i.e., the POR is still valid wrt IATA
      #    assignment), but the validity period end date is set
      if date_until and env_id == '':
        reason_str = 'valid-but-end-date-set'
        reportStruct = (iata_code, loc_type, geo_id, env_id,
                        date_from_str, date_until_str, reason_str)
        optd_por_date_inconsistency_list.append (reportStruct)

      # 4. The start date is not the older than the end date
      if date_from and date_until and date_from > date_until:
        reason_str = 'validity-dates-not-sorted'
        reportStruct = (iata_code, loc_type, geo_id, env_id,
                        date_from_str, date_until_str, reason_str)
        optd_por_date_inconsistency_list.append (reportStruct)
        
        
  ## Write the output lists into CSV files
  # POR in the best known list but not in the OPTD public data file
  with open (output_por_date_inconsistency_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_por_date_inconsistency_list:
      file_writer.writerow (record)
  
