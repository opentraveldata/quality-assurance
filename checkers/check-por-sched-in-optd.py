#!/usr/bin/env python3

import csv, datetime
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) airline-related CSV " \
    "files\nand check that the schedule POR are present in the OPTD POR file"
  verboseFlag = dq.handle_opt(usageStr)

  ## Input
  # OPTD-maintained list of POR
  optd_por_public_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_public.csv'

  # List of flight leg frequencies
  k_w_seats = False
  optd_airline_por_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por.csv?raw=true'
  optd_airline_por_file = 'to_be_checked/optd_airline_por.csv'
  if k_w_seats:
    optd_airline_por_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por_rcld.csv?raw=true'
    optd_airline_por_file = 'to_be_checked/optd_airline_por_rcld.csv'

  ## Output
  # No known exception rule applies for that state
  output_state_optd_it_diff_file = 'results/optd-qa-por-sched-not-in-optd.csv'
  por_sched_not_in_optd_list = [('airline_code', 'nonoptd_por_code',
                                 'org_code', 'dst_code', 'flt_freq')]

  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file,
                           verboseFlag)
  dq.downloadFileIfNeeded (optd_airline_por_url, optd_airline_por_file,
                           verboseFlag)

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

  # Without seats (optd_airline_por.csv):
  # airline_code^apt_org^apt_dst^flt_freq
  #
  # With seats (optd_airline_por_rcld.csv):
  # airline_code^apt_org^apt_dst^seats_mtly_avg^freq_mtly_avg
  #
  por_reported_dict = dict()
  with open (optd_airline_por_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      airline_code = row['airline_code']
      org_code = row['apt_org']
      dst_code = row['apt_dst']
      flt_freq = 0
      if k_w_seats:
        flt_freq = float(row['freq_mtly_avg'])
      else:
        flt_freq = int(row['flt_freq'])

      # Check whether the origin POR is in the list of OPTD POR.
      # If the POR is not in OPTD, check whether it has already been reported.
      if not org_code in optd_por_dict and not org_code in por_reported_dict:
        # Register the new POR
        por_reported_dict[org_code] = True

        # The origin POR cannot be found in the list of OPTD POR
        reportStruct = (airline_code, org_code, org_code, dst_code, flt_freq)
        por_sched_not_in_optd_list.append (reportStruct)

      # Check whether the destination POR is in the list of OPTD POR
      if not dst_code in optd_por_dict and not dst_code in por_reported_dict:
        # Register the new POR
        por_reported_dict[dst_code] = 1

        # The destination POR cannot be found in the list of OPTD POR
        reportStruct = (airline_code, dst_code, org_code, dst_code, flt_freq)
        por_sched_not_in_optd_list.append (reportStruct)

  ## Write the output lists into CSV files
  # IATA and OPTD have different state codes
  with open (output_state_optd_it_diff_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in por_sched_not_in_optd_list:
      file_writer.writerow (record)

        
  # DEBUG
  if verboseFlag:
    print ("OPTD POR data full dictionary:\n" + str(optd_por_dict))
