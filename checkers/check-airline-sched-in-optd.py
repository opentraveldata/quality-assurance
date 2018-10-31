#!/usr/bin/env python3

import csv, datetime
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) airline-related CSV files\nand check that the scheduled airlines are present in the OPTD airline file"
  verboseFlag = dq.handle_opt(usageStr)

  # Airline details
  optd_airline_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv?raw=true'
  optd_airline_file = 'to_be_checked/optd_airlines.csv'

  # List of flight leg frequencies
  optd_airline_por_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por_rcld.csv?raw=true'
  optd_airline_por_file = 'to_be_checked/optd_airline_por_rcld.csv'

  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_airline_url, optd_airline_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_airline_por_url, optd_airline_por_file, verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_airline_file)
    dq.displayFileHead (optd_airline_por_file)

  #
  # pk^env_id^validity_from^validity_to^3char_code^2char_code^num_code^name^name2^alliance_code^alliance_status^type^wiki_link^flt_freq^alt_names^bases^key^version
  #
  airline_dict = dict()
  with open (optd_airline_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      pk = row['pk']
      airline_2code = row['2char_code']
      airline_3code = row['3char_code']
      airline_name = row['name']
      pk = row['pk']
      env_id = row['env_id']
      version = row['version']
      date_from = row['validity_from']
      date_to = row['validity_to']

      # Take into account airlines having a ICAO code but no IATA code
      airline_code = airline_2code
      if (airline_code == ""):
        airline_code = airline_3code

      # Register or update the details for that airline code
      if not airline_code in airline_dict and env_id == '':
        airline_dict[airline_code] = dict()
        airline_dict[airline_code][pk] = {'airline_name': airline_name,
                                          'env_id': env_id,
                                          'version': version,
                                          'validity_from': date_from,
                                          'validity_to': date_to}

  #
  # airline_code^apt_org^apt_dst^seats_mtly_avg^freq_mtly_avg
  #
  airline_sched_dict = dict()
  with open (optd_airline_por_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      airline_code = row['airline_code']
      apt_org = row['apt_org']
      apt_dst = row['apt_dst']
      flt_freq = float(row['freq_mtly_avg'])

      #
      if not airline_code in airline_dict and not airline_code in airline_sched_dict:
        airline_sched_dict[airline_code] = True
        reportStr = {'airline_code': airline_code}
        print (str(reportStr))

  # DEBUG
  if verboseFlag:
    print ("Airline full dictionary:\n" + str(airline_dict))
