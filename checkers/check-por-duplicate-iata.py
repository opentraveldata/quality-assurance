#!/usr/bin/env python3

#
# Work In Progress
#
# Currently, that checker reports the POR sharing IATA codes.
# But since most the IATA codes are associated to at least two POR,
# namely one for the city and one for a transport-/travel-related point
# serving that city, almost all the POR are reported.
#
# Rather, overlaps in the validity periods should be reported only,
# independently of the number of POR an IATA code is assigned at a given
# point in time.
#

import csv, datetime
import DeliveryQuality as dq
from itertools import tee


#
def pairwise(iterable):
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

#
def check_overlap(l):
    for (s1, e1), (s2, e2) in pairwise(l):
        if e1 > s2: return True
    return False

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) POR-related CSV " \
      "files\nand check whether there are OPTD POR with duplicated IATA codes"
  verboseFlag = dq.handle_opt(usageStr)

  ## Input
  # OPTD-maintained list of POR
  optd_por_public_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_public.csv'

  ## Output
  # Points of reference (POR) for which duplicated IATA codes has been detected
  output_por_dup_iata_file = 'results/optd-qa-por-dup-iata.csv'
  optd_por_dup_iata_list = [('iata_code', 'loc_type', 'geo_id',
                             'env_id', 'date_from', 'date_until',
                             'ctry_code', 'adm1_code', 'page_rank')]

  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file,
                           verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_public_file)

  #
  optd_por_validperiod_dict = dict()
  optd_por_dict = dict()

  # Browse the OPTD POR (points of reference)
  with open (optd_por_public_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
        optd_por_iata = row['iata_code']
        optd_por_icao = row['icao_code']
        optd_date_from = "1900-01-01"
        if row['date_from'] != "": optd_date_from = row['date_from']
        optd_date_until = "2999-12-31"
        if row['date_until'] != "": optd_date_until = row['date_until']
        optd_geo_id = row['geoname_id']
        optd_env_id = row['envelope_id']
        optd_coord_lat = row['latitude']
        optd_coord_lon = row['longitude']
        optd_page_rank = row['page_rank']
        optd_ctry_code = row['country_code']
        optd_adm1_code = row['adm1_code']
        optd_loc_type = row['location_type']

        reportStruct = {'iata_code': optd_por_iata,
                        'icao_code': optd_por_icao,
                        'location_type': optd_loc_type,
                        'geoname_id': optd_geo_id,
                        'envelope_id': optd_env_id,
                        'date_from': optd_date_from,
                        'date_until': optd_date_until,
                        'country_code': optd_ctry_code,
                        'adm1_code': optd_adm1_code,
                        'page_rank': optd_page_rank}

        # Register the OPTD details for the POR
        if not optd_por_iata in optd_por_dict:
          optd_por_dict[optd_por_iata] = reportStruct

        #
        if not optd_por_iata in optd_por_validperiod_dict:
            optd_por_validperiod_dict[optd_por_iata] = []
          
        # The POR should be an airport (why not adding 'R', 'B', 'H' and 'P')
        validity_period = (optd_date_from, optd_date_until)
        optd_por_validperiod_dict[optd_por_iata].append (validity_period)
        
  # Filter those with more than one entry and sort by start and end dates
  optd_por_validperiod_sted_dict = \
      {k: sorted(v) for k, v in optd_por_validperiod_dict.items() if len(v) > 1}

  # Get those with an overlap
  optd_por_validperiod_fltd_dict = \
      {k: v for k, v in optd_por_validperiod_sted_dict.items() \
       if check_overlap(v)}

  # Browse the POR with duplicated IATA codes
  for optd_por_iata, optd_por_struct in optd_por_validperiod_fltd_dict.items():
      # Retrieve the full details from the OPTD POR dictionary
      optd_por_struct = optd_por_dict[optd_por_iata]
      optd_loc_type = optd_por_struct['location_type']
      optd_geo_id = optd_por_struct['geoname_id']
      optd_env_id = optd_por_struct['envelope_id']
      optd_date_from = optd_por_struct['date_from']
      optd_date_until = optd_por_struct['date_until']
      optd_ctry_code = optd_por_struct['country_code']
      optd_adm1_code = optd_por_struct['adm1_code']
      optd_page_rank = optd_por_struct['page_rank']

      # Report the record
      reportStruct = (optd_por_iata, optd_loc_type, optd_geo_id,
                      optd_env_id, optd_date_from, optd_date_until,
                      optd_ctry_code, optd_adm1_code, optd_page_rank)
      optd_por_dup_iata_list.append (reportStruct)

  ## Write the output lists into CSV files
  # POR in the best known list but not in the OPTD public data file
  with open (output_por_dup_iata_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_por_dup_iata_list:
      file_writer.writerow (record)
  
