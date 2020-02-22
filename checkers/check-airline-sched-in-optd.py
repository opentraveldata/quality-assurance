#!/usr/bin/env python3

import csv, datetime
import DeliveryQuality as dq

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) airline-related " \
    "CSV files\nand check that the scheduled airlines are present in " \
    "the OPTD airline file"
  verboseFlag = dq.handle_opt(usageStr)

  # Airline details
  optd_airline_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv?raw=true'
  optd_airline_file = 'to_be_checked/optd_airlines.csv'

  # List of flight leg frequencies
  k_w_seats = False
  optd_airline_por_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por.csv?raw=true'
  optd_airline_por_file = 'to_be_checked/optd_airline_por.csv'
  if k_w_seats:
    optd_airline_por_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por_rcld.csv?raw=true'
    optd_airline_por_file = 'to_be_checked/optd_airline_por_rcld.csv'

  ## Output
  # List of airlines present in schedules and not in OPTD
  output_arln_schd_no_optd_file = 'results/optd-qa-airline-schd-not-in-optd.csv'
  arln_not_in_optd_hdr = ('airline_code', 'clted_flt_freq')
  arln_not_in_optd_list = []

  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_airline_url, optd_airline_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_airline_por_url, optd_airline_por_file,
                           verboseFlag)

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
  # Without seats (optd_airline_por.csv):
  # airline_code^apt_org^apt_dst^flt_freq
  #
  # With seats (optd_airline_por_rcld.csv):
  # airline_code^apt_org^apt_dst^seats_mtly_avg^freq_mtly_avg
  #
  airline_sched_non_optd_dict = dict()
  with open (optd_airline_por_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      airline_code = row['airline_code']
      apt_org = row['apt_org']
      apt_dst = row['apt_dst']
      flt_freq = 0
      if k_w_seats:
        flt_freq = float(row['freq_mtly_avg'])
      else:
        flt_freq = int(row['flt_freq'])

      # Check whether the airline, appearing in the schedule,
      # is known from OPTD. If not, report it and keep track
      # of the total flight frequency so far for that airline
      if not airline_code in airline_dict:
        if not airline_code in airline_sched_non_optd_dict:
          airline_sched_non_optd_dict[airline_code] = 0

        # Keep track of the total flight frequency so far for that airline
        clted_flt_freq = airline_sched_non_optd_dict[airline_code] + flt_freq
        airline_sched_non_optd_dict[airline_code] = clted_flt_freq

  # Fill in the reporting list
  for airline_code, clted_flt_freq in airline_sched_non_optd_dict.items():
    reportStr = (airline_code, clted_flt_freq)
    arln_not_in_optd_list.append (reportStr)

  ## Write the output lists into CSV files
  # Sort by cumulated frequency, which are numbers (that is why the header
  # is added only after sorting)
  def sortSecond (row): return row[1]
  arln_not_in_optd_list.sort (key = sortSecond, reverse = True)
  # Insert the header
  arln_not_in_optd_list.insert (0, arln_not_in_optd_hdr)

  # Bases not appearing in flight legs
  with open (output_arln_schd_no_optd_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in arln_not_in_optd_list:
      file_writer.writerow (record)
      
  # DEBUG
  if verboseFlag:
    print ("Airline full dictionary:\n" + str(airline_dict))
