# Built-in Modules
import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
# Third-party Modules
from colorama import init, Fore, Back, Style
# Internal Modules
import get_json, get_pdfs, login, menus, file_browser, global_variables, fetch_updated_court_list
import config
import gui

# Inititalizes Colorama functionality, allowing us to write text to the terminal in different colors.
init()

CURRENT_DIR = os.path.dirname(__file__)

msg = Fore.YELLOW + """
  _____             _        _              _                                 _____ _____ 
 |  __ \           | |      | |       /\   | |                          /\   |  __ \_   _|
 | |  | | ___   ___| | _____| |_     /  \  | | __ _ _ __ _ __ ___      /  \  | |__) || |  
 | |  | |/ _ \ / __| |/ / _ \ __|   / /\ \ | |/ _` | '__| '_ ` _ \    / /\ \ |  ___/ | |  
 | |__| | (_) | (__|   <  __/ |_   / ____ \| | (_| | |  | | | | | |  / ____ \| |    _| |_ 
 |_____/ \___/_\___|_|\_\___|\__| /_/    \_\_|\__,_|_|  |_| |_| |_| /_/    \_\_|   |_____|
 |  _ \      | | |    |  __ \                    | |               | |                    
 | |_) |_   _| | | __ | |  | | _____      ___ __ | | ___   __ _  __| |                    
 |  _ <| | | | | |/ / | |  | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |                    
 | |_) | |_| | |   <  | |__| | (_) \ V  V /| | | | | (_) | (_| | (_| |                    
 |____/ \__,_|_|_|\_\ |_____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|                    
                                                                                          
"""

feesNotice = """
[Document Fees]

Courts may charge a fee to access certain documents. Docket Alarm passes their fee on
without markup. After the first access, later access does not incur a fee.
Contact Docket Alarm Support for information on specific fees associated with
particular courts.

Press ENTER to continue. 
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
    print(feesNotice)
    input()
    clear()

    # Checks to see if the account information was stored on the local machine previously
    if not os.path.isfile(os.path.join(CURRENT_DIR, "sav", "credentials.pickle")):

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

[4] More options.

Enter your response below.[1/2/3/4]
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
            clear()
            menus.specify_client_matter_menu()
            print(msg)
            get_json_and_pdfs()
        # Choice 2 is donwloading only JSON files.
        elif userChoice == "2":
            clear()
            menus.select_paths_menu(pdfOption=False)
            menus.specify_client_matter_menu()
            print(msg)
            get_json.thread_download_json()
        # Choice 3 is downloading only PDF files.
        elif userChoice == "3":
            clear()
            menus.select_paths_menu()
            menus.specify_client_matter_menu()
            print(msg)
            link_list = get_pdfs.get_urls("json-output")

            # get_pdfs.multiprocess_download_pdfs(link_list)
            get_pdfs.thread_download_pdfs(link_list)
        elif userChoice == "4":
            clear()
            menus.other_options_menu()

        # If the user enters anything other than a valid choice, then it tells them their choice is invalid and
        # restarts this function, prompting them to make a choice again.
        else:
            print("Please Enter Valid input (1, 2 or 3)")
            return handle_input()

    handle_input()
    try:
        os.startfile(os.path.join(CURRENT_DIR, "log"))
    except:
        pass
        
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

def select_paths_menu(pdfOption=True):
    """
    This displays a menu to the user allowing them to choose file paths to save their downloaded data to.
    It handles their choices and changes the global variables representing the file paths for saving.
    """
    print("Below are the current settings for finding and saving files:\n")
    print(f"[1] The CSV file filled with docket numbers is located at:\n{os.path.abspath(global_variables.CSV_INPUT_PATH)}\n")
    print(f"[2] JSON Files are saved to and retrieved from:\n{os.path.abspath(global_variables.JSON_INPUT_OUTPUT_PATH)}\n")
    if pdfOption == True:
        print(f"[3] PDF Files are saved to:\n{os.path.abspath(global_variables.PDF_OUTPUT_PATH)}\n")
    print("To change these paths. Type the number for the path you want to change and press ENTER.\n")
    print(Fore.RED + "[WARNING] A lot of files can be generated in the PDF and JSON directories you choose! Choose carefully!\n" + Style.RESET_ALL)
    if global_variables.IS_CACHED == False:
        print(Fore.RED + "[WARNING] You are making an UNCACHED search that may result in extra charges. Restart the program to make a CACHED search.\n" + Style.RESET_ALL)
    print("If you are happy with the current selection, simply press ENTER.\n")

    # Prompts the user for a choice and saves it in a variable.
    userChoice = input()

    # Choice 1 is to edit the path to the input csv full of docket numbers.
    if userChoice == "1":
        print("Select the path of your input csv file.")
        print("Press ENTER to open the file browser.")
        input()
        
        # Opens the file browser and returns the path to the file that the user selected.
        csvChoice = file_browser.browseCSVFiles()

        # We store this choice to a global variable to be used elsewhere in the script where
        # we need to access this choice.
        global_variables.CSV_INPUT_PATH = csvChoice

        clear()

        # Reloads path select menu, relflecting any changes.
        select_paths_menu()

    # Choice 2 is to edit the path to the json files.
    if userChoice == "2":
        print("Select the path where you would like to store your JSON files.")
        print("Press ENTER to open the file browser.")
        input()

        # Stores the users choice in a variable
        jsonChoice = file_browser.browseDirectories('json-output')

        # Stores the choice to a global variable so this choice can be used throughout this script,
        # not only in the context of this file.
        global_variables.JSON_INPUT_OUTPUT_PATH = jsonChoice

        clear()
        # Reloads path select menu, relflecting any changes.
        select_paths_menu()

    # Choice 3 is to edit the path where the folders full of PDF files will be saved.
    if userChoice == "3":
        print("Select the path where you would like to store your PDF files.")
        print("Press ENTER to open the file browser.")
        input()

        # Opens a file explorer and returns the path to the directory the user selected as a string.
        pdfChoice = file_browser.browseDirectories('pdf-output')

        # Saves the chosen file path to a global variable so it can be accessed elsewhere in the script when
        # we need to access this path.
        global_variables.PDF_OUTPUT_PATH = pdfChoice

        clear()
        # Reloads path select menu, relflecting any changes.
        select_paths_menu()

    # If the user doesnt make a choice and just presses ENTER, the program exits this menu and moves forward
    else:
        clear()

def other_options_menu():
    other_options = """
