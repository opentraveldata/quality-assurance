#!/usr/bin/env python3

import csv, re
import networkx as nx
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import DeliveryQuality as dq

#
k_airline_idx = 10000
k_dist_ratio = 7.0

# Main
if __name__ == '__main__':
  #
  usageStr = "That script downloads OpenTravelData (OPTD) airline-related CSV files\nand check outliers within airline networks"
  verboseFlag = dq.handle_opt(usageStr)

  ## Input
  # OPTD-maintained list of POR
  optd_por_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_por_public_all.csv?raw=true'
  optd_por_file = 'to_be_checked/optd_por_public_all.csv'

  # Airline details
  optd_airline_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airlines.csv?raw=true'
  optd_airline_file = 'to_be_checked/optd_airlines.csv'

  # List of flight leg frequencies
  optd_airline_por_url = 'https://github.com/opentraveldata/opentraveldata/blob/master/opentraveldata/optd_airline_por_rcld.csv?raw=true'
  optd_airline_por_file = 'to_be_checked/optd_airline_por_rcld.csv'

  ## Output
  # Zero-length edges on airline networks
  output_arln_net_zero_edge_file = 'results/optd-qa-airline-network-zero-edges.csv'
  arln_net_zero_edge_list = [('airline_code', 'apt_org', 'apt_dst', 'flt_freq')]

  # Nodes not in OpenTravelData (OPTD)
  output_arln_por_not_in_optd_file = 'results/optd-qa-airline-por-not-in-optd.csv'
  arln_por_not_in_optd_list = [('airline_code', 'airline_name', 'center',
                                'node') ]

  # Nodes referenced with no coordinates in OpenTravelData (OPTD)
  output_arln_zero_coord_por_in_optd_file = 'results/optd-qa-airline-zero-coord-por-in-optd.csv'
  arln_zero_coord_por_in_optd_list = [('iata_code', 'icao_code', 'geoname_id',
                                       'latitude', 'longitude') ]

  # Global airline network distance is zero
  output_arln_net_zero_distance_file = 'results/optd-qa-airline-network-zero-distance.csv'
  arln_net_zero_distance_list = [('airline_code', 'airline_name', 'center')]

  # Nodes far away from the center of the airline network
  output_arln_net_far_node_file = 'results/optd-qa-airline-network-far-nodes.csv'
  arln_net_far_node_list = [('airline_code', 'airline_name', 'subnetwork_id',
                             'center_list', 'center', 'order', 'size',
                             'avg degree', 'density', 'degree_list',
                             'degree_centrality', 'max_node', 'max_dist',
                             'avg_dist', 'ratio_dist')]
  
  # If the files are not present, or are too old, download them
  dq.downloadFileIfNeeded (optd_por_url, optd_por_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_airline_url, optd_airline_file, verboseFlag)
  dq.downloadFileIfNeeded (optd_airline_por_url, optd_airline_por_file, verboseFlag)

  # DEBUG
  if verboseFlag:
    dq.displayFileHead (optd_por_file)
    dq.displayFileHead (optd_airline_file)
    dq.displayFileHead (optd_airline_por_file)

  #
  basemap = Basemap(projection='robin',lon_0=0,resolution='l')

  #
  # OpenTravelData (OPTD) file of the POR details (optd_por_public.csv)
  #
  # iata_code^icao_code^geoname_id^envelope_id^latitude^longitude^date_from^city_code_list
  optd_por_map_dict = dict()
  optd_por_coord_dict = dict()
  primary_key_re = re.compile ("^([A-Z]{3})-([A-Z]{1,2})-([0-9]{1,15})$")
  with open (optd_por_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      # Filter out the no longer valid POR
      optd_por_env_id = row['envelope_id']
      if (optd_por_env_id != ""): continue

      # Retrieve the POR details
      optd_por_geo_id = row['geoname_id']
      optd_por_iata_code = row['iata_code']
      optd_por_icao_code = row['icao_code']
      optd_por_city_code = row['city_code_list']
      optd_por_coord_lat = row['latitude']
      optd_por_coord_lon = row['longitude']
      optd_por_date_from = row['date_from']

      # Derive a unique code, to be either IATA or ICAO
      optd_por_code = optd_por_iata_code
      if (optd_por_code == ""):
        optd_por_code = optd_por_icao_code

      # There are many POR with no IATA or ICAO code. They are not relevant here
      if (optd_por_code == ""): continue

      # Report and skip the POR having no geographical coordinates specified
      if (optd_por_coord_lat == "" or optd_por_coord_lon == ""):
        reportStruct = (optd_por_iata_code, optd_por_icao_code, optd_por_geo_id,
                        optd_por_coord_lat, optd_por_coord_lon)
        arln_zero_coord_por_in_optd_list.append (reportStruct)
        continue
      
      # Register the POR coordinates, if it is seen for the first time
      if not optd_por_code in optd_por_map_dict:
        optd_por_coord_dict[optd_por_code] = (optd_por_coord_lat, optd_por_coord_lon)
        optd_por_map_dict[optd_por_code] = basemap(optd_por_coord_lon, optd_por_coord_lat)


  #
  # airline_code^apt_org^apt_dst^seats_mtly_avg^freq_mtly_avg
  #
  airline_sched_dict = dict()
  schedule_dict = dict()
  last_airline_code = ""
  with open (optd_airline_por_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      airline_code = row['airline_code']
      apt_org = row['apt_org']
      apt_dst = row['apt_dst']
      flt_freq = float(row['freq_mtly_avg'])

      # If the airline code is new, create a (NetworkX graph)
      if airline_code != last_airline_code:
          schedule_dict[airline_code] = nx.Graph()
          last_airline_code = airline_code


      # If the flight origin and destination are the same, report it.
      # It is fine when the POR is a Seaplane Base (SPB), for instance
      # DJH/Jebel Ali SPB (http://geonames.org/10943128).
      # But sometimes it may be an issue in the schedule.
      # Nevertheless, networkx.degree_centrality() would fail
      # on such a loop edge; so, we do not add it to the network.
      if apt_org == apt_dst:
        reportStruct = (airline_code, apt_org, apt_dst, flt_freq)
        arln_net_zero_edge_list.append (reportStruct)

      # Register the flight leg as an edge into a NetworkX graph
      #idx_orig = getIdx(apt_org); idx_dest = getIdx(apt_dst)
      #schedule_dict[airline_code].add_edge (idx_orig-1, idx_dest-1, weight=flt_freq)
      if apt_org != apt_dst:
        schedule_dict[airline_code].add_edge (apt_org, apt_dst, weight=flt_freq)
      
      # Register or update a dictionary for that airline code
      airline_por_list = dict([(apt_org, flt_freq), (apt_dst, flt_freq)])
      if not airline_code in airline_sched_dict:
        # Register the flight frequencies for the origin and destination airports
        airline_sched_dict[airline_code] = airline_por_list
      else:
        airline_por_list = airline_sched_dict[airline_code]

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
        cumulated_flt_freq = airline_por_list[apt_dst]
        airline_por_list[apt_dst] = cumulated_flt_freq + flt_freq

  # DEBUG
  #nx.draw_graphviz (schedule_dict["FC"])
  #nx.draw_networkx (schedule_dict["FC"], optd_por_map_dict, node_color='blue')
  #nx.draw_networkx (schedule_dict["KT"], optd_por_map_dict, node_color='red')
  #plt.show()
  
  #
  # pk^env_id^validity_from^validity_to^3char_code^2char_code^num_code^name^name2^alliance_code^alliance_status^type^wiki_link^flt_freq^alt_names^bases^key^version
  #
  airline_dict = dict()
  with open (optd_airline_file, newline='') as csvfile:
    file_reader = csv.DictReader (csvfile, delimiter='^')
    for row in file_reader:
      pk = row['pk']
      airline_code = row['2char_code']
      airline_name = row['name']
      env_id = row['env_id']

      # Register the details for the airline, when that latter is active
      if env_id == "":
        airline_dict[airline_code] = {'airline_code': airline_code,
                                      'airline_name': airline_name}


  # DEBUG
  if verboseFlag:
    print ("Airline full dictionary:\n" + str(airline_sched_dict))


  # http://stackoverflow.com/questions/19915266/drawing-a-graph-with-networkx-on-a-basemap
# Networks on Maps: http://www.sociology-hacks.org/?p=67
  # Creating a route planner for road network: http://ipython-books.github.io/featured-03/
  
  # Decompose the airline network into independent sub-networks
  airline_idx = 1
  #for airline_code in ("K5", "U2", "9K", "LH"):
  for airline_code in airline_sched_dict:
      graph_comp_idx = 1
      current_network = schedule_dict[airline_code]
      graphs = list(nx.connected_component_subgraphs(current_network))

      for graph_comp in graphs:
          # Find the center of the sub-network
          graph_comp_center = nx.center(graph_comp)

          # Number of edges
          graph_size = graph_comp.size()

          # Number of nodes
          graph_order = graph_comp.order()

          # Average degree: size (nb of edges) / order (nb of nodes)
          graph_avg_deg = float(graph_size) / graph_order

          # Density
          graph_density = nx.density(graph_comp)

          # Degree: for every node, its number of edges
          graph_degree = graph_comp.degree()

          #
          graph_centrality = nx.degree_centrality(graph_comp)

          # DEBUG
          if verboseFlag:
              print ("[" + airline_code + "]: size=" + str(graph_size)
                     + ", order=" + str(graph_order)
                     + ", density=" + str(graph_density)
                     + ", degree=" + str(graph_degree)
                     + ", graph_centrality=" + str(graph_centrality))

              labelStr = "Sub-network[" + str(graph_comp_idx) + "] for " + airline_code
              plt.figure(k_airline_idx + graph_comp_idx)
              plt.title(labelStr)
              nx.draw_networkx (graph_comp, optd_por_map_dict,
                                node_color = 'green', label = labelStr)
              # Draw the geographical features
              basemap.drawcountries (linewidth = 0.5)
              basemap.fillcontinents (color = 'white', lake_color = 'white')
              basemap.drawcoastlines (linewidth = 0.5)

          #
          center_node = graph_comp_center[0]
          max_dist_to_center_km = 0.0
          max_dist_node = center_node
          sum_dist_km = 0.0
          for idx_node in (x for x in graph_comp if x!= center_node):
              # Distance of the current node to the center of the sub-network
              dist_to_center = nx.shortest_path_length (graph_comp,
                                                        center_node, idx_node)

              # Check whether the current node is referenced by OPTD
              if not idx_node in optd_por_map_dict:
                airline_name = airline_dict[airline_code]['airline_name']
                reportStruct = (airline_code, airline_name, center_node,
                                idx_node)
                arln_por_not_in_optd_list.append (reportStruct)
                break
              
              # Calculate the geographical distance between the current POR
              # and the network center
              dist_to_center_km = dq.geocalc (center_node, idx_node,
                                              optd_por_coord_dict)

              #
              sum_dist_km += dist_to_center_km

              #
              if dist_to_center_km > max_dist_to_center_km:
                  max_dist_to_center_km = dist_to_center_km
                  max_dist_node = idx_node


          # Check that the network is not empty
          if sum_dist_km == 0.0:
            reportStruct = (airline_code, airline_name, center_node)
            arln_net_zero_distance_list.append (reportStruct)
            continue
          
          # Calculate the geographical distance statistics (average and max)
          # The number of nodes on which the average is calculated is:
          #  * The number of nodes of the network
          #  * Minus the center node
          avg_dist_to_center_km = sum_dist_km / (graph_order-1)

          # Calculate the ratio (max distance / avg distance)
          ratio_dist = max_dist_to_center_km / avg_dist_to_center_km

          # If the airline is not known from OpenTravelData, do not report it
          # here, as it is specifically reported by the
          # check-airline-sched-in-optd.py script
          if not airline_code in airline_dict:
            continue

          # Reporting
          airline_name = airline_dict[airline_code]['airline_name']
          reportStruct = (airline_code, airline_name, graph_comp_idx,
                          graph_comp_center, center_node, graph_order,
                          graph_size, graph_avg_deg, graph_density,
                          graph_degree, graph_centrality, max_dist_node,
                          max_dist_to_center_km, avg_dist_to_center_km,
                          ratio_dist)

          if ratio_dist >= k_dist_ratio:
              arln_net_far_node_list.append (reportStruct)

          # Iteration on the sub-networks
          graph_comp_idx += 1

      # Iteration on the airlines
      airline_idx += 1

      # For the current airline
      if verboseFlag:
        a = 1
        #plt.show()

  ## Write the output lists into CSV files
  # Zero-length edges on airline networks
  with open (output_arln_net_zero_edge_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in arln_net_zero_edge_list:
      file_writer.writerow (record)
    
  # Nodes not in OpenTravelData (OPTD)
  with open (output_arln_por_not_in_optd_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in arln_por_not_in_optd_list:
      file_writer.writerow (record)

  # Nodes referenced with no coordinates in OpenTravelData (OPTD)
  with open (output_arln_zero_coord_por_in_optd_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in arln_zero_coord_por_in_optd_list:
      file_writer.writerow (record)
  
  # Global airline network distance is zero
  with open (output_arln_net_zero_distance_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in arln_net_zero_distance_list:
      file_writer.writerow (record)

  # Nodes far away from the center of the airline network
  with open (output_arln_net_far_node_file, 'w', newline ='') as csvfile:
    file_writer = csv.writer (csvfile, delimiter='^')
    for record in arln_net_far_node_list:
      file_writer.writerow (record)

