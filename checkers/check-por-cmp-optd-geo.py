#!/usr/bin/env python3

import csv, re, datetime
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) POR-related CSV " \
    "files\nand check the differences in geo-coordinates between OPTD " \
    "and Geonames"
  verboseFlag = dq.handle_opt(usageStr)

  ## Input
  # OPTD-maintained list of POR
  optd_por_public_url = \
    'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public.csv?raw=true'
  optd_por_public_file = 'to_be_checked/optd_por_public.csv'

  ## Output
  # OPTD points of reference (POR) not referenced by IATA
  output_por_optd_geo_diff_file = 'results/optd-qa-por-optd-geo-diff.csv'
  optd_por_optd_geo_diff_hdr = ('iata_code', 'geoname_id', 'location_type',
                                'country_code', 'adm1_code', 'page_rank',
                                'optd_lat', 'optd_lon', 'dist',
                                'geoname_lat', 'geoname_lon', 'wgted_geodist')
        
  optd_por_optd_geo_diff_list = []
  
  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_public_url, optd_por_public_file,
                           verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_public_file)

  # OPTD-maintained POR with the full details
  optd_por_dict = dict()
  with open (optd_por_public_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      por_code = row['iata_code']
      loc_type = row['location_type']
      geo_id = row['geoname_id']
      optd_coord_lat = row['latitude']
      optd_coord_lon = row['longitude']
      page_rank = row['page_rank']
      ctry_code = row['country_code']
      adm1_code = row['adm1_code']
      geoname_lat = row['geoname_lat']
      geoname_lon = row['geoname_lon']

      if (geoname_lat != ""):
        # Sanity check
        assert (geoname_lon != ""), \
          f"Error - {por_code}-{loc_type}-{geo_id} has non null " \
          f"Geonames latitude ({geoname_lat}) but null Geonames longitude"

        # Conversion to floats
        optd_coord_lat = float (optd_coord_lat)
        optd_coord_lon = float (optd_coord_lon)
        geoname_lat = float (geoname_lat)
        geoname_lon = float (geoname_lon)
                                     
        # Calculate the great circle distance between the two geo-coordinates
        geodist = dq.geocalcbycoord (optd_coord_lat, optd_coord_lon,
                                     geoname_lat, geoname_lon)
        wgted_geodist = geodist
        if page_rank != "":
          page_rank = float (page_rank)
          wgted_geodist = geodist * (1.0 + 1e4 * page_rank)

        reportStruct = (por_code, geo_id, loc_type, ctry_code, adm1_code,
                        page_rank, optd_coord_lat, optd_coord_lon, geodist,
                        geoname_lat, geoname_lon, wgted_geodist)
        optd_por_optd_geo_diff_list.append (reportStruct)
        
      else:
        # Sanity check
        assert (geoname_lon == ""), \
          f"Error - {por_code}-{optd_loc_type}-{optd_geo_id} has null " \
          f"Geonames latitude ({geoname_lat}) but non null Geonames longitude"

  ## Write the output lists into CSV files

  # Sort by Geonames ID, which are numbers (that is why the header is added
  # only after sorting)
  def sortLast (row): return row[-1]
  optd_por_optd_geo_diff_list.sort (key = sortLast, reverse = True)
  # Insert the header
  optd_por_optd_geo_diff_list.insert (0, optd_por_optd_geo_diff_hdr)

  # OPTD points of reference (POR) havving different geo-coorddinates
  # for OPTD and Geonames
  with open (output_por_optd_geo_diff_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in optd_por_optd_geo_diff_list:
      file_writer.writerow (record)

