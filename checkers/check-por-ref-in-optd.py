#!/usr/bin/env python3

import csv, datetime
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) airline-related CSV files\nand check that the reference POR are present in the OPTD POR file"
  verboseFlag = dq.handle_opt(usageStr)

  # OPTD-maintained list of POR
  optd_por_public_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_best_known_so_far.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_best_known_so_far.csv'

  # POR reference data
  optd_por_ref_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_ref.csv?raw=true'
  optd_por_ref_file = 'to_be_checked/optd_por_ref.csv'
  optd_por_ref_exc_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_exceptions.csv?raw=true'
  optd_por_ref_exc_file = 'to_be_checked/optd_por_exceptions.csv'

  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_por_ref_url, optd_por_ref_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_por_ref_exc_url, optd_por_ref_exc_file, verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_public_file)
    dq.displayFileHead (optd_por_ref_file)
    dq.displayFileHead (optd_por_ref_exc_file)

  #
  optd_por_dict = dict()
  with open (optd_por_public_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      por_code = row['iata_code']
      #optd_loc_type = row['location_type']
      #optd_geo_id = row['geoname_id']
      #optd_env_id = row['envelope_id']
      optd_coord_lat = row['latitude']
      optd_coord_lon = row['longitude']
      #optd_page_rank = row['page_rank']
      #optd_ctry_code = row['country_code']
      #optd_adm1_code = row['adm1_code']
      city_code_list_str = row['city_code']

      #
      if not por_code in optd_por_dict:
        # Register the OPTD details for the POR
        optd_por_dict[por_code] = (por_code, city_code_list_str,
                                   optd_coord_lat, optd_coord_lon)

  #
  ref_por_exc_dict = dict()
  with open (optd_por_ref_exc_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      ref_por_exc_code = row['por_code']
      ref_por_exc_src = row['source']
      ref_por_exc_env_id = row['env_id']
      ref_por_exc_actv_in_optd = row['actv_in_optd']

      #
      if not ref_por_exc_code in ref_por_exc_dict and 'R' in ref_por_exc_src and ref_por_exc_env_id == '' and ref_por_exc_actv_in_optd == '0':
        # Register the execption rule for the POR
        ref_por_exc_dict[ref_por_exc_code] = (ref_por_exc_code)

  #
  with open (optd_por_ref_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      ref_por_code = row['iata_code']
      ref_cty_code = row['cty_code']
      ref_ctry_code = row['ctry_code']
      ref_state_code = row['state_code']
      ref_coord_lat = row['lat']
      ref_coord_lon = row['lon']

      # Check whether the reference POR is in the list of OPTD POR
      if not ref_por_code in optd_por_dict and not ref_por_code in ref_por_exc_dict:
        # The OPTD POR cannot be found in the list of reference POR
        reportStruct = {'por_code': ref_por_code, 'in_optd': 0, 'in_ref': 1}
        print (str(reportStruct))

      else:
        # From the reference data
        optd_por_tuple = optd_por_dict[por_code]

  # DEBUG
  if verboseFlag:
    print ("OPTD POR data full dictionary:\n" + str(optd_por_dict))
