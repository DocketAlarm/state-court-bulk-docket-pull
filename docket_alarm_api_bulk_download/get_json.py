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
import config
import login, file_browser, global_variables
import gui #DEV
import PySimpleGUI as sg
import user_tools
import get_pdfs

CURRENT_DIR = os.path.dirname(__file__)

# Reinforces that the variables defined in the global_variables module, and then edited from within other modules,
# continue to have the value that the user changed it to.
# It may look redundant, but without this line, the script only uses the default variable, without reflecting changes.

global_variables.JSON_INPUT_OUTPUT_PATH = global_variables.JSON_INPUT_OUTPUT_PATH
global_variables.CLIENT_MATTER = global_variables.CLIENT_MATTER

# We create an instance of a lock object. We use this later when we download json with threads, to ensure that no 
# two threads try to access data in the same place at the same time, causing problems.
lock = threading.Lock()


def table_to_list_of_tuples():
    """
    Grabs the csv from the CSV_INPUT_PATH variable that the user specified in the main menu,
    and returns a list of tuples. Each tuple in the list is a set of arguments ready to be passed to
    the download_json_from_list_of_tuples() function within the thread_download_json() function
    that wraps both of these funtions to use threading to download more quickly.
    """

    # The path to the input spreadsheet is the path that the user specified in the main menu.
    spreadsheet_path = global_variables.CSV_INPUT_PATH

    # The path where the JSON files will be downloaded to is the path that the user specified in the main menu.
    JSON_INPUT_OUTPUT_PATH = global_variables.JSON_INPUT_OUTPUT_PATH

    # The client matter is the string that the user specified in the main menu.
    CLIENT_MATTER = global_variables.CLIENT_MATTER

    IS_CACHED = global_variables.IS_CACHED

    # This list starts out empty, gets a tuple appended to it with every iteration of the loop below, and will eventually
    # be the value returned by this function.
    output_list_of_tuples = []

    try:
        # We try to open the csv as a pandas dataframe. Pandas dataframes make working with tabular data in python faster and easier.
        df = pd.read_csv(spreadsheet_path)

    except Exception as e:
        # If there are any errors with opening the dataframe, we print the data to the console to alert the user.
        print(f"{e}")
        input()
    
    # We loop through every row of the input spreadsheet, the row value allows us to access each value in each row through indexing.
    for index, row in df.iterrows():
        # We use indexing to store each value in the appropriate variables so they are more human-readable.
        caseName = row[0]
        caseNo = row[1]
        caseCourt = row[2]
        # We place the values into a tuple that will serve as parameters for download_json_from_list_of_tuples()
        # when we call it inside the thread_download_json() wrapper.
        row_tuple = (caseName, caseNo, caseCourt, JSON_INPUT_OUTPUT_PATH, CLIENT_MATTER, IS_CACHED)
        # We append each tuple to the list at the top of the function.
        output_list_of_tuples.append(row_tuple)
    # We return the list after it is populated with tuples during each iteration over every row in the spreadsheet.
    return output_list_of_tuples

