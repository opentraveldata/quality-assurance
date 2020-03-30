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
  known_dup_geo_list = [6299466, ]

  ## Input
  # OPTD-maintained list of POR, master file
  optd_por_bksf_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_best_known_so_far.csv?raw=true'
  optd_por_bksf_file = 'to_be_checked/optd_por_best_known_so_far.csv'

  # OPTD-maintained list of POR, generated file
  optd_por_public_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_public.csv'

  ## Output
  # Points of reference (POR) manually curated (in the file of best known POR)
  # but not in Geonames (i.e., having zero (0) for Geonames ID)
  output_por_best_not_in_geo_file = 'results/optd-qa-por-best-not-in-geo.csv'
  optd_por_best_not_in_geo_list = [dq.k_optd_std_hdr]

  # Points of reference (POR) manually curated (in the file of best known POR)
  # where the primary key (made of the IATA code, location type and Geonames ID)
  # is not consistent with the IATA code
  output_por_best_incst_code_file = 'results/optd-qa-por-best-incst-code.csv'
  optd_por_best_incst_code_list = [('iata_code', 'optd_pk', 'loc_type',
                                    'geo_id', 'city_code_list')]
  
  # Points of reference (POR) having the same (duplicated) Geonames ID
  output_por_dup_geo_id_file = 'results/optd-qa-por-dup-geo-id.csv'
  optd_por_dup_geo_id_hdr = dq.k_optd_std_hdr
  optd_por_dup_geo_id_list = []
  
  # Points of reference (POR) having a Geonames ID in the manually curated file
  # (of best known POR), not consistent with the one in the OPTD public file
  output_por_cmp_geo_id_file = 'results/optd-qa-por-cmp-geo-id.csv'
  optd_por_cmp_geo_id_list = [dq.k_optd_std_hdr]

  
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
      record_as_list = tuple (row.values())
      optd_iata_code = row['iata_code']
      optd_loc_type = row['location_type']
      optd_geo_id = int(row['geoname_id'])
      optd_pk = f"{optd_iata_code}-{optd_loc_type}-{optd_geo_id}"
      optd_env_id = row['envelope_id']
      optd_page_rank = row['page_rank']
      city_code_list_str = row['city_code_list']

      # When the POR is no longer active (envelope_id != ''), it is filtered out
      if optd_env_id != '': continue
      
      #
      reportDict = {'notified': False,
                    'record_as_list': record_as_list}
      
      # Register the POR details with IATA code as the key
      # Note that there may be several records for a signle IATA code
      if not optd_iata_code in optd_por_dict:
        optd_por_dict[optd_iata_code] = dict()

      # Register the OPTD details for the POR
      optd_record_list = optd_por_dict[optd_iata_code]
      optd_record_list[optd_pk] = reportDict

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
            old_record_as_list = oldReportDict['record_as_list']
            old_record_as_list_for_rpt = \
              dq.addReportingReason (old_record_as_list, reporting_reason = '')
            old_record_as_list_for_rpt = \
              dq.addDistances (old_record_as_list_for_rpt, distance = '')

            optd_por_dup_geo_id_list.append (old_record_as_list_for_rpt)
            
          #
          record_as_list_for_rpt = dq.addReportingReason (record_as_list,
                                                          reporting_reason = '')
          record_as_list_for_rpt = dq.addDistances (record_as_list_for_rpt,
                                                    distance = '')
          optd_por_dup_geo_id_list.append (record_as_list_for_rpt)
        
  # OPTD file for best known POR so far
  # pk^iata_code^latitude^longitude^city_code^date_from
  primary_key_re = re.compile ("^([A-Z]{3})-([A-Z]{1,2})-([0-9]{1,15})$")
  with open (optd_por_bksf_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      optd_bksf_pk = row['pk']
      match = primary_key_re.match (optd_bksf_pk)
      optd_bksf_iata_code_from_pk = match.group (1)
      optd_bksf_loc_type = match.group (2)
      optd_bksf_geo_id_str = match.group (3)
      optd_bksf_geo_id = int(optd_bksf_geo_id_str)
      optd_bksf_iata_code = row['iata_code']
      optd_bksf_city_code_list = row['city_code']

      # Record the POR details
      reportStruct = (optd_bksf_iata_code, optd_bksf_pk,
                      optd_bksf_loc_type, optd_bksf_geo_id,
                      optd_bksf_city_code_list)

      # Check that the IATA code is the same individually and as part
      # of the primary key (made of the code, location type and Geonames ID)
      if optd_bksf_iata_code_from_pk != optd_bksf_iata_code:
        optd_por_best_incst_code_list.append (reportStruct)

      # Check whether the OPTD best known POR is in the list of OPTD public POR.
      #
      # By design, when the Geonames ID is zero (0), that POR is not (yet)
      # known from Geonames (but it is referenced in the list of best known POR).
      # Any POR not (yet) referenced by Geonames is reported here, in the
      # output_por_best_not_in_geo_file file.
      if not optd_bksf_geo_id in optd_por_dict:

        # Report the POR details when the Geonames ID is zero (0).
        # The POR details are retrieved from the main OPTD POR data
        # file (optd_por_public.csv)
        optd_record_list = optd_por_dict[optd_bksf_iata_code]
        if optd_bksf_geo_id == 0 and optd_bksf_pk in optd_record_list:
          optd_por_record = optd_record_list[optd_bksf_pk]
          record_as_list = optd_por_record['record_as_list']
          record_as_list_for_rpt = dq.addReportingReason (record_as_list)
          record_as_list_for_rpt = dq.addDistances (record_as_list_for_rpt,
                                                    distance = '')
          optd_por_best_not_in_geo_list.append (record_as_list_for_rpt)

      else:
        # Points of reference (POR) having a Geonames ID in the manually
        # curated file (of best known POR), but not consistent with the one
        # in the OPTD public file (optd_por_public.csv)
        if optd_bksf_geo_id != 0:
          optd_record_list = optd_por_dict[optd_bksf_iata_code]
          if not optd_bksf_pk in optd_record_list:
            for optd_por_pk, optd_por_record in optd_record_list.items():
              # Report the POR details
              record_as_list = optd_por_record['record_as_list']
              reporting_reason = f"{optd_bksf_pk} not found in optd"
              record_as_list_for_rpt = dq.addReportingReason (record_as_list,
                                                              reporting_reason)
              record_as_list_for_rpt = dq.addDistances (record_as_list_for_rpt,
                                                        distance = '')
              optd_por_cmp_geo_id_list.append (record_as_list_for_rpt)

  ## Write the output lists into CSV files
  # POR in the best known list but not in the OPTD public data file
  with open (output_por_best_not_in_geo_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^', lineterminator='\n')
    for record in optd_por_best_not_in_geo_list:
      file_writer.writerow (record)

  # POR having inconsistency between IATA code and primary key
  with open (output_por_best_incst_code_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^', lineterminator='\n')
    for record in optd_por_best_incst_code_list:
      file_writer.writerow (record)
  
  # POR having duplicated Geonames ID
  # Sort by Geonames ID, which are numbers (that is why the header is added
  # only after sorting)
  def sort5th (row): return row[4]
  optd_por_dup_geo_id_list.sort (key = sort5th)
  # Insert the header
  optd_por_dup_geo_id_list.insert (0, optd_por_dup_geo_id_hdr)
  with open (output_por_dup_geo_id_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^', lineterminator='\n')
    for record in optd_por_dup_geo_id_list:
      file_writer.writerow (record)
      
  # POR having a Geonames ID in the list of best known POR inconsistent
  # with the Geonames ID in the OPTD public file
  with open (output_por_cmp_geo_id_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^', lineterminator='\n')
    for record in optd_por_cmp_geo_id_list:
      file_writer.writerow (record)


  # DEBUG
  if verboseFlag:
    print ("OPTD POR data full dictionary:\n" + str(optd_por_dict))
