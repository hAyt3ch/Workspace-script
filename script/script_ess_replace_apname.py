# /usr/bin/python3

# usage: script_ess_replace_apname.py [-h] esx_file csv_file
# csv file format: 
# ess_#,ap_name,ess_name
# 1,B01-SS-URG11,Simulated AP-276

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

# Convert csv file to json 
# Takes the file paths as arguments 
def make_json(csvFilePath, jsonFilePath): 
	
	# create a dictionary 
	data = {} 
	
	# Open a csv reader called DictReader 
	with open(csvFilePath, encoding='utf-8') as csvf: 
		csvReader = csv.DictReader(csvf) 
		print('hello')
		# Convert each row into a dictionary 
		# and add it to data 
		for rows in csvReader: 
			# ess be the primary key 
			key = rows['ess'] 
			data[key] = rows 

	# Open a json writer, and use the json.dumps() 
	# function to dump data 
	with open(jsonFilePath, 'w', encoding='utf-8') as jsonf: 
		jsonf.write(json.dumps(data, indent=4)) 

# Parse args and return them
def get_args():
    # parse args
    parser = argparse.ArgumentParser(
        description='This script will update the name of AP based on the name from csv file')
    parser.add_argument('file_esx', metavar='esx_file', help='Ekahau project file')
    parser.add_argument('file_csv', metavar='csv_file', help='csv file using comma separator')
    args = parser.parse_args()
    # !parse args
    return args

# Make a new esx file from the input files (esx, csv)
def make_esx(file_esx, file_csv):

    # pwd
    current_filename = pathlib.PurePath(file_esx).stem
    working_directory = os.getcwd()
    # !pwd

    # extract esx file
    
    with zipfile.ZipFile(file_esx, 'r') as zipf:
        zipf.extractall(current_filename)

        # Load the accessPoints.json file into the accessPoints dictionary
        with zipf.open('accessPoints.json') as essjsonf:
            accessPoints = json.load(essjsonf)
        # Load csv file into a dictionary
        with open(file_csv, 'r', encoding='utf-8') as csvfile: 
            # Loop through the AP name in csv file
            for line in csv.DictReader(csvfile): 
                for ap in accessPoints['accessPoints']:
                    # Loop through the AP and auto populate the tag values based on the AP properties
                    if ap['mine'] is True and ap['name'] == line['ess_name']:
                        # replace esx AP Name by csv AP name
                        ap['name'] = line['ap_name']
                        

    # Write the changes into the accessPoints.json File
    with open(working_directory + '/' + current_filename + '/accessPoints.json', 'w') as file:
        json.dump(accessPoints, file, indent=4)

    # Create a new version of the Ekahau Project
    new_filename = current_filename + '_new'
    shutil.make_archive(new_filename, 'zip', current_filename)
    shutil.move(new_filename + '.zip', new_filename + '.esx')

    # Cleaning extracted files
    
    shutil.rmtree(current_filename)

if __name__ == "__main__":
    args = get_args()
    start_time = time.time()
    print('script_ess_replace_apname.py: note: Updating AP Names from csv file.\n')
    print('script_ess_replace_apname.py: note: Extracting files from esx.\n')
    make_esx(args.file_esx, args.file_csv)
    print('script_ess_replace_apname.py: note: Cleaning extracted files.\n')
    run_time = time.time() - start_time
    print("script_ess_replace_apname.py: note: A new version of the origin esx file: "+ args.file_esx + "_new was generated successfully in: %ss." % round(run_time, 2))
