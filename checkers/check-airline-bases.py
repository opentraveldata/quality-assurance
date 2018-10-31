#!/usr/bin/env python3

import csv, datetime
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) airline-related CSV files\nand check that the airport bases/hubs are present in the list of flight legs"
  verboseFlag = dq.handle_opt(usageStr)

  # Airline details
  optd_airline_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv?raw=true'
  optd_airline_file = 'to_be_checked/optd_airlines.csv'

  # List of flight leg frequencies
  optd_airline_por_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por_rcld.csv?raw=true'
  optd_airline_por_file = 'to_be_checked/optd_airline_por_rcld.csv'

  # OPTD-maintained list of POR, generated file
  optd_por_public_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_public.csv'

  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_airline_url, optd_airline_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_airline_por_url, optd_airline_por_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file, verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_airline_file)
    dq.displayFileHead (optd_airline_por_file)
    dq.displayFileHead (optd_por_public_file)

  #
  # Screen-scraped flight schedules
  # airline_code^apt_org^apt_dst^flt_freq
  #
  # Build, for every airline, the list of POR they serve
  #
  airline_por_dict = dict()
  with open (optd_airline_por_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      airline_code = row['airline_code']
      apt_org = row['apt_org']
      apt_dst = row['apt_dst']
      flt_freq = float(row['freq_mtly_avg'])

      # Register or update the dictionary for that airline code
      if airline_code in airline_por_dict:
        airline_por_list = airline_por_dict[airline_code]

        # Register the flight frequency for the origin airport
        if not apt_org in airline_por_list:
          airline_por_list[apt_org] = flt_freq
        else:
          cumulated_flt_freq = airline_por_list[apt_org]
          airline_por_list[apt_org] = cumulated_flt_freq + flt_freq

        # Register the flight frequency for the destination airport
        if not apt_dst in airline_por_list:
          airline_por_list[apt_dst] = flt_freq
        else:
          cumulated_flt_freq = int(airline_por_list[apt_dst])
          airline_por_list[apt_dst] = cumulated_flt_freq + flt_freq

      else:
        # Register the flight frequencies for the origin and destination airports
        airline_por_list = dict()
        airline_por_list[apt_org] = flt_freq
        airline_por_list[apt_dst] = flt_freq
        airline_por_dict[airline_code] = airline_por_list


  #
  # OpenTravelData-maintained list of POR
  # iata_code^icao_code^faa_code^is_geonames^geoname_id^envelope_id^name^asciiname^latitude^longitude^fclass^fcode^page_rank^date_from^date_until^comment^country_code^cc2^country_name^continent_name^adm1_code^adm1_name_utf^adm1_name_ascii^adm2_code^adm2_name_utf^adm2_name_ascii^adm3_code^adm4_code^population^elevation^gtopo30^timezone^gmt_offset^dst_offset^raw_offset^moddate^city_code_list^city_name_list^city_detail_list^tvl_por_list^state_code^location_type^wiki_link^alt_name_section^wac^wac_name
  #
  optd_por_dict = dict()
  with open (optd_por_public_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      optd_iata_code = row['iata_code']
      #optd_loc_type = row['location_type']
      #optd_geo_id = row['geoname_id']
      #optd_env_id = row['envelope_id']
      #optd_coord_lat = row['latitude']
      #optd_coord_lon = row['longitude']
      #optd_page_rank = row['page_rank']
      optd_ctry_code = row['country_code']
      optd_cont_name = row['continent_name']
      #optd_adm1_code = row['adm1_code']
      #city_code_list_str = row['city_code_list']

      #
      if not optd_iata_code in optd_por_dict:
        # Register the OPTD details for the POR
        optd_por_dict[optd_iata_code] = (optd_ctry_code, optd_cont_name)

  #
  # OpenTravelData-maintained list of airlines
  # pk^env_id^validity_from^validity_to^3char_code^2char_code^num_code^name^name2^alliance_code^alliance_status^type^wiki_link^flt_freq^alt_names^bases^key^version
  #
  airline_dict = dict()
  with open (optd_airline_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      #pk = row['pk']
      airline_code = row['2char_code']
      icao_code = row['3char_code']
      if icao_code == "": icao_code = "ZZZZ"
      env_id = row['env_id']
      airline_name = row['name']
      base_list_str = row['bases']

      # Keep only the airlines appearing in flight schedules
      if airline_code in airline_por_dict:
        airline_por_list = airline_por_dict[airline_code]

        # Register the airline, if active and not already registered
        if not airline_code in airline_dict and env_id == '':
          airline_dict[airline_code] = dict()
          airline_dict[airline_code]['bases_in_sched'] = False

        # Register the airport hubs/bases (only for active airlines)
        if env_id == '':
          base_list = base_list_str.split('=')
          # print (airline_code + ": " + base_list_str + " (" + str(base_list) + ")")
          airline_dict[airline_code][icao_code] = {'bases': base_list,
                                                   'name': airline_name}

  # Browse the airlines
  # By construction, those are active airlines appearing in flight schedules
  for iata_code in airline_dict:
    airline_por_list = airline_por_dict[iata_code]

    reportStruct = dict()
    for icao_code in airline_dict[iata_code]:
      if icao_code == 'bases_in_sched':
        continue
      por_details = airline_dict[iata_code][icao_code]
      base_list = por_details['bases']
      name = por_details['name']

      # Check whether the airport bases/hubs appear in the file of POR list
      if base_list:
        for base in base_list:

          if base in airline_por_list:
            # The base for an airline, having the current IATA code,
            # appears in flight schedules
            airline_dict[iata_code]['bases_in_sched'] = True

          else:
            # Register a few details to report later
            if base and not icao_code in reportStruct:
              reportStruct[icao_code] = {'base': base, 'airline_name': name}
            
    # If none of the airlines having that IATA code
    # have bases appearing in flight schedules, report them
    if airline_dict[iata_code]['bases_in_sched'] == False and len(reportStruct):
      reportStruct['iata_code'] = iata_code
      print (str(reportStruct))

    
  # DEBUG
  if verboseFlag:
    print ("Airline full dictionary:\n" + str(airline_dict))
    print ("Airline POR full dictionary:\n" + str(airline_por_dict))
