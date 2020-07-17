# Built-in Modules
import re           # For pattern matching within strings
import json         # For working with json data
import os           # For accessing features of the operating system
import threading
import concurrent.futures
import datetime
import time
# Third-party Modules
from progress.bar import IncrementalBar    # For showing graphical loading bars
from retrying import retry                 # For automatically retrying code that throws errors
import requests                            # For making http requests
import pandas as pd                        # For working with tabular data
from tqdm import tqdm
# Internal Modules
from config import config
from modules import login, file_browser, global_variables
import main
import gui #DEV
import PySimpleGUI as sg

# Reinforces that the variables defined in the global_variables module, and then edited from within other modules,
# continue to have the value that the user changed it to.
# It may look redundant, but without this line, the script only uses the default variable, without reflecting changes.

global_variables.JSON_INPUT_OUTPUT_PATH = global_variables.JSON_INPUT_OUTPUT_PATH
global_variables.CLIENT_MATTER = global_variables.CLIENT_MATTER

def table_to_list_of_tuples():
    spreadsheet_path = global_variables.CSV_INPUT_PATH
    JSON_INPUT_OUTPUT_PATH = global_variables.JSON_INPUT_OUTPUT_PATH
    CLIENT_MATTER = global_variables.CLIENT_MATTER
    output_list_of_tuples = []

    try:
        df = pd.read_csv(spreadsheet_path)
        len_df = len(df)
    except Exception as e:
        print(f"{e}")
        input()
    
 
    for index, row in df.iterrows():
        caseName = row[0]
        caseNo = row[1]
        caseCourt = row[2]
        row_tuple = (caseName, caseNo, caseCourt, JSON_INPUT_OUTPUT_PATH, CLIENT_MATTER)
        output_list_of_tuples.append(row_tuple)
    
    return output_list_of_tuples

@retry
def download_json_from_list_of_tuples(result_tuple):

    caseName, caseNo, caseCourt, JSON_INPUT_OUTPUT_PATH, CLIENT_MATTER = result_tuple

    user = login.Credentials()

    # The endpoint we will be connecting to. Calls to this endpoint return the json data for the docket we want.
    getdocket_url = "https://www.docketalarm.com/api/v1/getdocket/"

    # The parameters we pass to the endpoint. This is how the API knows how to find what we are looking for.
    data = {
        # The token generated after logging in.
        'login_token': user.authenticate(),
        # The reason for use
        'client_matter': CLIENT_MATTER,
        # The court we want to search.
        'court': caseCourt,
        # The docket number we want data for
        'docket':caseNo,
        # A boolean representing whether or not we want the cached version of the data.
        'cached': config.isCached,
        # Cleans up names
        'normalize':True,
    }

    # Makes the api call. We specify the endpoint and the parameters as arguments. The results of the API call are returned and
    # stored to a variable. 
    result = requests.get(getdocket_url, data, timeout=100)

    

    try:
        result.raise_for_status() #DEV
    except:
        result_json = None
        print(result)
        print(caseName)
        print(caseNo)
        timeNow = datetime.datetime.now().strftime("%I:%M%p %B %d, %Y")
        with open(os.path.join('log', 'log.txt'), 'a') as errorlog:
            errorlog.write(f"\n{timeNow}\n")
            errorlog.write("JSON could not be downloaded:\n")
            errorlog.write(f"{result}: {caseName}, {caseNo}, {caseCourt}\n")
            errorlog.write("------------------")
        return
    result_json = result.json()
    # We use .json() to convert the json results to a python dictionary we can more easily work with.

    
    try:
        # Created the path where our .json file will be saved to
        # filePathNameWExt = os.path.join(config.cwd, folder, fileName + '.json')
        filePathNameWExt = os.path.join(JSON_INPUT_OUTPUT_PATH, f"{caseName} {caseNo}" + '.json')


        # When 'opening' a file that doesn't yet exist, we create that file.
        # Here, we create the json file we'll be saving the data to.
        with open(filePathNameWExt, 'w') as fp:

            # Then we write the data to the newly created .json file.
            json.dump(result_json,fp)

    except Exception as e:
        print("\nError writing json file.\nReference the documentation for more information\n")
        input()
        print(e)
    return

def thread_download_json():
    tuples_from_table = table_to_list_of_tuples()
    maximum = len(tuples_from_table)
    print("Downloading JSON files...")
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(download_json_from_list_of_tuples, tuples_from_table), total=maximum))
    finish = time.perf_counter()
    print(f"Finished downloading JSON files in {round(finish-start)} seconds.")
    return results