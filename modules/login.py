# Built-in Modules
import pickle
import os
# Third-party Modules
import stdiomask
# Internal Modules
import main
import requests

def store_user_info_locally(username, password, client_matter=""):
    """
    Takes in 3 strings as arguments, a username, a password, and the client matter.
    Saves them as a dictionary in a .pickle file in the 'sav' folder to be used later.
    This is so the user can avoid logging in every time they run the script
    """

    # We store the arguments in a dictionary with proper keys to access them later in the script.
    credentials_dict = {
        'username':username,
        'password':password,
        'client_matter': client_matter,
    }

    # We choose a file location to save the dictionary to.
    output_path = os.path.join("sav", "credentials.pickle")
    # We open a .pickle file to save the dictionary in, which can store python variables to be accessed later.
    # This allows the program to not have to ask the user to log in every time they use the script.
    pickle_out = open(output_path, "wb")

    # We write the dictionary to the pickle file at sav/credentials.pickle
    pickle.dump(credentials_dict, pickle_out)

    # When we are done writing to the file, we close it.
    pickle_out.close()

class Credentials:
    # The allows us to create a Credentials object.
    # We can reference the username, password, and client_matter attributes to get the information we need about the user
    # elsewhere in the script.

    # This is the code that is run when we initialize a new instance of this object
    def __init__(self):
        # We get the path to the .pickle file the user credentials information is stored in.
        input_path = os.path.join("sav", "credentials.pickle")
        # We open it up...
        pickle_in = open(input_path, "rb")
        # We store the dictionary inside of it to a variable...
        credentials_dict = pickle.load(pickle_in)
        # And we close the file when we're done making changes.
        pickle_in.close()
        # by setting the below attributes, we can reference the username by calling credentials_object.username, and so on.
        self.username = credentials_dict['username']
        self.password = credentials_dict['password']
        self.client_matter = credentials_dict['client_matter']

    def authenticate(self):
        # """Returns the authentication token to make API calls. Make sure that auth.py is filled out!"""
        # This is the endpoint for logging in to Docket Alarm from the API.
        login_url = "https://www.docketalarm.com/api/v1/login/"

        # The data we will send to the endpoint with our post request will be
        # our Docket Alarm username and password.
        data = {
            'username': self.username,
            'password': self.password,
            'client_matter': self.client_matter,
            }

        # We save the response to a variable. The response is a json object containing
        # our authentication key iside the json key named 'login_token'
        result = requests.post(login_url, data=data)

        result.raise_for_status()
        # Calling the .json() method on the result turns it into a python dictionary we
        # can work with natively.
        result_json = result.json()

        # We go into the 'login_token' key in our dictionary. The value we save here to
        # this variable is our authentication key.
        login_token = result_json['login_token']

        # We have the function return the key so this function can be called wherever we need
        # the key.
        return login_token

def login_interface():
    """
    Called to display menus and options for logging in
    """
    print("\nPlease enter your Docket Alarm username and press ENTER.\n")
    input_username = input()
    main.clear()
    print("\nPlease enter your Docket Alarm password and press ENTER\n(This will be stored securely on your local machine)\n")
    input_password = stdiomask.getpass(mask="*", prompt="")
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
    # Checks to see if the login was a success...
    if result_json['success'] != True:
        # If it was not a sucess, we let the user know...
        print(result_json['error'])
        input()
        # And prompt the user to log in again.
        login_interface()
    else:
        # If the login is a success, we store the user info in a pickle file to be accessed later.
        # That way, the program can log in automatically every time the script is run afterwards.
        store_user_info_locally(input_username, input_password, input_client_matter)


    
    

