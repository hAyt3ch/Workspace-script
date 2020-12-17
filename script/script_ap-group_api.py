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
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class api_session:
  
  def __init__(self, api_url, username, password, port=4343, SSL=True,\
     check_ssl=False, verbose=True, debug = False, retrys=3, retry_wait=0.5):
    if SSL:
      protocol = "https"
    else:
      protocol = "http"

    self.__session = None
    self.__api_token = None
    self.__api_url = f"{protocol}://{api_url}:{port}/v1/"
    self.__username = username
    self.__password = password
    self.__check_ssl = check_ssl
    self.__verbose = verbose
    self.__debug = debug
    self.__retrys = retrys
    self.__retry_wait = retry_wait

  def _login(self):
    self.__session = requests.Session()
    try:
      url = f"{self.__api_url}api/login?username={self.__username}\
&password={self.__password}"
      for i in range(1,self.__retrys+1):
        if self.__verbose:
          print("\n**[AP_GROUP Genrator]: login, try {}".format(str(i)))
        response = self.__session.get(url, verify=self.__check_ssl)
        cookie = response.json()
        if self.__debug:
          print ("Debug: {}".format(cookie["_global_result"]["status_str"]))
        if cookie["_global_result"]["status"] == "0":
          self.__api_token = cookie["_global_result"]["UIDARUBA"]
          return cookie
        if i == self.__retrys:
          if self.__verbose:
            print("There was an Error with the login. \
              Please check the credentials.",file=sys.stderr)
            print("Controller-IP: {}, Username: {}".format(\
              self.__api_url,self.__username),file=sys.stderr)
          raise PermissionError(\
            "There was an Error with the login.\
               Please check the credentials of the User \
                 >{}< at host >{}<".format(self.__username,self.__api_url))
        time.sleep(self.__retry_wait)
    except:    
        exit

  def _logout(self):
    response = self.__session.get(self.__api_url + "api/logout")
    logout_data = json.loads(response.text)
    self.__api_token = None
    if self.__verbose:
      print ("\n**[AP_GROUP Genrator]: {}".format(logout_data["_global_result"]["status_str"]))

  def _get(self, api_path, config_path=None):
    if self.__api_token == None:
      self._login()
    node_path = None
    if config_path is not None:
      node_path = "&config_path={}".format(config_path)
    else:
      node_path = ""
    response = self.__session.get("{}{}?UIDARUBA={}{}".format(self.__api_url,api_path,self.__api_token,node_path))
    data = json.loads(response.text)
    if self.__debug:
      print ("\nVerbose: " + str(data))
    return data

  def _post(self, api_path, data, config_path="/md"):
    if self.__api_token == None:
      self._login()
    response = self.__session.post("{}{}?UIDARUBA={}&config_path={}".format(self.__api_url,api_path,self.__api_token,config_path), json=data)
    data = json.loads(response.text)
    if self.__debug:
      print ("\n**[AP_GROUP Genrator]: {}".format(str(data)))
    return data

  def _write_memory(self, config_path):
    node_path = "?config_path=" + config_path
    nothing = json.loads('{}')
    response = self.__session.post("{}configuration/object/write_memory{}&UIDARUBA={}".format(self.__api_url,node_path,self.__api_token),json=nothing)
    data = json.loads(response.text)
    if self.__verbose:
      print ("\n**[AP_GROUP Genrator]: {}".format(str(data)))
    return data

  def _cli_command(self, command):
    mod_command = command.replace(" ", "+")
    response = self.__session.get(\
      f"{self.__api_url}configuration/showcommand?command={mod_command}&UIDARUBA={self.__api_token}")
    data = json.loads(response.text)
    if self.__verbose:
      print ("\n**[AP_GROUP Genrator]: {}".format(str(data)))
    return data

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

  session = api_session("192.168.4.169", "api", "TEv72x84qCB")

  session._login()

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

      bar = IncrementalBar('**[AP_GROUP Genrator]: Countdown', max = len(lines))

      for line in lines:
        boolean_interior = re.findall(pattern_interior, line.strip())
        boolean_exterior = re.findall(pattern_exterior, line.strip())

        if not boolean_interior and not boolean_exterior:
          print('\n**[AP_GROUP Genrator]: the input file %s contain an invalid \
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
            print('\n**[AP_GROUP Generator]: Program have to stop')
            exit
  #session._cli_command()
  session._logout()

if __name__ == "__main__":
    start_time = time.time()
    print('\n**[AP_GROUP Generator]: Pushing configuration ...')
    main()
    run_time = time.time() - start_time
    print("\n**[AP_GROUP Generator]: \
Configuration pushed successfully after: %s sec" % round(run_time, 2))