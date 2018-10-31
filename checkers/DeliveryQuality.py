
import urllib.request, shutil, csv, datetime, re, getopt, sys, os
import numpy as np
import networkx as nx

# Index increment
k_idx_inc = 100
k_ascii = 64

#
k_earth_radius = 6372.8

def usage (script_name, usage_doc):
  """Display the usage for that program."""
  print ("")
  print ("Usage: %s [options]" % script_name)
  print ("")
  print (usage_doc)
  print ("")
  print ("Options:")
  print ("  -h, --help      : outputs this help and exits")
  print ("  -v, --verbose   : verbose output (debugging)")
  print ("")

def handle_opt (usage_doc):
  """Handle the command-line options."""
  try:
    opts, args = getopt.getopt (sys.argv[1:], "hv", ["help", "verbose"])
  except (getopt.GetoptError, err):
    # Print help information and exit. It will print something like
    # "option -a not recognized"
    print (str (err))
    usage (sys.argv[0], usage_doc)
    sys.exit(2)

  # Options
  verboseFlag = False
  for o, a in opts:
    if o in ("-h", "--help"):
      usage (sys.argv[0], usage_doc)
      sys.exit()
    elif o in ("-v", "--verbose"):
      verboseFlag = True
    else:
      assert False, "Unhandled option"
  return (verboseFlag)

def downloadFile (file_url, output_file, verbose_flag = False):
  """Download a file from the Web."""
  if verbose_flag:
    print ("Downloading '" + output_file + "' from " + file_url + "...")
  with urllib.request.urlopen (file_url) as response, open (output_file, 'wb') as out_file:
    shutil.copyfileobj (response, out_file)
  if verbose_flag:
    print ("... done")
  return

def downloadFileIfNeeded (file_url, output_file, verbose_flag = False):
  """Download a file from the Web, only if newer on that latter."""
  # Check whether the output_file has already been downloaded
  try:
    if os.stat (output_file).st_size > 0:
      file_time = datetime.datetime.fromtimestamp (os.path.getmtime (output_file))
      if verbose_flag:
        print ("Time-stamp of '" + output_file + "': " + str(file_time))
        print ("If that file is too old, you can delete it, and re-execute that script")
    else:
      downloadFile (file_url, output_file, verbose_flag)
  except OSError:
    downloadFile (file_url, output_file, verbose_flag)
  return

def displayFileHead (input_file):
  """Display the first 10 lines of the given file."""
  #
  print ("Header of the '" + input_file + "' file")
  #
  with open (input_file, newline='') as csvfile:
    file_reader = csv.reader (csvfile, delimiter='^')
    for i in range(10):
      print (','.join(file_reader.__next__()))

  #
  return

def geocalcbycoord(lat0, lon0, lat1, lon1):
    """Return the distance (in km) between two points in 
    geographical coordinates."""
    lat0 = np.radians(lat0)
    lon0 = np.radians(lon0)
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    dlon = lon0 - lon1
    y = np.sqrt(
        (np.cos(lat1) * np.sin(dlon)) ** 2
         + (np.cos(lat0) * np.sin(lat1) 
         - np.sin(lat0) * np.cos(lat1) * np.cos(dlon)) ** 2)
    x = np.sin(lat0) * np.sin(lat1) + \
        np.cos(lat0) * np.cos(lat1) * np.cos(dlon)
    c = np.arctan2(y, x)
    return k_earth_radius * c

def geocalc (node1, node2, coord_dict):
    """Return the geographical distance (in km) between
    two nodes of a NetworkX Graph."""
    lat0 = float(coord_dict[node1][0])
    lon0 = float(coord_dict[node1][1])
    lat1 = float(coord_dict[node2][0])
    lon1 = float(coord_dict[node2][1])
    return geocalcbycoord(lat0, lon0, lat1, lon1)

def getIdx (iata_code):
    """Return the ID associated to the POR (thanks to its IATA code)."""
    idx = 0
    if (len(iata_code) != 3):
        idx = 0
    ic1 = (ord(iata_code[0]) - k_ascii) * k_idx_inc**2
    ic2 = (ord(iata_code[1]) - k_ascii) * k_idx_inc
    ic3 = ord(iata_code[2]) - k_ascii
    idx = ic1 + ic2 + ic3
    return idx

def getIataCode (idx):
    """Return the IATA code corresponding to the ID."""
    ic1 = int(idx / k_idx_inc**2)
    ic2 = int((idx - ic1 * k_idx_inc**2) / k_idx_inc)
    ic3 = idx - (ic1 * k_idx_inc**2 + ic2 * k_idx_inc)
    iata_code = chr(ic1 + k_ascii) + chr(ic2 + k_ascii) + chr(ic3 + k_ascii)
    return iata_code

def getFullStateCode (country_code, state_code):
    """Return the ISO 3166-2 full code, which is the composition of
    the country code (ISO 3166-1) and the state code (ISO 3166-2)"""
    full_state_code = country_code + "-" + state_code
    return full_state_code
