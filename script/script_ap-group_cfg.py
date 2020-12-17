import argparse
import time
import os
import json
import pathlib
import shutil
from pprint import pprint
import re

def main():
    parser = argparse.ArgumentParser(
        description='This script will update the name of AP based on the name from csv file')
    parser.add_argument('file', metavar='txt_file', help='txt file')
    args = parser.parse_args()

    current_filename = pathlib.PurePath(args.file).stem
    
    #working_directory = os.getcwd()
    input_filename = current_filename + '.txt'
    print('[Script Genrator]: your input file name is: ' + input_filename)
    output_filename = current_filename + "_scipt.cfg"

    with open(output_filename, 'w', encoding='utf-8') as f_out:
        with open(input_filename, 'r', encoding='utf-8') as f_in:
            lines = f_in.readlines()
            for line in lines:
                boolean_1 = re.findall(r'^\d{3}-\w*.*-AP-GROUP$', line.strip())
                boolean_2 = re.findall(r'^\d{3}-\w*.*-AP-GROUP-EXT$', line.strip())
                establishment_number = line[0:3]
                cmd_line = None
                rf_dot11a_cmd_line = 'rf dot11a-radio-profile '
                rf_dot11g_cmd_line = 'rf dot11g-radio-profile '
                ap_group_cmd_line = f'ap-group {line.strip()}\r\n    virtual-ap CSSC\r\n    virtual-ap CSSC-PUBLIC\r\n'
                dot11a_radio = establishment_number
                dot11g_radio = establishment_number
                if boolean_1:
                    dot11a_radio = dot11a_radio +'-dot11a'
                    rf_dot11a_cmd_line = rf_dot11a_cmd_line + dot11a_radio + '\r\n    no high-efficiency-enable\r\n' + '    max-channel-bandwidth 40MHz\r\n' + '    eirp-min 18\r\n' + '    eirp-max 21\r\n!\r\n'
                    dot11g_radio = dot11g_radio +'-dot11g'
                    rf_dot11g_cmd_line = rf_dot11g_cmd_line + dot11g_radio + '\r\n    no high-efficiency-enable\r\n' + '    very-high-throughput-rates-enable\r\n' + '    eirp-min 18\r\n' + '    eirp-max 21\r\n!\r\n'
                elif boolean_2:
                    dot11a_radio = dot11a_radio +'-dot11a-ext'
                    rf_dot11a_cmd_line = rf_dot11a_cmd_line + dot11a_radio + '\r\n    no high-efficiency-enable\r\n' + '    max-channel-bandwidth 40MHz\r\n' + '    eirp-min 18\r\n' + '    eirp-max 21\r\n!\r\n'
                    dot11g_radio = dot11g_radio +'-dot11g-ext'
                    rf_dot11g_cmd_line = rf_dot11g_cmd_line + dot11g_radio + '\r\n    no high-efficiency-enable\r\n' + '    very-high-throughput-rates-enable\r\n' + '    eirp-min 18\r\n' + '    eirp-max 21\r\n!\r\n'
                else:
                    print('file : %s contain non valid ap-group.', input_filename)
                ap_group_cmd_line = ap_group_cmd_line + f'    dot11a-radio-profile {dot11a_radio}\r\n' + f'    dot11a-radio-profile {dot11g_radio}\r\n!\r\n'
                cmd_line = rf_dot11a_cmd_line + rf_dot11g_cmd_line + ap_group_cmd_line
                f_out.write(cmd_line)
if __name__ == "__main__":
    start_time = time.time()
    print('Generating cfg script ...\n')
    main()
    run_time = time.time() - start_time
    print("\n** Time to run: %s sec" % round(run_time, 2))