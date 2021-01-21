from arubafi import MMClient
import argparse
import time
from progress.bar import IncrementalBar
import json
import pathlib
import re
import sys

import logging
import logzero
from logzero import setup_logger

from template_builder import mm_builder

main_logger = setup_logger(name="main_logger", logfile="push_ap_group.log", level=logging.INFO)

def measure_time(func):                                                                                                                                                                                                                           
  def wrapper(*arg):
    start = time.time()                                                                                                     
    res = func(*arg)
    run_time=time.time()-start                                                                                                 
    main_logger.info('Configuration pushed successfully after: %s sec' % round(run_time, 2))
    return res
  return wrapper

@measure_time
def main():
  
  main_logger.info('Welcome!')
  
  parser = argparse.ArgumentParser(
      description='This script will push rf profiles and ap groups to the MM')
  parser.add_argument('file', metavar='txt_file', help='txt file')
  parser.add_argument('template', metavar='string', help='template string')
  
  args = parser.parse_args()

  current_filename = pathlib.PurePath(args.file).stem
  template = pathlib.PurePath(args.template).stem
  template_len = len(template)
  if template_len >= 16:
    main_logger.error('The second args format is not correct,\
       the node string should be maximum of 16 characters')
  
  #working_directory = os.getcwd()
  input_filename = current_filename + '.txt'

  mm_session = mm_builder.MMBuilder.mm_login(mm_host='10.10.93.100', username='apiuser')

  main_logger.info('Please hold-on while preparing the configuration ...')

  with open(input_filename, 'r', encoding='utf-8') as f_in:

      lines = f_in.readlines()

      pattern_interior = r'^\d{3}-\w*.*-AP-GROUP$'
      pattern_exterior = r'^\d{3}-\w*.*-AP-GROUP-EXT$'

      main_logger.info('Pushing AP_Group configuration')
      with IncrementalBar('Loading',max = len(lines), suffix='%(percent)d%%') as bar:

        for line in lines:
          boolean_interior = re.findall(pattern_interior, line.strip())
          boolean_exterior = re.findall(pattern_exterior, line.strip())

          if not boolean_interior and not boolean_exterior:
            main_logger.warning('The input file %s contain an invalid \
            AP-Group format.'% input_filename)
            exit(0)
          else:
            build_profiles = mm_builder.MMBuilder(ap_group_name=line, template_name=template, \
              ant_ext=False if boolean_interior else True)
            if build_profiles.build_ap_group_profile():
              bar.next()
              time.sleep(1)
            else:
              main_logger.error('There is no valid ap-group data. The script is quitting.')
              mm_builder.MMBuilder.mm_purge_config()
              exit(0)

  
  mm_builder.MMBuilder.mm_logout()
  
if __name__ == "__main__":
  main()
    
    