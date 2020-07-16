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

def write_to_json_file(fileName, data):
    """ 
    takes in the name of a folder in the current directory, the name of
    the file you want to create, and the json object you want to write to
    the file.
    """ 

    try:
        # Created the path where our .json file will be saved to
        # filePathNameWExt = os.path.join(config.cwd, folder, fileName + '.json')
        filePathNameWExt = os.path.join(global_variables.JSON_INPUT_OUTPUT_PATH, fileName + '.json')


        # When 'opening' a file that doesn't yet exist, we create that file.
        # Here, we create the json file we'll be saving the data to.
        with open(filePathNameWExt, 'w') as fp:

            # Then we write the data to the newly created .json file.
            json.dump(data,fp)
    
    except Exception as e:
        print("\nError writing json file.\nReference the documentation for more information\n")
        input()
        print(e)


@retry
def get_docket(docket, caseCourt):
    """ 
    Takes in a docket number and the name of the court the docket is in as arguments and returns all the JSON data available from Docket Alarm.
    """

    # We create a user object from the /sav/credentials.pickle file so we can access the username and password from its attributes.
    user = login.Credentials()

    # The endpoint we will be connecting to. Calls to this endpoint return the json data for the docket we want.
    getdocket_url = "https://www.docketalarm.com/api/v1/getdocket/"

    # The parameters we pass to the endpoint. This is how the API knows how to find what we are looking for.
    data = {
        # The token generated after logging in.
        'login_token': user.authenticate(),
        # The reason for use
        'client_matter': user.client_matter,
        # The court we want to search.
        'court': caseCourt,
        # The docket number we want data for
        'docket':docket,
        # A boolean representing whether or not we want the cached version of the data.
        'cached': config.isCached,
        # Cleans up names
        'normalize':True,
    }

    headers = {'Content-Type':'application/x-www-form-urlencoded'}

    # Makes the api call. We specify the endpoint and the parameters as arguments. The results of the API call are returned and
    # stored to a variable. 
    result = requests.get(getdocket_url, data, timeout=30, headers=headers)
    
    # We use .json() to convert the json results to a python dictionary we can more easily work with.
    result_json = result.json()
    try:
        result_json = result.json()
    except:
        result_json = None
    return result_json

# This function is no longer used and only suits a very specific use case.
def format_case_number(unformatted_case_number):
    """ 
    Trims off excess data from the case numbers
    provided, and returns the same number in a
    form that Docket Alarm can search for.
    """

    # Takes in a regular expression as the first argument and the string you
    # want to search through as the second argument. returns a list, where
    # index 0 is the whole string, and index 1 is the part captured
    # in the parentheses of the regex
    regex = re.search(r"^\d\d-(\d\d\d\d-CF-\d+)-?", unformatted_case_number)
    result = regex[1]
    return result

def loop_dataframe():
    """ 
    loops through the spreadsheet listed in the global variable toward the top of
    this script. Returns docket info from each.
    """
    progress = 0 #DEV

    # Gets the path to the input csv that the user specified in the menu.
    spreadsheet_path = global_variables.CSV_INPUT_PATH

    main.clear()

    # Prints the ascii art from the welcome page.
    print(main.msg)

    # We turn the csv in our current directory into a DataFrame object. This is
    # an object representing tabular data that can comfortably be manipulated and
    # accessed in python.
    try:
        df = pd.read_csv(spreadsheet_path)
        len_df = len(df)
        # We declare a new variable that represents the amount of rows in the DataFrame.
        # We use this when we add our loading bar, to tell it what the max number of
        # loops is.
    except Exception:
        print("[ERROR] Input CSV file not found. Check to make sure the file is present and the filename matches the name specified in config/config.py\nThe default filename is 'input.csv' and it should be placed in the 'csv' folder.\nAlso, ensure all dependencies are installed.\nDependencies are listed in docs/requirements.txt\nReference documentation for more information.")
        input()

    # Here we display the loading bar on the console.
    bar = IncrementalBar('Downloading JSON Data', max=len_df)

    # We loops through each row in the pandas dataframe
    for index, row in df.iterrows():

        progress += 1 #DEV

        if config.isGUI == True:
            sg.one_line_progress_meter("Downloading JSON", progress + 1, len_df, "progbar2")

        # During each run through the loop, we grab the values from each column and
        # save them to variables.
        caseName = row[0]
        caseNo = row[1]
        caseCourt = row[2]
        
        # Here we set up the logic to specify if we want to format the case numbers or not.
        # Config.py has a 'formatCaseNos' variable set to a boolean. If it's True, we
        # run the case numbers through a regular expression. If False, it runs the script
        # on the case numbers provided as is.
        if config.formatCaseNos == True:
            caseNo = format_case_number(caseNo)
        elif config.formatCaseNos == False:
            caseNo = row[1].strip()
        else:
            # If for some reason the 'formatCaseNos' variable is not set, we default on the
            # case numbers provided in the spreadsheet.
            caseNo = caseNo

        #We run get_docket() on each docket number in the loop, which returns the dictionary
        # of that individual docket's json data. We save it to a variable.
        docket = get_docket(caseNo, caseCourt)

        # We save the json files and set their individual filenames to be the last name of the
        # party followed by the docket number

        write_to_json_file(f"{caseName} {caseNo}", docket)

        # With each loop, the progress bar moves forward.
        bar.next()

    # Forces the progress bar to 100%
    bar.finish()
    try:
        # When the json files are finished downloading, we open the output folder in the file explorer.
        os.startfile(global_variables.JSON_INPUT_OUTPUT_PATH)
    except Exception:
        # In case the users OS doesn't support this feature, we except any errors.
        pass  


def table_to_list_of_tuples():
    spreadsheet_path = global_variables.CSV_INPUT_PATH
    JSON_INPUT_OUTPUT_PATH = global_variables.JSON_INPUT_OUTPUT_PATH
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
        row_tuple = (caseName, caseNo, caseCourt, JSON_INPUT_OUTPUT_PATH)
        output_list_of_tuples.append(row_tuple)
    
    return output_list_of_tuples

@retry
def download_json_from_list_of_tuples(result_tuple):

    caseName, caseNo, caseCourt, JSON_INPUT_OUTPUT_PATH = result_tuple

    user = login.Credentials()

    # The endpoint we will be connecting to. Calls to this endpoint return the json data for the docket we want.
    getdocket_url = "https://www.docketalarm.com/api/v1/getdocket/"

    # The parameters we pass to the endpoint. This is how the API knows how to find what we are looking for.
    data = {
        # The token generated after logging in.
        'login_token': user.authenticate(),
        # The reason for use
        'client_matter': user.client_matter,
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