# Built-in Modules
from tools import utilities
import os
# Third-party Modules
from colorama import init, Fore, Back, Style
# Internal Modules
from modules import get_json, get_pdfs, login, menus, file_browser, global_variables
from config import config
import gui


# Inititalizes Colorama functionality, allowing us to write text to the terminal in different colors.
init()


msg = Fore.YELLOW + """
  _____             _        _              _                                 _____ _____ 
 |  __ \           | |      | |       /\   | |                          /\   |  __ \_   _|
 | |  | | ___   ___| | _____| |_     /  \  | | __ _ _ __ _ __ ___      /  \  | |__) || |  
 | |  | |/ _ \ / __| |/ / _ \ __|   / /\ \ | |/ _` | '__| '_ ` _ \    / /\ \ |  ___/ | |  
 | |__| | (_) | (__|   <  __/ |_   / ____ \| | (_| | |  | | | | | |  / ____ \| |    _| |_ 
 |_____/ \___/ \___|_|\_\___|\__|_/_/    \_\_|\__,_|_|  |_| |_| |_| /_/    \_\_|   |_____|
  / ____| |      | |        / ____|               | |                                     
 | (___ | |_ __ _| |_ ___  | |     ___  _   _ _ __| |_                                    
  \___ \| __/ _` | __/ _ \ | |    / _ \| | | | '__| __|                                   
  ____) | || (_| | ||  __/ | |___| (_) | |_| | |  | |_                                    
 |_____/ \__\__,_|\__\___|__\_____\___/ \__,_|_|  _\__| _____       _ _                   
 |  _ \      | | |    |  __ \           | |      | |   |  __ \     | | |                  
 | |_) |_   _| | | __ | |  | | ___   ___| | _____| |_  | |__) |   _| | |                  
 |  _ <| | | | | |/ / | |  | |/ _ \ / __| |/ / _ \ __| |  ___/ | | | | |                  
 | |_) | |_| | |   <  | |__| | (_) | (__|   <  __/ |_  | |   | |_| | | |                  
 |____/ \__,_|_|_|\_\ |_____/ \___/ \___|_|\_\___|\__| |_|    \__,_|_|_|                  
"""
def clear():
    """clears the terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def welcome():
    """
    The code that executes at launch. It guides the user through menus and starts other functions from the other folders
    based on the users choices.
    """
    clear()
    print(msg)
    print(Style.RESET_ALL)
    print("\n")
    print("Welcome!")
    input("Press ENTER key to begin!")
    clear()

    # Checks to see if the account information was stored on the local machine previously
    if not os.path.isfile(os.path.join("sav", "credentials.pickle")):

        # If the user hasn't successfullly logged in before, it takes them to a menu sequence to log in, and saves the info locally
        # for the next time the script is run.
        login.login_interface()

    
    user = login.Credentials()

    print(f"You are logged in as: {user.username}")
    instructions = """
Instructions:

This program takes in a csv file full of docket numbers and will automatically
populate 2 folders with the raw JSON data and all of the PDF documents associated
with that docket.

You will now select the path where your input csv is located.
Press ENTER to open the file browser.
    """
    print(instructions)
    input()
    clear()

    # Opens a graphical file browser and returns the path to the csv file that the user selected.
    csvChoice = file_browser.browseCSVFiles()

    # Assigns the choice to a global variable, so other modules can find the path that the user specified.
    global_variables.CSV_INPUT_PATH = csvChoice

    options = """
Type in one of the following numbers and press ENTER to specify your choice:

[1] Get all JSON files and PDF files.

[2] Get JSON files only.

[3] Get PDF files only.
    ( Only select 3 if you already have a directory full of JSON files. )
    ( The JSON files are needed to extract the download links from.     )

Enter your response below.
    """
    print(options)

    def handle_input():
        """
        Prompts the user for a choice and calls the function from the 'modules' folder that corresponds
        with that choice.
        """
        userChoice = input()

        # Choice 1 is downloading all json and pdf files.
        if userChoice == "1":
            clear()
            menus.select_paths_menu()
            print(msg)
            get_json_and_pdfs()
        # Choice 2 is donwloading only JSON files.
        elif userChoice == "2":
            clear()
            menus.select_paths_menu(pdfOption=False)
            print(msg)
            # get_json.loop_dataframe()
            get_json.thread_download_json()
        # Choice 3 is downloading only PDF files.
        elif userChoice == "3":
            clear()
            menus.select_paths_menu()
            print(msg)
            link_list = get_pdfs.get_urls("json-output")

            # get_pdfs.multiprocess_download_pdfs(link_list)
            get_pdfs.thread_download_pdfs(link_list) # development

        # If the user enters anything other than a valid choice, then it tells them their choice is invalid and
        # restarts this function, prompting them to make a choice again.
        else:
            print("Please Enter Valid input (1, 2 or 3)")
            return handle_input()

    handle_input()

    print("\nDone.")
    input()



def get_json_and_pdfs():
    """
    This function calls the function to download JSON first, immediately followed by the function to download
    PDFs. This is used when the user chooses the menu choice to download both.
    """

    # The function that downloads the JSON files
    # get_json.loop_dataframe()
    get_json.thread_download_json()

    # The function that extracts the proper arguments to pass to the function for downloading PDFs using multiprocessing.
    # That function requires a list of tuples, each tuple being a seperate set of arguments to pass.
    link_list = get_pdfs.get_urls("json-output")

    # This function uses threading on the function that downloads PDFs, allowing us to download multiple PDFs at once,
    # speeding up the process.
    get_pdfs.thread_download_pdfs(link_list)


# This code executes if this function is run directly, rather than being imported from elsewhere.
if __name__ == '__main__':
    if config.isGUI == False:
        # If isGUI is set to False in config/config.py, then the program will run in the command line when this file is executed.
        welcome()
    if config.isGUI == True:
        # If isGUI is set to True in config/config.py, Then the program will open with an experimental GUI. (This is not reccomended as of yet.)
        gui.gui_run()
