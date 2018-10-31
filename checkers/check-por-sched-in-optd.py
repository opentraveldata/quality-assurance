#!/usr/bin/env python3

import csv, datetime
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) airline-related CSV files\nand check that the schedule POR are present in the OPTD POR file"
  verboseFlag = dq.handle_opt(usageStr)

  # OPTD-maintained list of POR
  optd_por_public_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_public.csv'

  # List of flight leg frequencies
  optd_airline_por_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por_rcld.csv?raw=true'
  optd_airline_por_file = 'to_be_checked/optd_airline_por_rcld.csv'

  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_airline_por_url, optd_airline_por_file, verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_public_file)
    dq.displayFileHead (optd_airline_por_file)

  #
  optd_por_dict = dict()
  with open (optd_por_public_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      optd_iata_code = row['iata_code']
      optd_icao_code = row['icao_code']
      optd_loc_type = row['location_type']
      optd_geo_id = row['geoname_id']
      optd_env_id = row['envelope_id']
      optd_page_rank = row['page_rank']
      optd_ctry_code = row['country_code']

      # Derive a unique code
      por_code = optd_iata_code
      if (por_code == "ZZZ"): por_code = optd_icao_code
      
      #
      if not por_code in optd_por_dict:
        # Register the OPTD details for the POR
        optd_por_dict[por_code] = (por_code, optd_loc_type, optd_geo_id,
                                   optd_env_id, optd_page_rank, optd_ctry_code)

  #
  # airline_code^apt_org^apt_dst^seats_mtly_avg^freq_mtly_avg
  #
  airline_sched_dict = dict()
  with open (optd_airline_por_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      airline_code = row['airline_code']
      org_code = row['apt_org']
      dst_code = row['apt_dst']
      flt_freq = float(row['freq_mtly_avg'])

      # Check whether the origin POR is in the list of OPTD POR
      if not org_code in optd_por_dict and not org_code in airline_sched_dict:
        # Register the new POR
        airline_sched_dict[org_code] = 1

        # The origin POR cannot be found in the list of OPTD POR
        reportStruct = {'por_code': org_code, 'airline_code': airline_code,
                        'in_optd': 0, 'in_sched': 1}
        print (str(reportStruct))

      # Check whether the destination POR is in the list of OPTD POR
      if not dst_code in optd_por_dict and not dst_code in airline_sched_dict:
        # Register the new POR
        airline_sched_dict[dst_code] = 1

        # The origin POR cannot be found in the list of OPTD POR
        reportStruct = {'por_code': dst_code, 'airline_code': airline_code,
                        'in_optd': 0, 'in_sched': 1}
        print (str(reportStruct))

  # DEBUG
  if verboseFlag:
    print ("OPTD POR data full dictionary:\n" + str(optd_por_dict))
