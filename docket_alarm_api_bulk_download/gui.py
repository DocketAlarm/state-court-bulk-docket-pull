import PySimpleGUI as sg
import global_variables
import get_pdfs
import get_json
import login
import os
import pandas as pd
import requests
import json

CURRENT_DIR = os.path.dirname(__file__)

# This function makes it so when the user selects file paths for the csv, json files, and pdf files,
# their choices will be saved to the global variables in modules/global_variables.py, that way these paths
# can be referenced from anywhere in the program.
def declare_globals(event, values):
    global_variables.CSV_INPUT_PATH = values['pathCSV']
    global_variables.JSON_INPUT_OUTPUT_PATH = values['pathJSON']
    global_variables.PDF_OUTPUT_PATH = values['pathPDF']
    print(f"CSV GLOBAL = {global_variables.CSV_INPUT_PATH}\nJSON GLOBAL = {global_variables.JSON_INPUT_OUTPUT_PATH}\nPDF GLOBAL = {global_variables.PDF_OUTPUT_PATH}")



# The first layout is the screen where you choose your paths and select what files you want to download.
layout = [
    [sg.Txt('Input CSV')],
    [sg.Input(os.path.abspath(os.path.join(CURRENT_DIR,"csv", "input.csv")),size=(50,1), key="pathCSV"), sg.FileBrowse("Browse", key="browseCSV", initial_folder="csv", file_types=(("CSV Files", "*.csv"),))],
    [sg.Txt('JSON Directory')],
    [sg.Input(os.path.abspath("json-output"),size=(50,1), key="pathJSON"), sg.FolderBrowse("Browse", key="browseJSON",initial_folder="json-output")],
    [sg.Txt('PDF Directory')],
    [sg.Input(os.path.abspath("pdf-output"),size=(50,1), key="pathPDF"), sg.FolderBrowse("Browse", key="browsePDF", initial_folder="pdf-output")],
    [sg.Button("Get JSON & PDFs", key="getJSON_PDF"), sg.Button("Get JSON", key="getJSON"), sg.Button("Get PDFs", key="getPDF")],
    [sg.Image("img/spinner.gif", key="spinner")]
]

# This layout is for the login screen and asks the user for their username, password, and client_matter.
loginLayout = [
    [sg.Txt("Log in to Docket Alarm")],
    [sg.Txt("Username:"), sg.Input(size=(50,1), key="username")],
    [sg.Txt("Password:"), sg.Input(size=(50,1), key="password")],
    [sg.Txt("Client Matter:"), sg.Input(size=(50,1), key="clientMatter")],
    [sg.Button("Submit", key="submit")]
]


# This code assigns the layout to their windows. This does not pull up the windows automatically.
# .read() must be called on these to open them. This merely selects the text in the window header for each
# window we might open in the program.
window = sg.Window('Bulk-Docket-Pull', layout)
loginWindow = sg.Window("Log In", loginLayout)


def display_login_window():
    """
    Displays the window to log in to Docket Alarm.
    Prompts the user for their username, password, and client matter.
    """
    while True:
        # Read() opens the window of our choice.
        # Event is the key for the button pressed. We can make logic around this to give buttons their abilities.
        # Values is a dictionary containing any information the user entered into the program.
        event, values = loginWindow.read()

        # An attempt at animating a loading spinner when PDFs are downloading.
        window.Element('spinner').UpdateAnimation("img/spinner.gif",  time_between_frames=50)

        # if the submit button in this window is pressed...
        if event == "submit":

            # We ready up the api endpoint for logging in to Docket Alarm...
            login_url = "https://www.docketalarm.com/api/v1/login/"

            # We ready up the parameters to send to the login endpoint, with the values the user specified...
            data = {
                'username':values['username'],
                'password':values['password'],
                'client_matter':values['clientMatter'],
                }

            # We send the parameters to the API endpoint, storing the resulting json data in a variable...
            result = requests.post(login_url, data=data)

            # We convert the json data from the result of the API call to a python dictionary, making it
            # easier to work with.
            result_json = result.json()

            # We check if the login is a success.
            # If it is not...
            if result_json['success'] != True:
                # We display a popup letting the user know, returning them back to the sign in form.
                sg.popup_error("Invalid Username or Password.")
            else:
                # If it is a success...
                # We save the login info locally to a pickle file so they won't have to log in again next time they use
                # the script.
                login.store_user_info_locally(values['username'], values['password'], values['clientMatter'])
                # We let them know their login was successful.
                sg.popup_ok("Login successful!")
                # We close the login window...
                loginWindow.close()
                # And bring the user to the main window, where they can select their paths, and choose which data to download.
                display_main_window()

def display_main_window():
    """
    Displays the main window of the program.
    This window prompts the user for the paths for their CSV, their PDF files, and their JSON files.
    """
    while True:
        # Read() opens the window of our choice.
        # Event is the key for the button pressed. We can make logic around this to give buttons their abilities.
        # Values is a dictionary containing any information the user entered into the program.
        event, values = window.read()
        print(event, values) # For debugging - Prints buttons pressed, and values returned to the console.
        # If the user selects the 'Get JSON & PDFs' button, we run the function that gets JSON and PDF files.
        if event == "getJSON_PDF":
            # Sets the path choices specified as the global variables that can be used throughout the whole program
            # to reference their choice.
            declare_globals(event, values)
            # Downloads JSON files and PDF files.
            main.get_json_and_pdfs()
        # If the user selects the 'Get JSON' button, we run the function that gets JSON files.
        if event == "getJSON":
            # Sets the path choices specified as the global variables that can be used throughout the whole program
            # to reference their choice.
            declare_globals(event, values)
            # Downloads JSON files.
            get_json.loop_dataframe()
        # If the user selects the 'Get PDFs' button, we run the function that gets the PDF files.
        # (JSON files must be downloaded first to use this option.)
        if event == "getPDF":
            # Sets the path choices specified as the global variables that can be used throughout the whole program
            # to reference their choice.
            declare_globals(event, values)
            # Gets all the links to PDF files from within the json files in the directory the user specified.
            # This is a list of tuples.
            link_list = get_pdfs.get_urls("json-output")
            # Downloads all of the PDF files. Takes the link list from above as an argument.
            get_pdfs.thread_download_pdfs(link_list)
        # If the user closes the window with the "X" in the corner...
        if event == sg.WIN_CLOSED:
            # Close the window.
            break

def gui_run():
    """
    Used for running the GUI.
    Checks to see if valid user login information is stored on the local machine.
    If it is not, it prompts the user to log in.
    If it is, it logs the user in and opens directly to the main window where the
    user can select their filepaths and what files they want to download.
    """
    # If there is no file stored locally containing valid login credentials...
    if not os.path.isfile(os.path.join(CURRENT_DIR, "sav", "credentials.pickle")):
        # Prompt the user to enter their login info.
        display_login_window()
    # If there is a file stored locally containing valid login credentials...
    else:
        # Bring the user to the main window of the program.
        display_main_window()
    
# If this file is run directly...    
if __name__ == "__main__":
    # Crunch the logic to see if the user has logged in successfully before,
    # and open the correct window for them.
    gui_run()