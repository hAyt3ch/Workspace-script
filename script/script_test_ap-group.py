from aos8 import session_handler
import argparse
import time
from progress.bar import IncrementalBar
import os
import json
import pathlib
import shutil
from pprint import pprint
import re
import requests
import sys
import urllib3
import getpass

def build_radio_profile(radio_profile_name, radio_profile_data, postfix):
  radio_profile_name += postfix
  radio_profile_data['profile-name'] = radio_profile_name
  return radio_profile_name

def build_profile_ap_group(ap_group_name, ap_group_data, dot11a_profile, \
  dot11g_profile):
  ap_group_data['profile-name'] = ap_group_name
  ap_group_data['dot11a_prof']['profile-name'] = dot11a_profile
  ap_group_data['dot11g_prof']['profile-name'] = dot11g_profile

def main():
  parser = argparse.ArgumentParser(
      description='This script will push rf profiles and ap groups to the MM')
  parser.add_argument('file', metavar='txt_file', help='txt file')
  parser.add_argument('dot11a', metavar='json_file', help='json file')
  parser.add_argument('dot11g', metavar='json_file', help='json file')
  parser.add_argument('ap_group', metavar='json_file', help='json file')
  args = parser.parse_args()

  current_filename = pathlib.PurePath(args.file).stem
  dot11a_filename = pathlib.PurePath(args.dot11a).stem
  dot11g_filename = pathlib.PurePath(args.dot11g).stem
  ap_group_filename = pathlib.PurePath(args.ap_group).stem
  
  #working_directory = os.getcwd()
  input_filename = current_filename + '.txt'
  dot11g_filename = dot11g_filename + '.json'
  dot11a_filename = dot11a_filename + '.json'
  ap_group_filename = ap_group_filename + '.json'

  try:
      username = input('Login:')
      pwd = getpass.getpass('Password:')
  except Exception as error:
      print('Error', error)
  else:
      session = session_handler.mm_session('10.10.93.100', username, pwd)

  session._login()

  print('[AP_GROUP Generator]: Please holdon while preparing the configuration ...')

  with open(input_filename, 'r', encoding='utf-8') as f_in, \
    open(dot11a_filename, 'r') as f_dot11a,\
      open(dot11g_filename, 'r') as f_dot11g, \
        open(ap_group_filename, 'r') as f_ap_group:

      dot11a_data = json.load(f_dot11a)
      dot11g_data = json.load(f_dot11g)
      ap_group_data = json.load(f_ap_group)

      lines = f_in.readlines()

      pattern_interior = r'^\d{3}-\w*.*-AP-GROUP$'
      pattern_exterior = r'^\d{3}-\w*.*-AP-GROUP-EXT$'

      bar = IncrementalBar('[AP_GROUP Genarator]: Pushing AP_Group configuration', max = len(lines))

      for line in lines:
        boolean_interior = re.findall(pattern_interior, line.strip())
        boolean_exterior = re.findall(pattern_exterior, line.strip())

        if not boolean_interior and not boolean_exterior:
          print('\n[AP_GROUP Genrator]: the input file %s contain an invalid \
AP-Group format.'% input_filename)
        else:
          establishment_number = line[0:3]
          dot11a_radio = dot11g_radio = establishment_number
          dot11a_radio = build_radio_profile(dot11a_radio, dot11a_data, \
            '-dot11a' if boolean_interior else '-dot11a-ext')
          dot11g_radio = build_radio_profile(dot11g_radio, dot11g_data, \
            '-dot11g' if boolean_interior else '-dot11g-ext')
          build_profile_ap_group(line, ap_group_data, dot11a_radio, dot11g_radio)
          data_post_dot11a = session._post('configuration/object/ap_a_radio_prof', dot11a_data,'/md/CSSC')
          data_post_dot11g = session._post('configuration/object/ap_g_radio_prof'\
            ,dot11g_data,'/md/CSSC')
          data_post_ap_group = session._post('configuration/object/ap_group', \
            ap_group_data,'/md/CSSC')
          if data_post_ap_group and data_post_dot11a and data_post_dot11g:
            bar.next()
            time.sleep(1)
          else:
            print('\n[AP_GROUP Generator]: Program have to stop')
            exit
  #session._cli_command()
  session._logout()

if __name__ == "__main__":
    start_time = time.time()
    print('\n[AP_GROUP Generator]: Welcome, please log me to the MM ...')
    main()
    run_time = time.time() - start_time
    print("\n[AP_GROUP Generator]: \
Configuration pushed successfully after: %s sec" % round(run_time, 2))