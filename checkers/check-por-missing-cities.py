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

  # OPTD-maintained list of (POR, city)-related known issues
  # for different sources (eg, reference, IATA, OAG, Innovata)
  optd_por_exc_url = \
    'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_exceptions.csv?raw=true'
  optd_por_exc_file = 'to_be_checked/optd_por_exceptions.csv'

  ## Output
  # There is a big city, which is close enough geographically
  output_big_city_around_file = 'results/optd-qa-por-big-city-around.csv'
  optd_big_city_around_list = [('por_code', 'por_page_rank',
                                'por_feat_code', 'por_geo_id,',
                                'city_code', 'city_page_rank',
                                'city_code_list', 'distance')]

  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file,
                           verboseFlag)
  dq.downloadFileIfNeeded (optd_por_exc_url, optd_por_exc_file, verboseFlag)

  # DEBUG
  if verboseFlag:
      dq.displayFileHead (optd_por_public_file)
      dq.displayFileHead (optd_por_exc_file)

  # (POR, city)-related known errors, by various sources
  por_exc_dict = dict()
  with open (optd_por_exc_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
        por_code = row['por_code']
        cty_code = row['city_code']
        exc_src = row['source']
        env_id = row['env_id']
        actv_in_optd = row['actv_in_optd']
        reason_code = row['reason_code']

        # Store the record when it corresponds to a close-city exception rule
        # (reason_code is "CC"), for a POR still active in OPTD (source is "O"
        # and env_id is empty)
        if not por_code in por_exc_dict \
           and env_id == "" and exc_src == "O" and actv_in_optd == "1" \
           and reason_code == "CC":
            # Register the exception details for the POR
            por_exc_dict[por_code] = {'por_code': por_code,
                                      'city_code': cty_code,
                                      'source': exc_src,
                                      'actv_in_optd': actv_in_optd,
                                      'env_id': env_id,
                                      'reason_code': reason_code,
                                      'used': False}

  # OPTD-maintained POR with the full details
  optd_por_dict = dict()
  optd_por_geo_dict = dict()
  with open (optd_por_public_file, newline='') as csvfile:
      file_reader = csv.DictReader (csvfile, delimiter='^')
      for row in file_reader:
          por_code = row['iata_code']
          #optd_por_name = row['name']
          optd_loc_type = row['location_type']
          optd_geo_id = row['geoname_id']
          optd_env_id = row['envelope_id']
          optd_date_from = row['date_from']
          optd_date_until = row['date_until']
          optd_feat_class = row['fclass']
          optd_feat_code = row['fcode']
          optd_coord_lat = row['latitude']
          optd_coord_lon = row['longitude']
          optd_page_rank = row['page_rank']
          optd_ctry_code = row['country_code']
          #optd_ctry_name = row['country_name']
          #optd_ctry_code_alt = row['cc2']
          #optd_cont_name = row['continent_name']
          optd_adm1_code = row['adm1_code']
          #optd_adm1_name = row['adm1_name_utf']
          optd_state_code = row['iso31662']
          city_code_list_str = row['city_code_list']
          city_detail_list_str = row['city_detail_list']
          #tvl_code_list_str = row['tvl_por_list']

          # Only the transport-/travel-related POR are stored here,
          # as opposed to the pure city-typed POR.
          # By design, the transport-/travel-related POR are unique, ie,
          #
          # there can only be a single POR corresponding to a given IATA code
          # and being travel-/transport-related.
          #
          # On the other hand, many cities may be assigned the same IATA code.
          #
          if optd_loc_type != 'C' \
             and not por_code in optd_por_dict \
             and optd_env_id == '':
              # Extract the list of IATA codes of the cities.
              # Example of city code list for PAE: PAE,SEA
              # For PAE: city_code_list = ['PAE', 'SEA']
              city_code_list = [v for v in city_code_list_str.split(',')]
          
              # Extract the list of Geonames ID of the cities
              # Example of city detail list for RDU:
              # RDU|4464368|Durham|Durham=RDU|4487042|Raleigh|Raleigh
              # The following list comprehension extracts the Geonames ID.
              # For RDU, it gives: city_geoid_list = ['4464368', '4487042']
              city_geoid_list = []
              try:
                  city_geoid_list = [geoid[1] for geoid in \
                                     (v.split('|') for v in \
                                      city_detail_list_str.split('='))]
              except:
                  print ("Error - the city list string associateed to " \
                         "{}/{} has an issue: {}".format (por_code,
                                                          optd_geo_id,
                                                          city_detail_list_str))
          
              # Register the OPTD details for the POR
              optd_por_dict[por_code] = {
                  'por_code': por_code,
                  'loc_type': optd_loc_type,
                  'geo_id': optd_geo_id,
                  'env_id': optd_env_id,
                  'date_from': optd_date_from,
                  'date_until': optd_date_until,
                  'feat_class': optd_feat_class,
                  'feat_code': optd_feat_code,
                  'geo_lat': optd_coord_lat,
                  'geo_lon': optd_coord_lon,
                  'page_rank': optd_page_rank,
                  'ctry_code': optd_ctry_code,
                  'adm1_code': optd_adm1_code,
                  'state_code': optd_state_code,
                  'city_code_list': city_code_list,
                  'city_geoid_list': city_geoid_list,
                  'city_detail_list': city_detail_list_str
              }

          # Record the details for the cities
          if optd_loc_type == 'C' \
             and not optd_geo_id in optd_por_geo_dict \
             and optd_env_id == '':

              # Register the OPTD details for the POR
              optd_por_geo_dict[optd_geo_id] = {
                  'por_code': por_code,
                  'loc_type': optd_loc_type,
                  'geo_id': optd_geo_id,
                  'env_id': optd_env_id,
                  'date_from': optd_date_from,
                  'date_until': optd_date_until,
                  'feat_class': optd_feat_class,
                  'feat_code': optd_feat_code,
                  'geo_lat': optd_coord_lat,
                  'geo_lon': optd_coord_lon,
                  'page_rank': optd_page_rank,
                  'ctry_code': optd_ctry_code,
                  'adm1_code': optd_adm1_code,
                  'state_code': optd_state_code
              }
              
  # OPTD POR list, but with less details. Neobase is used here for its
  # find_near() piece of functionality.
  # Note that, as of end 2019, Neobase ships with a bundled snapshot version
  # of the OPTD POR data file, which may be different from the latest version
  # this checker script retrieves above in the downloadFileIfNeeded() function.
  # When https://github.com/alexprengere/neobase/issues/1 will be solved,
  # Neobase should then be required to update the OPTD POR data file.
  #
  N = neobase.NeoBase()

  for key in N:
      N.set (key, city_codes = set (N.get (key, "city_code_list")))

  for key in sorted(N):
      if "A" not in N.get (key, "location_type"):
          continue
        
      # to speed things up, but this could be removed
      if N.get (key, "page_rank") is None:
          continue

      city_codes = N.get (key, "city_codes")
      for dist, other in N.find_near (key, radius=60):
          if "C" not in N.get(other, "location_type"):
              continue
          if N.get(other, "iata_code") in city_codes:
              continue
          if N.get(other, "page_rank") is None:
              continue
          if N.get(other, "page_rank") <= N.get(key, "page_rank") * 100:
              continue

          # Neobase part
          por_code = N.get (key, "iata_code")
          por_page_rank = N.get (key, "page_rank")
          city_code = N.get (other, "iata_code")
          city_page_rank = N.get (other, "page_rank")
          por_city_code_list = city_codes
          por_city_code_list_str = ','.join (por_city_code_list)
          por_city_dist = dist

          # OPTD part (would become redundant/obsolete if integrated within
          # Neobase at some point; see
          # https://github.com/alexprengere/neobase/issues/2 for the status)
          optd_por = optd_por_dict[por_code]
          optd_feat_code = optd_por['feat_code']
          optd_geoid = optd_por['geo_id']

          # Check whether the POR is known to be an exception
          # for the OPTD ("O") source, with reason_code "CC" (close city)
          # and where the close big city is stated. Example of rule:
          # por_code^source^actv_in_optd^...^city_code^reason_code^comment
          # CCB^O^1^1^..^LAX^CC^comment
          # That rule states that this Python script reports CCB as potentially
          # also serving LAX, but this reporting should be dismissed (see the
          # comment part of that exception rule to understand why)
          it_por_exc = False
          if por_code in por_exc_dict:

              optd_city_code = por_exc_dict[por_code]['city_code']
              if optd_city_code == city_code:
                  it_por_exc = True

                  # Remove the record from the known errors,
                  # as it has been handled
                  por_exc_dict[por_code]['used'] = True

          # When the POR corresponds to an exception, we do not report it
          if it_por_exc:
              continue
              
          # When the POR is an air base, it is normal that it does not "serve"
          # a big city. The (so far only) example of that situation is
          # ADW, corresponding to the Joint Base Andrews, Maryland (MD), USA.
          # IATA associates ADW to Camp Springs. This Python script detects
          # that the city of WAS/Washington D.C., DC, USA, is close to ADW.
          # But it seems reasonable to consider that WAS, as a city, not be
          # served by ADW, the air base.
          if optd_feat_code == "AIRB":
              continue
          
          # Add the record for later reporting
          reportStruct = (por_code, por_page_rank,
                          optd_feat_code, optd_geoid,
                          city_code, city_page_rank,
                          por_city_code_list_str, por_city_dist)
          optd_big_city_around_list.append (reportStruct)

  # Sanity checks
  # All the (POR, city)-related exception rules should have been used
  for por_code_exc in por_exc_dict:
      if not por_exc_dict[por_code_exc]['used']:
          reportStruct = {'por_code': por_code_exc,
                          'source': por_exc_dict[por_code_exc]['source']}
          print ("!!!!! Remaining entry of the file of (POR, city)-related " \
                 "known exceptions: " + str(reportStruct) + \
                 ". Please, remove that from the '" + optd_por_exc_url \
                 + "' file.")
          
  ## Write the output lists into CSV files
  # IATA and OPTD have different state codes
  with open (output_big_city_around_file, 'w', newline ='') as csvfile:
      file_writer = csv.writer (csvfile, delimiter='^')
      for record in optd_big_city_around_list:
          file_writer.writerow (record)

  # DEBUG
  if verboseFlag:
      print ("OPTD POR data full dictionary:\n" + str(optd_por_dict))
      
