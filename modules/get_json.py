from config import config
from config import auth


# Module for working with tabular data like csv and excel files.
import pandas as pd

# Module for sending HTTP requests and accessing repsonse data.
import requests

# Module for working with regular expressions. Used for searching through
# strings, trimming them, and extracting data from them.
import re

# Module for working with json data.
import json

# Module for working with parts of the computer system. Here we use it to
# access the results folder where our end result JSON files will go.
import os

# Module for creating visual loading bars. These are purely cosmetic
from progress.bar import IncrementalBar

# Module for adding retry functionality to most pieces of code that may
# throw errors.
from retrying import retry


# This is a local module, found in the auth.py file in the same
# directory as this one. If you are accessing this file from the
# GitHub repository, then create an auth.py file in the same directory
# as this file. You will specify 3 variables for logging in:
# username, password, and client_matter.
# The username and password are the same username and password for
# your Docket Alarm account. client_matter is your use case.



# These are your global variables. They are important to change if you want
# to repurpose this code to make API calls based on a different spreadsheet,
# or if you want to search within a different court.

# court = "Florida State, Duval County, Fourth Circuit Court"
# spreadsheet = "death-penalty-project.csv"
# isCached = True

def write_to_json_file(folder, fileName, data):
    """ takes in the name of a folder in the current directory, the name of
        the file you want to create, and the json object you want to write to
        the file.
    """ 
    try:
        # Created the path where our .json file will be saved to
        # filePathNameWExt = os.path.join(config.cwd, folder, fileName + '.json')
        filePathNameWExt = os.path.join(folder, fileName + '.json')


        # When 'opening' a file that doesn't yet exist, we create that file.
        # Here, we create the json file we'll be saving the data to.
        with open(filePathNameWExt, 'w') as fp:

            # Then we write the data to the newly created .json file.
            json.dump(data,fp)
    
    except Exception as e:
        print("\nError writing json file. Make sure 'json-output' folder is present in the root directory of the program.\nReference the documentation for more information\n")
        input()
        print(e)

def authenticate():
    """Returns the authentication token to make API calls.
       Make sure that auth.py is filled out!
    """

    # This is the endpoint for logging in to Docket Alarm from the API.
    login_url = "https://www.docketalarm.com/api/v1/login/"

    # The data we will send to the endpoint with our post request will be
    # our Docket Alarm username and password.
    data = {
        'username':auth.username,
        'password':auth.password,
        }

    # We save the response to a variable. The response is a json object containing
    # our authentication key iside the json key named 'login_token'
    result = requests.post(login_url, data=data)

    # Calling the .json() method on the result turns it into a python dictionary we
    # can work with natively.
    result_json = result.json()

    if result_json['success'] != True:
        print("\n\nThere was an error authenticating your account.\nPlease check config/auth.py and make sure your Docket Alarm account info is there.\nReference the documentation for more information.\n")
        input()
        print(result_json['error'])

    # We go into the 'login_token' key in our dictionary. The value we save here to
    # this variable is our authentication key.
    login_token = result_json['login_token']

    # We have the function return the key so this function can be called wherever we need
    # the key.
    return login_token




@retry
def get_docket(docket, caseCourt):
    """ Takes in a docket number as an argument and returns all the JSON data available from Docket Alarm.
    """
    getdocket_url = "https://www.docketalarm.com/api/v1/getdocket/"

    data = {
        'login_token':authenticate(),
        'client_matter': auth.client_matter,
        'court': caseCourt,
        'docket':docket,
        'cached': config.isCached,
        'normalize':True,
    }

    result = requests.get(getdocket_url, data, timeout=30)
    

    result_json = result.json()
    try:
        result_json = result.json()
    except:
        result_json = None
    return result_json


def format_case_number(unformatted_case_number):
    """ Trims off excess data from the case numbers
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
    """ loops through the spreadsheet listed in the global variable toward the top of
        this script. Returns docket info from each."""



    # We turn the csv in our current directory into a DataFrame object. This is
    # an object representing tabular data that can comfortably be manipulated and
    # accessed in python.

    spreadsheet_path = os.path.join('csv', config.spreadsheet)

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

        # During each run through the loop, we grab the values from each column and
        # save them to variables.

        # lastName = row[0]
        # firstName = row[1]
        # county = row[5]
        # caseNo = row[6]

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
            caseNo = row[1]
        else:
            # If for some reason the 'formatCaseNos' variable is not set, we default on the
            # case numbers provided in the spreadsheet.
            caseNo = caseNo
        


        #We run get_docket() on each docket number in the loop, which returns the dictionary
        # of that individual docket's json data. We save it to a variable.
        docket = get_docket(caseNo, caseCourt)

        # We save the json files and set their individual filenames to be the last name of the
        # party followed by the docket number

        write_to_json_file('json-output', f"{caseName} {caseNo}", docket)

        # With each loop, the progress bar moves forward.
        bar.next()

    # Forces the progress bar to 100%
    bar.finish()
    try:
        os.startfile('json-output')
    except Exception:
        pass  

