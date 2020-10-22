import csv 
import json 
import argparse
import time
import os
import zipfile
import json
import pathlib
import shutil
from pprint import pprint

def main():
    parser = argparse.ArgumentParser(
        description='This script will update the name of AP based on the name from csv file')
    parser.add_argument('file', metavar='csv_file', help='csv file')
    args = parser.parse_args()

    current_filename = pathlib.PurePath(args.file).stem
    
    #working_directory = os.getcwd()
    input_filename = current_filename + '.csv'
    print('[Script Genrator]: your input file name is: ' + input_filename)
    output_filename = current_filename + "_scipt.cfg"
    # opening the file using "with"  
    # statement
    cli_cmd_begin = 'provision-ap\n'
    ap_mac_column = ':' 
    ap_mac = ''
    ap_name = ''
    with open(output_filename, 'w', encoding='utf-8') as jsonf: 

        with open(input_filename, 'r', encoding='utf-8') as data: 
            
            for line in csv.DictReader(data): 
                ap_mac = line['ap-mac']
                ap_name = line['ap-name']
                ap_group = line['ap-group']
                ap_mac_column = ':'.join(format(s, '02x') for s in bytes.fromhex(ap_mac))
                cli_cmd = cli_cmd_begin + f'read-bootinfo ap-name {ap_mac_column}\n' + f'ap-name {ap_name}\n' + f'ap-group {ap_group}\n' + f'reprovision ap-name {ap_name}\n' + '!\n'
                print(cli_cmd) 
                jsonf.write(cli_cmd)
if __name__ == "__main__":
    start_time = time.time()
    print('Generating cfg script ...\n')
    main()
    run_time = time.time() - start_time
    print("\n** Time to run: %s sec" % round(run_time, 2))
