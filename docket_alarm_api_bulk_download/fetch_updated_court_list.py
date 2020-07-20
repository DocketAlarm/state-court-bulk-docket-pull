import requests
import os
import login
import global_variables

CURRENT_DIR = os.path.dirname(__file__)

def fetch_updated_court_list():
    """
    Prints all the courts to the console and returns a list of courts
    """

    user = login.Credentials()

    # Sending a get request to the /searchdirect/ endpoint with only the login_token and
    # client matter will return a list of couthouses. This list is every court we can search,
    # with the name formatted in a way that we can send later when accessing the API for 
    # searching for dockets.
    searchdirect_url = "https://www.docketalarm.com/api/v1/searchdirect/"

    data = {
        'login_token':user.authenticate(),
        'client_matter': global_variables.CLIENT_MATTER,
    }

    # returns a json object
    result = requests.get(searchdirect_url, data)


    # We call the .json() method on the json object to turn it into a python dictionary
    result_json = result.json()

    # The list of courts is stored in the 'courts' key we assign to a variable here
    courts = result_json['courts']

    # Designates the file path where the new list of courts will be stored
    updated_courts_output_file = os.path.join(CURRENT_DIR,"docs", "updated-courts.txt")

    # Deletes an old copy of this file if one exists
    try:
        os.remove(updated_courts_output_file)
    except:
        pass

    # Loops through every court in the list
    for court in courts:
        # Opens the output txt file
        with open(updated_courts_output_file, "a") as txt:
            # And writes that court to the file, until all courts are written.
            txt.write(court + "\n")
    
    # Opens the new list of courts on the users desktop
    try:
        os.startfile(updated_courts_output_file)
    except:
        pass
        


    # The function call returns a list object with all the courts we can search with Docket Alarm
    return courts