import sys
import time
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

'''
@author: hkefi@outlook.com

@desc: class routines to send post get http request to an aruba Mobility Master

@version: 1.0.0_build
'''

class mm_session:
  
  def __init__(self, api_url, username, password, port=4343, SSL=True,\
     check_ssl=False, verbose=False, debug = False, retrys=3, retry_wait=0.5):
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
    
    try:
      self.__session = requests.Session()
      url = f"{self.__api_url}api/login?username={self.__username}\
&password={self.__password}"
      for i in range(1,self.__retrys+1):
        if self.__verbose:
          print("\n**[session_handler]: login, try {}".format(str(i)))
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
      print ("\n**[session_handler]: {}".format(logout_data["_global_result"]["status_str"]))

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
      print ("\n**[session_handler]: {}".format(str(data)))
    return data

  def _write_memory(self, config_path):
    node_path = "?config_path=" + config_path
    nothing = json.loads('{}')
    response = self.__session.post("{}configuration/object/write_memory{}&UIDARUBA={}".format(self.__api_url,node_path,self.__api_token),json=nothing)
    data = json.loads(response.text)
    if self.__verbose:
      print ("\n**[session_handler]: {}".format(str(data)))
    return data

  def _cli_command(self, command):
    mod_command = command.replace(" ", "+")
    response = self.__session.get(\
      f"{self.__api_url}configuration/showcommand?command={mod_command}&UIDARUBA={self.__api_token}")
    data = json.loads(response.text)
    if self.__verbose:
      print ("\n**[session_handler]: {}".format(str(data)))
    return data