@retry
def download_json_from_list_of_tuples(result_tuple):
    """
    This function takes in a tuple with 5 arguments as strings in order:
    The case name,
    The case number,
    The court the case is in,
    The output path for the download,
    The client matter (The reason for making the call, for billing purposes).
    It downloads json data for each case.
    This function is not called on its own, it is wrapped by the 
    thread_download_json() function, which allows each call of the function to be done in it's
    own thread, speeding up the download.
    """

    # We unpack the tuple and assign all of it's values to human-readable variable names.
    caseName, caseNo, caseCourt, JSON_INPUT_OUTPUT_PATH, CLIENT_MATTER, IS_CACHED = result_tuple

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
        'cached': IS_CACHED,
        # Cleans up names
        'normalize':True,
    }

    # Makes the api call. We specify the endpoint and the parameters as arguments. The results of the API call are returned and
    # stored to a variable. 


    # result = requests.get(getdocket_url, data)

    

    try:
        # if the api call fails, a detailed error is thrown. The script does not stop and the error message is not immediately shown to the user.
        # result.raise_for_status() 
        myDocket = user_tools.Docket((user.username, user.password), caseNo, caseCourt, client_matter=CLIENT_MATTER, cached=IS_CACHED, normalize=True)
        result_json = myDocket.all
    except Exception as error:
        # Rather, the error is written to log/log.txt with a timestamp and information about which case could not be downloaded.
        result_json = None
        timeNow = datetime.datetime.now().strftime("%I:%M%p %B %d, %Y")
        with open(os.path.join(CURRENT_DIR, 'log', 'log.txt'), 'a') as errorlog:
            errorlog.write(f"\n{timeNow}\n")
            errorlog.write("JSON could not be downloaded:\n")
            errorlog.write(f"{caseName}, {caseNo}, {caseCourt}\n")
            errorlog.write(f"{error}\n")
            errorlog.write("------------------")
        return

    # result_json = result.json()


    # We use .json() to convert the json results to a python dictionary we can more easily work with.

    # If there was a problem with the json data retrieved, and it's been written to the error log, do not write it.
    # Exits the function.
    if result_json.get('success', False) == False:
        timeNow = datetime.datetime.now().strftime("%I:%M%p %B %d, %Y")
        with open(os.path.join(CURRENT_DIR, 'log', 'log.txt'), 'a') as errorlog:
            errorlog.write(f"\n{timeNow}\n")
            errorlog.write("JSON could not be downloaded:\n")
            errorlog.write(f"{result_json}: {caseName}, {caseNo}, {caseCourt}\n")
            errorlog.write("------------------")
        return
    
    try:
        # Creates the path where our .json file will be saved to
        filePathNameWExt = os.path.join(JSON_INPUT_OUTPUT_PATH, f"{get_pdfs.cleanhtml(caseName)} {get_pdfs.cleanhtml(caseNo)}" + '.json')


        # We use a lock so this code won't be executed by multiple threads simultaneously, this way we don't get errors.
        with lock:
            # When 'opening' a file that doesn't yet exist, we create that file.
            # Here, we create the json file we'll be saving the data to.
            with open(filePathNameWExt, 'w') as fp:

                # Then we write the data to the newly created .json file.
                json.dump(result_json,fp, indent=3)

    # If the api call was successful, but the writing of the data to a file fails, we display the error message to the user.
    except Exception as e:
        print("\nError writing json file.\nReference the documentation for more information\n")
        input()
        print(e)
    return

def thread_download_json():
    """
    Wrapper function for download_json_from_list_of_tuples
    and table_to_list_of_tuples().
    table_to_list_of_tuples() is called, and it's return values are stored in a variable and passed as arguments
    to individual calls of download_json_from_list_of_tuples() within individual threads, speeding up the download.
    """

    # We call table_to_list_of_tuples() and store the results in a variable.
    tuples_from_table = table_to_list_of_tuples()
    # We get the amount of iterations the program will make, this will be used to tell the loading bar when it will be done.
    maximum = len(tuples_from_table)
    print("Downloading JSON files...")
    # We start a counter, so at the end we can calculate how long the downloads took.
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor:
    # We start concurrent.futures to have every line of code within the block get passed to its own sepreate thread.
        results = list(tqdm(executor.map(download_json_from_list_of_tuples, tuples_from_table), total=maximum))
        # We use executor.map to use threading, it takes the function and a list of arguments to pass as arguments.
        # tdqm starts a progress bar, and we specify the max value it needs to reach to finish.
    # We store the time again when it is over.
    finish = time.perf_counter()
    # We subtract the start time from the finish time to let the user know how long the download took.
    print(f"Finished downloading JSON files in {round(finish-start)} seconds.")
    try:
        # If the users operating system permits, we open the download directory where the desired output files were downloaded to.
        os.startfile(global_variables.JSON_INPUT_OUTPUT_PATH)
    except:
        pass
        
    return results