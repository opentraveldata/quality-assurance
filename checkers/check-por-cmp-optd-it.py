#!/usr/bin/env python3

import csv, re, datetime
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) POR-related CSV " \
    "files\nand check that the reference POR are present in the OPTD POR file"
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

  # OPTD-maintained list of state-related known issues
  # for different sources (eg, reference, IATA, OAG, Innovata)
  optd_state_exc_url = \
    'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_state_exceptions.csv?raw=true'
  optd_state_exc_file = 'to_be_checked/optd_state_exceptions.csv'

  # IATA derived list of POR
  optd_por_it_base_url = \
    'https://github.com/opentraveldata/opentraveldata/blob/master/data/IATA/'
  optd_por_it_symlink_url = optd_por_it_base_url + \
    'iata_airport_list_latest.csv?raw=true'
  optd_por_it_url = ''
  optd_por_it_symlink_file = 'to_be_checked/iata_airport_list_latest.csv'
  optd_por_it_file = ''

  ## Output
  # No known exception rule applies for that state
  output_state_optd_it_diff_file = 'results/optd-qa-state-optd-it-diff.csv'
  optd_state_optd_it_diff_list = [('por_code', 'in_optd', 'in_iata',
                                   'env_id', 'date_from', 'date_until',
                                   'it_state_code', 'it_ctry_code',
                                   'it_cty_code', 'it_loc_type',
                                   'optd_geo_id', 'optd_state_code',
                                   'optd_city_state_list',
                                   'optd_ctry_code', 'optd_cty_list',
                                   'optd_loc_type', 'optd_feat_class',
                                   'optd_feat_code', 'optd_page_rank')]

  # OPTD points of reference (POR) not referenced by IATA
  output_por_optd_no_it_file = 'results/optd-qa-por-optd-no-it.csv'
  optd_por_optd_no_it_list = [('iata_code', 'geoname_id', 'iso31662',
                               'country_code', 'city_code_list',
                               'location_type', 'fclass', 'fcode', 'page_rank')]

  # IATA POR not referenced by OPTD
  output_por_it_not_optd_file = 'results/optd-qa-por-it-not-optd.csv'
  optd_por_it_not_optd_list = [('iata_code', 'iata_name', 'iata_loc_type',
                                'iata_ctry_code', 'iata_state_code',
                                'it_tz_code', 'it_cty_code', 'it_cty_name')]

  # IATA POR no longer valid in OPTD
  output_por_it_no_valid_in_optd_file = \
    'results/optd-qa-por-it-no-valid-in-optd.csv'
  optd_por_it_no_valid_in_optd_list = [('iata_code', 'envelope_id', 'date_from',
                                        'date_until', 'it_state_code',
                                        'it_country_code', 'it_city_code',
                                        'it_location_type', 'geoname_id',
                                        'iso31662', 'country_code',
                                        'city_code_list', 'location_type',
                                        'fclass', 'fcode', 'page_rank')]

  # IATA derived POR in OpenTravelData as a city, but not as travel-related POR
  output_por_it_in_optd_as_city_only_file = \
    'results/optd-qa-por-it-in-optd-as-city-only.csv'
  optd_por_it_in_optd_as_city_only_list = [('por_code', 'in_optd', 'in_iata',
                                            'env_id', 'date_from', 'date_until',
                                            'it_state_code', 'it_ctry_code',
                                            'it_cty_code', 'it_loc_type',
                                            'optd_geo_id', 'optd_state_code',
                                            'optd_ctry_code', 'optd_cty_list',
                                            'optd_loc_type', 'optd_feat_class',
                                            'optd_feat_code', 'optd_page_rank')]
  
  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file,
                           verboseFlag)
  dq.downloadFileIfNeeded (optd_por_exc_url, optd_por_exc_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_state_exc_url, optd_state_exc_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_por_it_symlink_url, optd_por_it_symlink_file,
                           verboseFlag)

  # For the IATA screen-scraped data, the file is a symbolic link.
  # The actual (pointed to) data file has to be retrieved.
  # Example of content of the symbolic link file:
  # archives/iata_airport_list_20190418.csv
  # The actual data file is then https://github.com/opentraveldata/opentraveldata/blob/master/data/IATA/archives/iata_airport_list_20190418.csv
  it_filepath_re = re.compile ("^archives/(iata_airport_list_[0-9]{8}.csv)$")
  it_filepath = dq.extractFileHeader (optd_por_it_symlink_file)
  optd_por_it_url = optd_por_it_base_url + it_filepath + '?raw=true'
  match = it_filepath_re.match (it_filepath)
  it_filename = match.group (1)
  optd_por_it_file = 'to_be_checked/' + it_filename
  dq.downloadFileIfNeeded (optd_por_it_url, optd_por_it_file, verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_public_file)
    dq.displayFileHead (optd_por_exc_file)
    dq.displayFileHead (optd_state_exc_file)
    dq.displayFileHead (optd_por_it_file)

  #
  # (POR, city)-related known errors, by various sources
  #
  # por_code^source^actv_in_optd^actv_in_src^env_id^date_from^date_to^city_code^state_code^reason_code^comment
  #
  por_exc_dict = dict()
  with open (optd_por_exc_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      por_code = row['por_code']
      cty_code = row['city_code']
      state_code = row['state_code']
      exc_src = row['source']
      env_id = row['env_id']
      actv_in_optd = row['actv_in_optd']
      actv_in_src = row['actv_in_src']

      #
      if not por_code in por_exc_dict and env_id == "" and "I" in exc_src:
        # Register the exception details for the POR
        por_exc_dict[por_code] = {'iata_code': por_code,
                                  'city_code': cty_code,
                                  'state_code': state_code,
                                  'source': exc_src,
                                  'actv_in_optd': actv_in_optd,
                                  'actv_in_src': actv_in_src,
                                  'used': False}

  #
  # State-related known errors, by various sources
  #
  # ctry_code^state_code^geo_id^source^env_id^date_from^date_to^wrong_country_code^wrong_state_code^comment
  #
  state_exc_dict = dict()
  with open (optd_state_exc_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      state_pk = row['pk']
      state_code = row['state_code']
      geo_id = row['geo_id']
      wrong_country_code = row['wrong_country_code']
      wrong_state_code = row['wrong_state_code']
      exc_src = row['source']
      env_id = row['env_id']

      #
      if not state_pk in state_exc_dict and env_id == '' and 'I' in exc_src:
        # Register the exception details for the POR
        state_exc_dict[state_pk] = {'pk': state_pk, 'state_code': state_code,
                                    'geoname_id': geo_id,
                                    'wrong_country_code': wrong_country_code,
                                    'wrong_state_code': wrong_state_code,
                                    'source': exc_src,
                                    'used': False}

  #
  # OPTD-maintained POR with the full details
  #
  optd_por_by_code_dict = dict()
  optd_por_by_geo_dict = dict()
  with open (optd_por_public_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      por_code = row['iata_code']
      optd_por_name = row['name']
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
      optd_ctry_name = row['country_name']
      optd_ctry_code_alt = row['cc2']
      optd_cont_name = row['continent_name']
      optd_adm1_code = row['adm1_code']
      optd_adm1_name_utf = row['adm1_name_utf']
      optd_state_code = row['iso31662']
      city_code_list_str = row['city_code_list']
      city_detail_list_str = row['city_detail_list']
      tvl_code_list_str = row['tvl_por_list']

      # POR record with full details
      optd_record = {'iata_code': por_code,
                     'location_type': optd_loc_type,
                     'geoname_id': optd_geo_id,
                     'name': optd_por_name,
                     'env_id': optd_env_id,
                     'date_from': optd_date_from,
                     'date_until': optd_date_until,
                     'feat_class': optd_feat_class,
                     'feat_code': optd_feat_code,
                     'geo_lat': optd_coord_lat,
                     'geo_lon': optd_coord_lon,
                     'page_rank': optd_page_rank,
                     'country_code': optd_ctry_code,
                     'country_name': optd_ctry_name,
                     'cc2': optd_ctry_code_alt,
                     'adm1_code': optd_adm1_code,
                     'adm1_name_utf': optd_adm1_name_utf,
                     'state_code': optd_state_code,
                     'city_code_list': city_code_list_str,
                     'city_detail_list': city_detail_list_str,
                     'city_state_list': set(),
                     'tvl_por_list': tvl_code_list_str}
      
      # Store the record indexed by IATA code
      if not por_code in optd_por_by_code_dict \
         or optd_por_by_code_dict[por_code]['env_id'] != '':
        # Register the OPTD details for the POR
        optd_por_by_code_dict[por_code] = optd_record
      
      # Store the record indexed by Geonames ID
      if not optd_geo_id in optd_por_by_geo_dict \
         or optd_por_by_geo_dict[optd_geo_id]['env_id'] != '':
        # Register the OPTD details for the POR
        optd_por_by_geo_dict[optd_geo_id] = optd_record

  # Browse the just built POR dictionary, and add the details for cities.
  # There are two independent POR dictionaries (one indexed by IATA code,
  # the other one indexed by Geonames ID). The state of the city has to be
  # added in both dictionaries.
  # The rationale is that some airports (like CBE, CVG, BWI) are located
  # in a given state, while the city their are serving are located in a
  # neighbouring state. And IATA references the state only for the city,
  # whereas the in OPTD, the state (ISO3166-2 code) is given for the POR
  # itself, not the city it is serving.
  # So, here, every POR is added the list of states corresponding to the
  # list of cities it is serving. Then, at a later stage, the IATA state
  # will be compared to the OPTD state (and to the list of its city states).
  for optd_por_code, optd_por_details in optd_por_by_code_dict.items():
    city_detail_list_str = optd_por_details['city_detail_list']
    city_detail_list = city_detail_list_str.split('=')

    for city_detail_str in city_detail_list:
      city_details = city_detail_str.split('|')
      try:
        city_geo_id = city_details[1]
      except:
        print(f"optd_por_code: {optd_por_code}")
        print(f"city_details: {city_details}")
        print(f"city_detail_list: {city_detail_list}")
        print(f"city_detail_list_str: {city_detail_list_str}")
        raise Exception

      if city_geo_id in optd_por_by_geo_dict:
        city_record = optd_por_by_geo_dict[city_geo_id]
        city_state = city_record['state_code']
        city_record['city_state_list'].add (city_state)
        optd_por_details['city_state_list'].add (city_state)
  
  # IATA derived list of POR
  it_por_dict = dict()
  with open (optd_por_it_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      it_por_code = row['por_code']
      it_por_name = row['por_name']
      it_loc_type = row['loc_type']
      it_state_code = row['state_code']
      it_ctry_code = row['country_code']
      it_cty_code = row['city_code']
      it_cty_name = row['city_name']
      it_tz_code = row['tz_code']
      it_loc_id = row['loc_id']

      # Check whether the POR is known to be an exception
      # for the reference ('I') source
      it_por_exc = False
      if it_por_code in por_exc_dict:
        if 'I' in por_exc_dict[it_por_code]['source'] and \
           por_exc_dict[it_por_code]['actv_in_optd'] == '0' and \
           por_exc_dict[it_por_code]['actv_in_src'] == '1':
          it_por_exc = True

          # Remove the record from the known errors, as it has been handled
          por_exc_dict[it_por_code]['used'] = True

      # Check whether the IATA derived POR is in the list of OPTD POR
      if not it_por_code in optd_por_by_code_dict and \
         not it_cty_code in optd_por_by_code_dict and not it_por_exc:
        # The OPTD POR cannot be found in the list of IATA derived POR,
        # and it is not a known exception
        reportStruct = (it_por_code, it_por_name, it_loc_type,
                        it_ctry_code, it_state_code, it_tz_code,
                        it_cty_code, it_cty_name)
        optd_por_it_not_optd_list.append (reportStruct)

      elif not it_por_exc:
        # Still not a known exception, but the IATA POR is known by OPTD,
        # either as a travel-related POR or as a city POR:
        # if it_por_code in optd_por_by_code_dict or it_cty_code in optd_por_by_code_dict

        it_code = it_por_code
        if it_por_code in optd_por_by_code_dict:
          # First, register the IATA derived POR, so that we can then,
          # in the next main loop, search for OPTD POR not referenced by IATA
          it_por_dict[it_por_code] = {'location_type': it_loc_type,
                                      'state_code': it_state_code,
                                      'country_code': it_ctry_code,
                                      'city_code': it_cty_code}
        if it_cty_code in optd_por_by_code_dict:
          # If the city code is different from the travel related code,
          # and that city code is still not known from OPTD, register it
          it_por_dict[it_cty_code] = {'location_type': "C",
                                      'state_code': it_state_code,
                                      'country_code': it_ctry_code,
                                      'city_code': it_cty_code}
          # Only the IATA city code is known by OPTD
          if not it_por_code in optd_por_by_code_dict:
            it_code = it_cty_code

        # The OPTD POR is in the list of IATA derived POR,
        # and it is not a known exception: retrieve the details from OPTD
        optd_por_details = optd_por_by_code_dict[it_code]

        optd_env_id = optd_por_details['env_id']
        optd_date_from = optd_por_details['date_from']
        optd_date_until = optd_por_details['date_until']
        optd_state_code = optd_por_details['state_code']
        optd_ctry_code = optd_por_details['country_code']
        optd_cty_list_str = optd_por_details['city_code_list']
        optd_loc_type = optd_por_details['location_type']
        optd_geo_id = optd_por_details['geoname_id']
        optd_feat_class = optd_por_details['feat_class']
        optd_feat_code = optd_por_details['feat_code']
        optd_page_rank = optd_por_details['page_rank']
        optd_city_state_list = optd_por_details['city_state_list']

        if optd_env_id != '' and it_ctry_code != optd_ctry_code:
          # The OPTD POR is no longer valid, whereas still active
          # in the list of IATA derived POR
          reportStruct = (it_por_code, optd_env_id, optd_date_from,
                          optd_date_until, it_state_code,
                          it_ctry_code, it_cty_code,
                          it_loc_type, optd_geo_id,
                          optd_state_code, optd_ctry_code,
                          optd_cty_list_str, optd_loc_type,
                          optd_feat_class, optd_feat_code, optd_page_rank)
          optd_por_it_no_valid_in_optd_list.append (reportStruct)

        if optd_env_id == '' and not it_por_code in optd_por_by_code_dict:
          # Only the IATA city code is known by OPTD
          reasonStr = "IATA derived POR in OpenTravelData as a city, " \
                      "but not as travel-related POR"
          reportStruct = (it_por_code, 1, 1, optd_env_id,
                          optd_date_from, optd_date_until,
                          it_state_code, it_ctry_code, it_cty_code, it_loc_type,
                          optd_geo_id, optd_state_code,
                          optd_ctry_code, optd_cty_list_str,
                          optd_loc_type, optd_feat_class, optd_feat_code,
                          optd_page_rank)
          optd_por_it_in_optd_as_city_only_list.append (reportStruct)

        # ISO 3166-2 state code
        if it_state_code != optd_state_code \
           and not it_state_code in optd_city_state_list:
          # The state codes are not the same for the IATA- and OPTD-derived POR

          # Check that there is no known exception
          is_state_exc = False

          # Check the optd_state_exceptions.csv file
          # The full state code is formatted as "<ctry_code>-<state_code>",
          # where ctry_code and state_code are the ISO 3166-1 and ISO 3166-2
          # codes respectively
          full_state_code = dq.getFullStateCode (optd_ctry_code, optd_state_code)
          if full_state_code in state_exc_dict:
            state_exc_details = state_exc_dict[full_state_code]
            state_exc_geo_id = state_exc_details['geoname_id']
            state_exc_wrong_country_code= state_exc_details['wrong_country_code']
            state_exc_wrong_state_code = state_exc_details['wrong_state_code']
            if it_state_code == state_exc_wrong_state_code:
              is_state_exc = True
              state_exc_dict[full_state_code]['used'] = True

          # Check the optd_por_exceptions.csv file
          optd_por_exc_state_diff = it_code in por_exc_dict \
            and "I" in por_exc_dict[it_code]['source'] \
            and por_exc_dict[it_code]['actv_in_optd'] == "1" \
            and por_exc_dict[it_code]['actv_in_src'] == "1"
          if optd_por_exc_state_diff:
            is_state_exc = True
            por_exc_dict[it_code]['used'] = True

          #
          if it_state_code != '' and not is_state_exc:
            # No known exception rule applies for that state
            optd_city_state_list_str = '|'.join (optd_city_state_list)
            reportStruct = (it_por_code, 1, 1, optd_env_id, optd_date_from,
                            optd_date_until, it_state_code, it_ctry_code,
                            it_cty_code, it_loc_type, optd_geo_id,
                            optd_state_code, optd_city_state_list_str,
                            optd_ctry_code, optd_cty_list_str,
                            optd_loc_type, optd_feat_class, optd_feat_code,
                            optd_page_rank)
            optd_state_optd_it_diff_list.append (reportStruct)

      else:
        # The exception rule has been handled; register it
        por_exc_dict[it_por_code]['used'] = True

  # Search for OPTD POR not, or no longer, referenced by IATA
  for optd_por_code, optd_por_details in optd_por_by_code_dict.items():
    optd_env_id = optd_por_details['env_id']

    # Check whether there is an exception rule
    optd_por_exc_in_optd_but_not_it = optd_por_code in por_exc_dict \
      and "I" in por_exc_dict[optd_por_code]['source'] \
      and por_exc_dict[optd_por_code]['actv_in_optd'] == "1" \
      and por_exc_dict[optd_por_code]['actv_in_src'] == "0"

    if not optd_por_code in it_por_dict and optd_env_id == "" \
       and not optd_por_exc_in_optd_but_not_it:
      # Retrieve the details from OPTD
      optd_state_code = optd_por_details['state_code']
      optd_ctry_code = optd_por_details['country_code']
      optd_cty_list_str = optd_por_details['city_code_list']
      optd_loc_type = optd_por_details['location_type']
      optd_geo_id = optd_por_details['geoname_id']
      optd_feat_class = optd_por_details['feat_class']
      optd_feat_code = optd_por_details['feat_code']
      optd_page_rank = optd_por_details['page_rank']

      reportStruct = (optd_por_code, optd_geo_id, optd_state_code,
                      optd_ctry_code, optd_cty_list_str, optd_loc_type,
                      optd_feat_class, optd_feat_code, optd_page_rank)
      optd_por_optd_no_it_list.append (reportStruct)
  
  # Sanity checks
  # All the (POR, city)-related exception rules should have been used
  for por_code_exc in por_exc_dict:
    if not por_exc_dict[por_code_exc]['used'] \
       and por_exc_dict[por_code_exc]['actv_in_src'] == "1":
      reportStruct = {'por_code': por_code_exc,
                      'actv_in_it': por_exc_dict[por_code_exc]['actv_in_src']}
      print ("!!!!! Remaining entry of the file of (POR, city)-related " \
             "known exceptions: " + str(reportStruct) + \
             ". Please, remove that from the '" + optd_por_exc_url + "' file.")

  # All the state-related exception rules should have been used
  for state_code_exc in state_exc_dict:
    if not state_exc_dict[state_code_exc]['used']:
      reportStruct = {'full_state_code': state_code_exc,
                      'wrong_state_code': state_exc_dict[state_code_exc]['wrong_state_code']}
      print ("!!!!! Remaining entry of the file of state-related known " \
             "exceptions: " + str(reportStruct) + \
             ". Please, remove that from the '" + optd_state_exc_url + "' file.")
    

  ## Write the output lists into CSV files
  # IATA and OPTD have different state codes
  with open (output_state_optd_it_diff_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_state_optd_it_diff_list:
      file_writer.writerow (record)

  # OPTD points of reference (POR) not referenced by IATA
  with open (output_por_optd_no_it_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_por_optd_no_it_list:
      file_writer.writerow (record)

  # IATA POR not referenced by OPTD
  with open (output_por_it_not_optd_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_por_it_not_optd_list:
      file_writer.writerow (record)

  # IATA POR no longer valid in OPTD
  with open (output_por_it_no_valid_in_optd_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_por_it_no_valid_in_optd_list:
      file_writer.writerow (record)

  # IATA POR in OPTD only as city
  with open (output_por_it_in_optd_as_city_only_file, 'w',
             newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_por_it_in_optd_as_city_only_list:
      file_writer.writerow (record)
      
  # DEBUG
  if verboseFlag:
    print ("OPTD POR data full dictionary:\n" + str(optd_por_by_code_dict))
