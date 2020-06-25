import config
import auth


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
    # Created the path where our .json file will be saved to
    filePathNameWExt = os.path.join(config.cwd, folder, fileName + '.json')

    # When 'opening' a file that doesn't yet exist, we create that file.
    # Here, we create the json file we'll be saving the data to.
    with open(filePathNameWExt, 'w') as fp:

        # Then we write the data to the newly created .json file.
        json.dump(data,fp)

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

    # We go into the 'login_token' key in our dictionary. The value we save here to
    # this variable is our authentication key.
    login_token = result_json['login_token']

    # We have the function return the key so this function can be called wherever we need
    # the key.
    return login_token


def list_courts():
    """Prints all the courts to the console and returns a list of courts
    """

    # Sending a get request to the /searchdirect/ endpoint with only the login_token and
    # client matter will return a list of couthouses. This list is every court we can search,
    # with the name formatted in a way that we can send later when accessing the API for 
    # searching for dockets.
    searchdirect_url = "https://www.docketalarm.com/api/v1/searchdirect/"

    data = {
        'login_token':authenticate(),
        'client_matter': auth.client_matter,
    }

    # returns a json object
    result = requests.get(searchdirect_url, data)


    # We call the .json() method on the json object to turn it into a python dictionary
    result_json = result.json()

    # The list of courts is stored in the 'courts' key we assign to a variable here
    courts = result_json['courts']

    # Uncomment out the 2 lines below to have the courts print to the console when calling
    # this function

    # for court in courts:
    #     print(court + "\n")


    # The function call returns a list object with all the courts we can search with Docket Alarm
    return courts


def get_parameters():
    """Returns all of the parameters you can use when making a post 
        request to the /searchdirect endpoint
    """
    searchdirect_url = "https://www.docketalarm.com/api/v1/searchdirect/"

    data = {
        'login_token':authenticate(),
        'client_matter': client_matter,
        'court': config.court
    }

    result = requests.get(searchdirect_url, data)



    result_json = result.json()

    return result_json

def get_results(party_name, docketnum):
    """ Takes in the name of a party and the docket number as a parameter,
        returns the Docket Alarm search results. You can make calls to the
        /getdocket endpoint with these results to get more detailed information
        on the docket you are looking for.
    """
    searchdirect_url = "https://www.docketalarm.com/api/v1/searchdirect/"

    data = {
        'login_token':authenticate(),
        'client_matter':client_matter,
        'party_name':party_name,
        'docketnum':docketnum,
        'court': config.court,
        'case_type':'CF',

    }
    
    result = requests.post(searchdirect_url, data)

    result_json = result.json()

    search_results = None

    if result_json['success']:
        search_results = result_json['search_results']
    else:
        search_results = None
    

    # print(result_json)
    return search_results

@retry
def get_docket(docket):
    """ Takes in a docket number as an argument and returns all the JSON data available from Docket Alarm.
    """
    getdocket_url = "https://www.docketalarm.com/api/v1/getdocket/"

    data = {
        'login_token':authenticate(),
        'client_matter': auth.client_matter,
        'court': config.court,
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

    spreadsheet_path = os.path.join(config.cwd, config.spreadsheet)

    df = pd.read_csv(spreadsheet_path)

    # We declare a new variable that represents the amount of rows in the DataFrame.
    # We use this when we add our loading bar, to tell it what the max number of
    # loops is.
    len_df = len(df)

    # Here we display the loading bar on the console.
    bar = IncrementalBar('Downloading JSON Data', max=len_df)

    # We loops through each row in the pandas dataframe
    for index, row in df.iterrows():

        # During each run through the loop, we grab the values from each column and
        # save them to variables.
        lastName = row[0]
        firstName = row[1]
        county = row[5]
        caseNo = row[6]
        
        # We use our regular expression from earlier to change the format of the case number
        # into something Docket Alarm recognizes natively.
        formatted_caseNo = format_case_number(caseNo)

        #We run get_docket() on each docket number in the loop, which returns the dictionary
        # of that individual docket's json data. We save it to a variable.
        docket = get_docket(formatted_caseNo)

        # We save the json files and set their individual filenames to be the last name of the
        # party followed by the docket number

        write_to_json_file('json-output', f"{lastName} {formatted_caseNo}", docket)

        # With each loop, the progress bar moves forward.
        bar.next()

    # Forces the progress bar to 100%
    bar.finish()    

# Makes it so loop_dataframe() runs when this main.py file is ran
# loop_dataframe()