from config import config
import requests

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

    for court in courts:
        print(court + "\n")
        with open("courts.txt", "a") as txt:
            txt.write(court + "\n")
        


    # The function call returns a list object with all the courts we can search with Docket Alarm
    return courts


def get_parameters():
    """Returns all of the parameters you can use when making a post 
        request to the /searchdirect endpoint
    """
    searchdirect_url = "https://www.docketalarm.com/api/v1/searchdirect/"

    data = {
        'login_token':authenticate(),
        'client_matter': config.client_matter,
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
        'client_matter':config.client_matter,
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


