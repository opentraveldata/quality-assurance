#!/usr/bin/env python3

import csv, datetime, re
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) POR-related CSV " \
    "files\nand check that the OPTD best known POR are present in " \
    "the OPTD public POR file"
  verboseFlag = dq.handle_opt(usageStr)

  ##
  # List of known exceptions for single POR being assigned several Geonames ID
  # * 6299466 is the Geonames ID corresponding to Basel/Mulhouse/EuroAirport.
  #   IATA wrongly assigns on one hand BSL and MLH to the airport itself
  #   (named EuroAirport), and on the other hand the same EAP code
  #   to both of the cities. All that does not make sense at whole,
  #   but, as of 2020, almost all of the published flight schedules use
  #   either BSL or MLH to designate the airport, and EAP does not appear
  #   in those schedules. See to_be_checked/optd_airline_por.csv:
  #  - 2A^BSL^QYG^2562
  #  - 3O^BSL^CMN^155
  #  - 3V^MLH^GVA^53
  #  - A5^BSL^CDG^961
  #  - 5^MLH^ORY^932  
  known_dup_geo_list = ['6299466']

  ## Input
  # OPTD-maintained list of POR, master file
  optd_por_bksf_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_best_known_so_far.csv?raw=true'
  optd_por_bksf_file = 'to_be_checked/optd_por_best_known_so_far.csv'

  # OPTD-maintained list of POR, generated file
  optd_por_public_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_public.csv'

  ## Output
  # Points of reference (POR) manually curated (in the file of best known POR)
  # but not in the OPTD public file
  output_por_best_not_in_optd_file = 'results/optd-qa-por-best-not-in-optd.csv'
  optd_por_best_not_in_optd_list = [('iata_code', 'optd_pk', 'loc_type',
                                     'geo_id', 'city_code_list')]

  # Points of reference (POR) having the same (duplicated) Geonames ID
  output_por_dup_geo_id_file = 'results/optd-qa-por-dup-geo-id.csv'
  optd_por_dup_geo_id_hdr = ('iata_code', 'loc_type', 'geo_id')
  optd_por_dup_geo_id_list = []
  
  # Points of reference (POR) having a Geonames ID in the manually curated file
  # (of best known POR), not consistent with the one in the OPTD public file
  output_por_cmp_geo_id_file = 'results/optd-qa-por-cmp-geo-id.csv'
  optd_por_cmp_geo_id_list = [('iata_code', 'optd_pk', 'loc_type', 'geo_id',
                               'page_rank', 'city_code_list')]

  
  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file,
                           verboseFlag)
  dq.downloadFileIfNeeded (optd_por_bksf_url, optd_por_bksf_file, verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_public_file)
    dq.displayFileHead (optd_por_bksf_file)

  # OPTD main reference data file for POR
  # iata_code^icao_code^faa_code^is_geonames^geoname_id^envelope_id^name^asciiname^latitude^longitude^fclass^fcode^page_rank^date_from^date_until^comment^country_code^cc2^country_name^continent_name^adm1_code^adm1_name_utf^adm1_name_ascii^adm2_code^adm2_name_utf^adm2_name_ascii^adm3_code^adm4_code^population^elevation^gtopo30^timezone^gmt_offset^dst_offset^raw_offset^moddate^city_code_list^city_name_list^city_detail_list^tvl_por_list^state_code^location_type^wiki_link^alt_name_section^wac^wac_name^ccy_code^unlc_list^uic_list^geoname_lat^geoname_lon
  optd_por_dict = dict()
  with open (optd_por_public_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      optd_iata_code = row['iata_code']
      optd_loc_type = row['location_type']
      optd_geo_id = int(row['geoname_id'])
      optd_env_id = row['envelope_id']
      optd_coord_lat = row['latitude']
      optd_coord_lon = row['longitude']
      optd_page_rank = row['page_rank']
      optd_ctry_code = row['country_code']
      optd_adm1_code = row['adm1_code']
      city_code_list_str = row['city_code_list']

      # When the POR is no longer active (envelope_id != ''), it is filtered out
      if optd_env_id != '': continue
      
      #
      reportDict = {"iata_code": optd_iata_code,
                    'location_type': optd_loc_type,
                    'geoname_id': optd_geo_id,
                    'envelope_id': optd_env_id,
                    "city_code_list": city_code_list_str,
                    "country_code": optd_ctry_code,
                    "page_rank": optd_page_rank, "adm1_code": optd_adm1_code,
                    "geo_lat": optd_coord_lat, "geo_lon": optd_coord_lon,
                    'notified': False}
      
      # Register the POR details with IATA code as the key
      if not optd_iata_code in optd_por_dict:
        optd_por_dict[optd_iata_code] = dict()

      # Register the OPTD details for the POR
      optd_por_dict[optd_iata_code][optd_loc_type] = reportDict

      # When the POR has no Geonames ID assigned, it is not reported here
      if optd_geo_id == 0: continue

      # Register the POR details with Geonames ID as the key, and/or report
      # when the Geonames ID is duplicated (used by several POR)
      if not optd_geo_id in optd_por_dict:
        optd_por_dict[optd_geo_id] = reportDict
      else:
        if not optd_geo_id in known_dup_geo_list:
          oldReportDict = optd_por_dict[optd_geo_id]
          has_been_notified = oldReportDict['notified']
          if not has_been_notified:
            oldReportDict['notified'] = True
            old_iata_code = oldReportDict['iata_code']
            old_loc_type = oldReportDict['location_type']
            old_geo_id = oldReportDict['geoname_id']
            oldReportStruct = (old_iata_code, old_loc_type, old_geo_id)
            optd_por_dup_geo_id_list.append (oldReportStruct)

          reportStruct = (optd_iata_code, optd_loc_type, optd_geo_id)
          optd_por_dup_geo_id_list.append (reportStruct)        
        
  # OPTD file for best known POR so far
  # pk^iata_code^latitude^longitude^city_code^date_from
  primary_key_re = re.compile ("^([A-Z]{3})-([A-Z]{1,2})-([0-9]{1,15})$")
  with open (optd_por_bksf_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      optd_bksf_pk = row['pk']
      match = primary_key_re.match (optd_bksf_pk)
      optd_bksf_loc_type = match.group (2)
      optd_bksf_geo_id = match.group (3)
      optd_bksf_iata_code = row['iata_code']
      optd_bksf_city_code_list = row['city_code']
      optd_bksf_coord_lat = row['latitude']
      optd_bksf_coord_lon = row['longitude']
      optd_bksf_date_from = row['date_from']

      # Check whether the OPTD best known POR is in the list of OPTD public POR
      if not optd_bksf_geo_id in optd_por_dict:
        # The OPTD POR cannot be found in the list of best known POR

        # Get a few more details in order to report them. As there is
        # an inconsistency between the OPTD public file and the list of
        # best known POR (curated by OPTD), it is possible that
        # the (IATA code, location type) pair cannot be found in the OPTD
        # public file as well. However, there should be at least one record
        # for that IATA code.
        if not optd_bksf_iata_code in optd_por_dict:
          # Report the POR details
          reportStruct = (optd_bksf_iata_code, optd_bksf_pk,
                          optd_bksf_loc_type, optd_bksf_geo_id,
                          optd_bksf_city_code_list)
          optd_por_best_not_in_optd_list.append (reportStruct)

        else:
          optd_por_record_dict = optd_por_dict[optd_bksf_iata_code]
          for optd_por_loc_type, optd_por_record in optd_por_record_dict.items():
            optd_por_page_rank = optd_por_record['page_rank']
            # Report the POR details
            reportStruct = (optd_bksf_iata_code, optd_bksf_pk,
                            optd_bksf_loc_type,
                            optd_bksf_geo_id, optd_por_page_rank,
                            optd_bksf_city_code_list)
            optd_por_cmp_geo_id_list.append (reportStruct)

  ## Write the output lists into CSV files
  # POR in the best known list but not in the OPTD public data file
  with open (output_por_best_not_in_optd_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_por_best_not_in_optd_list:
      file_writer.writerow (record)
  
  ##
  # POR having duplicated Geonames ID
  # Sort by Geonames ID, which are numbers (that is why the header is added
  # only after sorting)
  def sortThird (row): return row[2]
  optd_por_dup_geo_id_list.sort (key = sortThird)
  # Insert the header
  optd_por_dup_geo_id_list.insert (0, optd_por_dup_geo_id_hdr)
  with open (output_por_dup_geo_id_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_por_dup_geo_id_list:
      file_writer.writerow (record)
      
  # POR having a Geonames ID in the list of best known POR inconsistent
  # with the Geonames ID in the OPTD public file
  with open (output_por_cmp_geo_id_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_por_cmp_geo_id_list:
      file_writer.writerow (record)


  # DEBUG
  if verboseFlag:
    print ("OPTD POR data full dictionary:\n" + str(optd_por_dict))
