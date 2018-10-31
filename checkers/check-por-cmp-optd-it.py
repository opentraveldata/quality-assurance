#!/usr/bin/env python3

import csv, datetime
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) airline-related CSV files\nand check that the reference POR are present in the OPTD POR file"
  verboseFlag = dq.handle_opt(usageStr)

  # OPTD-maintained list of POR
  optd_por_public_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_public.csv'

  # OPTD-maintained list of (POR, city)-related known issues
  # for different sources (eg, reference, IATA, OAG, Innovata)
  optd_por_exc_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_exceptions.csv?raw=true'
  optd_por_exc_file = 'to_be_checked/optd_por_exceptions.csv'

  # OPTD-maintained list of state-related known issues
  # for different sources (eg, reference, IATA, OAG, Innovata)
  optd_state_exc_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_state_exceptions.csv?raw=true'
  optd_state_exc_file = 'to_be_checked/optd_state_exceptions.csv'

  # IATA derived list of POR
  optd_por_it_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/data/IATA/iata_airport_list_latest.csv?raw=true'
  optd_por_it_file = 'to_be_checked/iata_airport_list_latest.csv'

  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_por_exc_url, optd_por_exc_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_por_it_url, optd_por_it_file, verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_public_file)
    dq.displayFileHead (optd_por_exc_file)
    dq.displayFileHead (optd_por_it_file)

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
      actv_in_src = row['actv_in_src']

      #
      if not por_code in por_exc_dict and env_id == "" and "I" in exc_src:
        # Register the exception details for the POR
        por_exc_dict[por_code] = {'city_code': cty_code, 'source': exc_src,
                                  'actv_in_optd': actv_in_optd,
                                  'actv_in_src': actv_in_src,
                                  'used': False}

  # State-related known errors, by various sources
  state_exc_dict = dict()
  with open (optd_state_exc_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    # ctry_code^state_code^geo_id^source^env_id^date_from^date_to^wrong_state_code^comment
    for row in file_reader:
      state_pk = row['pk']
      state_code = row['state_code']
      geo_id = row['geo_id']
      wrong_state_code = row['wrong_state_code']
      exc_src = row['source']
      env_id = row['env_id']

      #
      if not state_pk in state_exc_dict and env_id == "" and "I" in exc_src:
        # Register the exception details for the POR
        state_exc_dict[state_pk] = {'pk': state_pk, 'state_code': state_code,
                                    'geo_id': geo_id,
                                    'wrong_state_code': wrong_state_code,
                                    'source': exc_src,
                                    'used': False}

  # OPTD-maintained POR with the full details
  optd_por_dict = dict()
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
      optd_state_code = row['state_code']
      city_code_list_str = row['city_code_list']
      #tvl_code_list_str = row['tvl_por_list']

      #
      if not por_code in optd_por_dict or optd_por_dict[por_code]['env_id'] != '':
        # Register the OPTD details for the POR
        optd_por_dict[por_code] = {'por_code': por_code,
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
                                   'cty_list': city_code_list_str}

  # IATA derived list of POR
  it_por_dict = dict()
  with open (optd_por_it_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      it_por_code = row['por_code']
      #it_por_name = row['por_name']
      it_loc_type = row['loc_type']
      it_state_code = row['state_code']
      it_ctry_code = row['country_code']
      it_cty_code = row['city_code']
      #it_cty_name = row['city_name']
      #it_tz_code = row['tz_code']
      #it_loc_id = row['loc_id']

      # Check whether the POR is known to be an exception
      # for the reference ("I") source
      it_por_exc = False
      if it_por_code in por_exc_dict:
        if "I" in por_exc_dict[it_por_code]['source'] and por_exc_dict[it_por_code]['actv_in_optd'] == "0" and por_exc_dict[it_por_code]['actv_in_src'] == "1":
          it_por_exc = True

          # Remove the record from the known errors, as it has been handled
          por_exc_dict[it_por_code]['used'] = True

      # Check whether the IATA derived POR is in the list of OPTD POR
      if not it_por_code in optd_por_dict and not it_cty_code in optd_por_dict and not it_por_exc:
        # The OPTD POR cannot be found in the list of IATA derived POR,
        # and it is not a known exception
        reasonStr = "IATA derived POR not in OpenTravelData"
        reportStruct = {'por_code': it_por_code, 'in_optd': 0, 'in_iata': 1,
                        'reason': reasonStr}
        print (str(reportStruct))

      elif not it_por_exc:
        # Still not a known exception, but the IATA POR is known by OPTD,
        # either as a travel-related POR or as a city POR:
        # if it_por_code in optd_por_dict or it_cty_code in optd_por_dict

        it_code = it_por_code
        if it_por_code in optd_por_dict:
          # First, register the IATA derived POR, so that we can then,
          # in the next main loop, search for OPTD POR not referenced by IATA
          it_por_dict[it_por_code] = {'loc_type': it_loc_type,
                                      'state_code': it_state_code,
                                      'country_code': it_ctry_code,
                                      'city_code': it_cty_code}
        if it_cty_code in optd_por_dict:
          # If the city code is different from the travel related code,
          # and that city code is still not known from OPTD, register it
          it_por_dict[it_cty_code] = {'loc_type': "C",
                                      'state_code': it_state_code,
                                      'country_code': it_ctry_code,
                                      'city_code': it_cty_code}
          # Only the IATA city code is known by OPTD
          if not it_por_code in optd_por_dict:
            it_code = it_cty_code

        # The OPTD POR is in the list of IATA derived POR,
        # and it is not a known exception: retrieve the details from OPTD
        optd_por_details = optd_por_dict[it_code]

        optd_env_id = optd_por_details['env_id']
        optd_date_from = optd_por_details['date_from']
        optd_date_until = optd_por_details['date_until']
        optd_state_code = optd_por_details['state_code']
        optd_ctry_code = optd_por_details['ctry_code']
        optd_cty_list_str = optd_por_details['cty_list']
        optd_loc_type = optd_por_details['loc_type']
        optd_geo_id = optd_por_details['geo_id']
        optd_feat_class = optd_por_details['feat_class']
        optd_feat_code = optd_por_details['feat_code']
        optd_page_rank = optd_por_details['page_rank']

        if optd_env_id != '' and it_ctry_code != optd_ctry_code:
          # The OPTD POR is no longer valid, whereas still active
          # in the list of IATA derived POR
          reasonStr = "IATA derived POR no longer valid in OpenTravelData"
          reportStruct = {'por_code': it_por_code, 'in_optd': 1, 'in_iata': 1,
                          'env_id': optd_env_id,
                          'date_from': optd_date_from,
                          'date_until': optd_date_until,
                          'it_state_code': it_state_code,
                          'it_ctry_code': it_ctry_code,
                          'it_cty_code': it_cty_code,
                          'it_loc_type': it_loc_type,
                          'optd_geo_id': optd_geo_id,
                          'optd_state_code': optd_state_code,
                          'optd_ctry_code': optd_ctry_code,
                          'optd_cty_list': optd_cty_list_str,
                          'optd_loc_type': optd_loc_type,
                          'optd_feat_class': optd_feat_class,
                          'optd_feat_code': optd_feat_code,
                          'optd_page_rank': optd_page_rank,
                          'reason': reasonStr}
          print (str(reportStruct))

        if optd_env_id == '' and not it_por_code in optd_por_dict:
          # Only the IATA city code is known by OPTD
          reasonStr = "IATA derived POR in OpenTravelData as a city, but not as travel-related POR"
          reportStruct = {'por_code': it_por_code, 'in_optd': 1, 'in_iata': 1,
                          'env_id': optd_env_id,
                          'date_from': optd_date_from,
                          'date_until': optd_date_until,
                          'it_state_code': it_state_code,
                          'it_ctry_code': it_ctry_code,
                          'it_cty_code': it_cty_code,
                          'it_loc_type': it_loc_type,
                          'optd_geo_id': optd_geo_id,
                          'optd_state_code': optd_state_code,
                          'optd_ctry_code': optd_ctry_code,
                          'optd_cty_list': optd_cty_list_str,
                          'optd_loc_type': optd_loc_type,
                          'optd_feat_class': optd_feat_class,
                          'optd_feat_code': optd_feat_code,
                          'optd_page_rank': optd_page_rank,
                          'reason': reasonStr}
          print (str(reportStruct))

        # ISO 3166-2 state code
        if it_state_code != optd_state_code:
          # The state codes are not the same for the IATA- and OPTD-derived POR
          
          # First, check that there is no known exception
          is_state_exc = False

          # In the optd_state_exceptions.csv
          full_state_code = dq.getFullStateCode (optd_ctry_code, optd_state_code)
          if full_state_code in state_exc_dict:
            state_exc_details = state_exc_dict[full_state_code]
            state_exc_geo_id = state_exc_details['geo_id']
            state_exc_wrong_state_code = state_exc_details['wrong_state_code']
            if it_state_code == state_exc_wrong_state_code:
              is_state_exc = True
              state_exc_dict[full_state_code]['used'] = True

          # In the optd_por_exceptions.csv
          optd_por_exc_state_diff = it_code in por_exc_dict and "I" in por_exc_dict[it_code]['source'] and por_exc_dict[it_code]['actv_in_optd'] == "1" and por_exc_dict[it_code]['actv_in_src'] == "1"
          if optd_por_exc_state_diff:
            is_state_exc = True
            por_exc_dict[it_code]['used'] = True

          #
          if not is_state_exc:
            # No known exception rule applies for that state
            reasonStr = "IATA- and OPTD-derived POR have not the same state codes"
            reportStruct = {'por_code': it_por_code, 'in_optd': 1, 'in_iata': 1,
                            'env_id': optd_env_id,
                            'date_from': optd_date_from,
                            'date_until': optd_date_until,
                            'it_state_code': it_state_code,
                            'it_ctry_code': it_ctry_code,
                            'it_cty_code': it_cty_code,
                            'it_loc_type': it_loc_type,
                            'optd_geo_id': optd_geo_id,
                            'optd_state_code': optd_state_code,
                            'optd_ctry_code': optd_ctry_code,
                            'optd_cty_list': optd_cty_list_str,
                            'optd_loc_type': optd_loc_type,
                            'optd_feat_class': optd_feat_class,
                            'optd_feat_code': optd_feat_code,
                            'optd_page_rank': optd_page_rank,
                            'reason': reasonStr}
            print (str(reportStruct))

      else:
        # The exception rule has been handled; register it
        por_exc_dict[it_por_code]['used'] = True

  # Search for OPTD POR not, or no longer, referenced by IATA
  for optd_por_code in optd_por_dict:
    optd_por_details = optd_por_dict[optd_por_code]
    optd_env_id = optd_por_details['env_id']

    # Check whether there is an exception rule
    optd_por_exc_in_optd_but_not_it = optd_por_code in por_exc_dict and "I" in por_exc_dict[optd_por_code]['source'] and por_exc_dict[optd_por_code]['actv_in_optd'] == "1" and por_exc_dict[optd_por_code]['actv_in_src'] == "0"

    if not optd_por_code in it_por_dict and optd_env_id == "" and not optd_por_exc_in_optd_but_not_it:
      # Retrieve the details from OPTD
      optd_state_code = optd_por_details['state_code']
      optd_ctry_code = optd_por_details['ctry_code']
      optd_cty_list_str = optd_por_details['cty_list']
      optd_loc_type = optd_por_details['loc_type']
      optd_geo_id = optd_por_details['geo_id']
      optd_feat_class = optd_por_details['feat_class']
      optd_feat_code = optd_por_details['feat_code']
      optd_page_rank = optd_por_details['page_rank']

      reasonStr = "OPTD POR not/no longer referenced by IATA"
      reportStruct = {'por_code': optd_por_code, 'in_optd': 1, 'in_iata': 0,
                      'optd_geo_id': optd_geo_id,
                      'optd_state_code': optd_state_code,
                      'optd_ctry_code': optd_ctry_code,
                      'optd_cty_list': optd_cty_list_str,
                      'optd_loc_type': optd_loc_type,
                      'optd_feat_class': optd_feat_class,
                      'optd_feat_code': optd_feat_code,
                      'optd_page_rank': optd_page_rank,
                      'reason': reasonStr}
      print (str(reportStruct))
  
  # Sanity checks
  # All the (POR, city)-related exception rules should have been used
  for por_code_exc in por_exc_dict:
    if not por_exc_dict[por_code_exc]['used'] and por_exc_dict[por_code_exc]['actv_in_src'] == "1":
      reportStruct = {'por_code': por_code_exc,
                      'actv_in_it': por_exc_dict[por_code_exc]['actv_in_src']}
      print ("!!!!! Remaining entry of the file of (POR, city)-related related known exceptions: " + str(reportStruct) + ". Please, remove that from the '" + optd_por_exc_url + "' file.")

  # All the state-related exception rules should have been used
  for state_code_exc in state_exc_dict:
    if not state_exc_dict[state_code_exc]['used']:
      reportStruct = {'full_state_code': state_code_exc,
                      'wrong_state_code': state_exc_dict[state_code_exc]['wrong_state_code']}
      print ("!!!!! Remaining entry of the file of state-related known exceptions: " + str(reportStruct) + ". Please, remove that from the '" + optd_state_exc_url + "' file.")
    

  # DEBUG
  if verboseFlag:
    print ("OPTD POR data full dictionary:\n" + str(optd_por_dict))
