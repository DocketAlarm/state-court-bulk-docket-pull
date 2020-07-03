import pickle
import os
import main
import requests

def store_user_info_locally(username, password, client_matter=""):
    """
    Takes in 3 strings as arguments, a username, a password, and the client matter.
    Saves them as a dictionary in a .pickle file in the 'sav' folder to be used later.
    This is so the user can avoid logging in every time they run the script
    """
    credentials_dict = {
        'username':username,
        'password':password,
        'client_matter': client_matter,
    }

    output_path = os.path.join("sav", "credentials.pickle")
    pickle_out = open(output_path, "wb")
    pickle.dump(credentials_dict, pickle_out)

class Credentials:
    
    def __init__(self):
        input_path = os.path.join("sav", "credentials.pickle")
        pickle_in = open(input_path, "rb")
        credentials_dict = pickle.load(pickle_in)
        self.username = credentials_dict['username']
        self.password = credentials_dict['password']
        self.client_matter = credentials_dict['client_matter']

def login_interface():
    """
    Called to display menus and options for logging in
    """
    print("\nPlease enter your Docket Alarm username and press ENTER.\n")

    input_username = input()

    main.clear()

    print("\nPlease enter your Docket Alarm password and press ENTER\n(This will be stored securely on your local machine)\n")

    input_password = input()

    main.clear()

    print("\nIf applicable, please enter your client matter.\nIf unsure, leave blank and press ENTER\n")

    input_client_matter = input()

    main.clear()

    # This is the endpoint for logging in to Docket Alarm from the API.
    login_url = "https://www.docketalarm.com/api/v1/login/"

    # The data we will send to the endpoint with our post request will be
    # our Docket Alarm username and password.
    data = {
        'username':input_username,
        'password':input_password,
        'client_matter':input_client_matter,
        }

    # We save the response to a variable. The response is a json object containing
    # our authentication key iside the json key named 'login_token'
    result = requests.post(login_url, data=data)

    # Calling the .json() method on the result turns it into a python dictionary we
    # can work with natively.
    result_json = result.json()

    if result_json['success'] != True:
        print(result_json['error'])
        input()
        login_interface()
    else:
        store_user_info_locally(input_username, input_password, input_client_matter)

    
    

