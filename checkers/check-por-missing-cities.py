#!/usr/bin/env python3

# Inspired by Alex Prengere's script:
#  https://gist.github.com/alexprengere/c54d706d659653049863355b8bb2ac3b
# Discussed on https://github.com/opentraveldata/opentraveldata/issues/133
#

import csv, re, datetime, neobase
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
    #
  usageStr= "That script downloads OpenTravelData (OPTD) POR-related CSV files" \
      "\nand check that the transport-/travel-related POR are associated " \
      "\nto big cities which are geographically close"
  verboseFlag = dq.handle_opt(usageStr)

  ## Input
  # OPTD-maintained list of POR
  optd_por_public_url = \
      'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_public.csv'

  ## Output
  # There is a big city, which is close enough geographically
  output_big_city_around_file = 'results/optd-qa-por-big-city-around.csv'
  optd_big_city_around_list = [('por_code', 'por_page_rank',
                                'city_code', 'city_page_rank',
                                'city_code_list', 'distance')]

  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file,
                           verboseFlag)

  # DEBUG
  if verboseFlag:
      dq.displayFileHead (optd_por_public_file)

  #
  N = neobase.NeoBase()

  for key in N:
      N.set(key, city_codes=set(N.get(key, "city_code_list")))

  for key in sorted(N):
      if "A" not in N.get(key, "location_type"):
          continue
        
      # to speed things up, but this could be removed
      if N.get(key, "page_rank") is None:
          continue
      city_codes = N.get(key, "city_codes")
      for dist, other in N.find_near(key, radius=60):
          if "C" not in N.get(other, "location_type"):
              continue
          if N.get(other, "iata_code") in city_codes:
              continue
          if N.get(other, "page_rank") is None:
              continue
          if N.get(other, "page_rank") <= N.get(key, "page_rank") * 100:
              continue

          por_code = N.get (key, "iata_code")
          por_page_rank = N.get (key, "page_rank")
          city_code = N.get(other, "iata_code")
          city_page_rank = N.get(other, "page_rank")
          por_city_code_list = list (city_codes)
          por_city_dist = dist
            
          # Add the record for later reporting
          reportStruct = (por_code, por_page_rank, city_code, city_page_rank,
                          por_city_code_list, por_city_dist)
          optd_big_city_around_list.append (reportStruct)
            
  ## Write the output lists into CSV files
  # IATA and OPTD have different state codes
  with open (output_big_city_around_file, 'w', newline ='') as csvfile:
      file_writer = csv.writer (csvfile, delimiter='^')
      for record in optd_big_city_around_list:
          file_writer.writerow (record)

  # DEBUG
  if verboseFlag:
      print ("OPTD POR data full dictionary:\n" + str(optd_por_dict))
      
