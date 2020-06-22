msg = """
 __  ___      ___  ___       
/__`  |   /\   |  |__        
.__/  |  /~~\  |  |___       
                             
 __   __        __  ___      
/  ` /  \ |  | |__)  |       
\__, \__/ \__/ |  \  |       
                             
 __                          
|__) |  | |    |__/          
|__) \__/ |___ |  \          
                             
 __   __   __        ___ ___ 
|  \ /  \ /  ` |__/ |__   |  
|__/ \__/ \__, |  \ |___  |  
                             
 __                          
|__) |  | |    |             
|    \__/ |___ |___          
                             
"""
print(msg)
input("Press any key to continue")




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
from progress.bar import ShadyBar

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
import auth


# These are your global variables. They are important to change if you want
# to repurpose this code to make API calls based on a different spreadsheet,
# or if you want to search within a different court.
court = "Florida State, Duval County, Fourth Circuit Court"
spreadsheet = "death-penalty-project.csv"
isCached = False

def writeToJSONFile(folder, fileName, data):
    """ takes in the name of a folder in the current directory, the name of
        the file you want to create, and the json object you want to write to
        the file.
    """ 
    filePathNameWExt = os.path.join( os.getcwd(), folder, fileName + '.json')
    with open(filePathNameWExt, 'w') as fp:
        json.dump(data,fp)

def authenticate():
    """Returns the authentication token to make API calls.
       Make sure that auth.py is filled out!
    """

    login_url = "https://www.docketalarm.com/api/v1/login/"


    data = {
        'username':auth.username,
        'password':auth.password,
        }

    result = requests.post(login_url, data=data)


    result_json = result.json()

    login_token = result_json['login_token']

    return login_token


def list_courts():
    """Prints all the courts to the console and returns a list of courts
    """
    searchdirect_url = "https://www.docketalarm.com/api/v1/searchdirect/"

    data = {
        'login_token':authenticate(),
        'client_matter':auth.client_matter,
    }

    result = requests.get(searchdirect_url, data)



    result_json = result.json()

    courts = result_json['courts']

    # for court in courts:
    #     print(court + "\n")

    return courts


def get_parameters():
    """Returns all of the parameters you can use when making a post 
        request to the /searchdirect endpoint
    """
    searchdirect_url = "https://www.docketalarm.com/api/v1/searchdirect/"

    court = court

    data = {
        'login_token':authenticate(),
        'client_matter':auth.client_matter,
        'court':court
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
        'client_matter':auth.client_matter,
        'party_name':party_name,
        'docketnum':docketnum,
        'court':court,
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
""" Takes in a docket number as an argument and returns all the JSON data
    available from Docket Alarm."""
    getdocket_url = "https://www.docketalarm.com/api/v1/getdocket/"

    data = {
        'login_token':authenticate(),
        'client_matter':auth.client_matter,
        'court':court,
        'docket':docket,
        'cached': isCached,
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
    regex = re.search(r"^\d\d-(\d\d\d\d-CF-\d+)-?", unformatted_case_number)
    result = regex[1]
    return result

def loop_dataframe():
    """ loops through the spreadsheet listed in the global variable toward the top of
        this script. Returns docket info from each."""
    df = pd.read_csv(spreadsheet)
    len_df = len(df)
    bar = ShadyBar('Processing', max=len_df)
    for index, row in df.iterrows():
        lastName = row[0]
        firstName = row[1]
        county = row[5]
        caseNo = row[6]
        
        formatted_caseNo = format_case_number(caseNo)

        docket = get_docket(formatted_caseNo)
        writeToJSONFile('result', f"{lastName} {formatted_caseNo}", docket)
        bar.next()
    bar.finish()    


loop_dataframe()