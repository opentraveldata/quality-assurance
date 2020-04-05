#!/usr/bin/env python3

import csv, datetime
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) airline-related CSV files\nand check that the UN/LOCODE POR are present in Geonames (and in the OPTD POR file)"
  verboseFlag = dq.handle_opt(usageStr)

  ## Input
  # OPTD-maintained list of UN/LOCODE-referenced POR
  optd_por_extd_unlc_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_unlc.csv?raw=true'
  optd_por_extd_unlc_file = 'to_be_checked/optd_por_unlc.csv'

  # UN/LOCODE derived list of POR
  optd_por_unlc_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/data/unlocode/archives/unlocode-code-list-2018-1.csv?raw=true'
  optd_por_unlc_file = 'to_be_checked/unlocode-code-list-latest.csv'

  ## Output
  # UN/LOCODE points of reference (POR) not referenced by OPTD
  output_por_unlc_not_in_optd_file = 'results/optd-qa-por-unlc-not-in-optd.csv'
  por_unlc_not_in_optd_list = [('por_code', 'unlc_iata_code', 'unlc_ctry_code',
                                'unlc_state_code', 'unlc_short_code',
                                'unlc_name_utf8', 'unlc_name_ascii',
                                'unlc_coord_lat', 'unlc_coord_lon',
                                'unlc_change_code', 'unlc_status',
                                'unlc_is_port', 'unlc_is_rail', 'unlc_is_road',
                                'unlc_is_apt', 'unlc_is_postoff',
                                'unlc_is_icd', 'unlc_is_fxtpt',
                                'unlc_is_brdxing', 'unlc_is_unkwn')]
  
  # OPTD points of reference (POR) not referenced by UN/LOCODE
  output_por_optd_not_in_unlc_file = 'results/optd-qa-por-optd-not-in-unlc.csv'
  por_optd_not_in_unlc_list = [('unlc_code', 'geo_id', 'fclass', 'fcode',
                                'geo_lat', 'geo_lon', 'iso31662_code',
                                'iso31662_name')]

  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_extd_unlc_url, optd_por_extd_unlc_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_por_unlc_url, optd_por_unlc_file, verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_extd_unlc_file)
    dq.displayFileHead (optd_por_unlc_file)

  # OPTD-maintained POR with the full details
  optd_por_dict = dict()
  with open (optd_por_extd_unlc_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      optd_unlc_code = row['unlocode']
      optd_fclass = row['feat_class']
      optd_fcode = row['feat_code']
      optd_geo_id = row['geonames_id']
      optd_coord_lat = row['latitude']
      optd_coord_lon = row['longitude']
      optd_iso31662_code = row['iso31662_code']
      optd_iso31662_name = row['iso31662_name']

      # Register the OPTD details for the POR
      if not optd_unlc_code in optd_por_dict:
        optd_por_dict[optd_unlc_code] = dict()
        
        if optd_fcode not in optd_por_dict[optd_unlc_code]:
          # Register the OPTD details for the POR
          optd_por_dict[optd_unlc_code][optd_fcode] = {
            'unlc_code': optd_unlc_code,
            'fclass': optd_fclass,
            'fcode': optd_fcode,
            'geo_lat': optd_coord_lat,
            'geo_lon': optd_coord_lon,
            'geo_id': optd_geo_id,
            'iso31662_code': optd_iso31662_code,
            'iso31662_name': optd_iso31662_name
          }

  # UN/LOCODE derived list of POR
  unlc_por_dict = dict()
  with open (optd_por_unlc_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      unlc_por_code = row['unlc']
      unlc_iata_code = row['iata_code']
      unlc_ctry_code = row['country_code']
      unlc_state_code = row['state_code']
      unlc_short_code = row['unlc_short']
      unlc_name_utf8 = row['name_utf8']
      unlc_name_ascii = row['name_ascii']
      unlc_coord_lat = row['lat']
      unlc_coord_lon = row['lon']
      unlc_change_code = row['change_code']
      unlc_status = row['status']
      unlc_is_port = row['is_port']
      unlc_is_rail = row['is_railterm']
      unlc_is_road = row['is_roadterm']
      unlc_is_apt = row['is_apt']
      unlc_is_postoff = row['is_postoff']
      unlc_is_icd = row['is_icd']
      unlc_is_fxtpt = row['is_fxtpt']
      unlc_is_brdxing = row['is_brdxing']
      unlc_is_unkwn = row['is_unkwn']

      # The UN/LOCODE-referenced POR is not referenced by OPTD
      reportStruct = (unlc_por_code, unlc_iata_code, unlc_ctry_code,
                      unlc_state_code, unlc_short_code, unlc_name_utf8,
                      unlc_name_ascii, unlc_coord_lat, unlc_coord_lon,
                      unlc_change_code, unlc_status, unlc_is_port,
                      unlc_is_rail, unlc_is_road, unlc_is_apt, unlc_is_postoff,
                      unlc_is_icd, unlc_is_fxtpt, unlc_is_brdxing,
                      unlc_is_unkwn)
      
      # Record the details in the list of UN/LOCODE indexed POR.
      # Note that there may be several records for a given UN/LOCODE,
      # typically one record per location type. For instance:
      # ADALV^42.50779^1.52109^3041563^^^P^PPLC
      # ADALV^42.51124^1.53358^7730819^^^S^AIRH
      #
      # As we are interested only by whether or not a UN/LOCODE is referenced
      # or not, there is no need so far to record all the POR with
      # different location types
      if not unlc_por_code in unlc_por_dict:
        unlc_por_dict[unlc_por_code] = reportStruct

      # Check whether the UN/LOCODE referenced POR is in the list of OPTD POR
      if not unlc_por_code in optd_por_dict:
        # UN/LOCODE not referenced by OPTD
        por_unlc_not_in_optd_list.append (reportStruct)

  # Search for OPTD POR not, or no longer, referenced by UN/LOCODE
  for optd_unlc_code in optd_por_dict:
    # The OPTD-referenced POR is not referenced by UN/LOCODE
    optd_por_list = optd_por_dict[optd_unlc_code]
    optd_fcode = next(iter(optd_por_list))
    optd_por_details = optd_por_list[optd_fcode]

    if optd_unlc_code not in unlc_por_dict:
      # Retrieve the details from OPTD
      optd_fclass = optd_por_details['fclass']
      optd_geo_id = optd_por_details['geo_id']
      optd_coord_lat = optd_por_details['geo_lat']
      optd_coord_lon = optd_por_details['geo_lon']
      optd_iso31662_code = optd_por_details['iso31662_code']
      optd_iso31662_name = optd_por_details['iso31662_name']

      reportStruct = (optd_unlc_code, optd_geo_id, optd_fclass, optd_fcode,
                      optd_coord_lat, optd_coord_lon, optd_iso31662_code,
                      optd_iso31662_name)

      # OPTD POR not referenced by UN/LOCODE
      por_optd_not_in_unlc_list.append (reportStruct)

  ## Write the output lists into CSV files
  # UN/LOCODE not referenced by OPTD
  with open (output_por_unlc_not_in_optd_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in por_unlc_not_in_optd_list:
      file_writer.writerow (record)
    
  # OPTD POR not referenced by UN/LOCODE
  with open (output_por_optd_not_in_unlc_file, 'w', newline='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in por_optd_not_in_unlc_list:
      file_writer.writerow (record)
  
  
  # DEBUG
  if verboseFlag:
    print ("OPTD POR data full dictionary:\n" + str(optd_por_dict))