Type in one of the following numbers and press ENTER to specify your choice:

[0] Return to menu.

[1] Fetch updated list of compatible courts.
    (You use these names in your input CSV.                                          )
    (The list is always being updated and changes are not immediately added to Github)

[2] Log Out of Docket Alarm.

[3] Uncached Search

Enter your response below.[0/1/2/3]
    """
    print(other_options)
    userChoice = input()
    if userChoice == "0":
        clear()
        welcome()
    elif userChoice == "1":
        clear()
        print("Fetching updated court list...")
        fetch_updated_court_list.fetch_updated_court_list()
        print("Done.")
        input()
        welcome()
    elif userChoice == "2":
        clear()
        user = login.Credentials()
        print("\nAre you sure you want to log out of Docket Alarm?[Y/n]")
        userChoice = input()
        if userChoice.upper() == "Y":
            user.logout()
            clear()
            welcome()
        else:
            clear()
            other_options_menu()
    elif userChoice == "3":
        clear()
        print("\nUncached searches retrieve more up-to-date results but may result in extra charges.\nWould you like to turn uncached search on?[Y/n]\n")
        userChoice = input()
        if userChoice.upper() == "Y":
            clear()
            global_variables.IS_CACHED = False
            print("\nUncached search is ON and will remain ON until the program is closed.")
            print("\nPress ENTER to return to the menu.")
            input()
            welcome()
        elif userChoice.upper() == "N":
            clear()
            other_options_menu()
        else:
            print("Invalid choice entered.\nPress ENTER to return to menu.")
            input()
            clear()
            other_options_menu()
            

            
    else:
        print("Please Enter Valid input (0, 1 or 2)")

def specify_client_matter_menu():
    clear()
    print("Please enter the client or matter code used to bill this search. Max length is 50 characters.\n(If unsure or not applicable, leave blank and press ENTER.)")
    user_input = input()
    global_variables.CLIENT_MATTER = user_input
    clear()
    return

