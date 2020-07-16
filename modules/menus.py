# Built In Modules
import os
# Internal Modules
from modules import global_variables, file_browser, fetch_updated_court_list, login
import main


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

        main.clear()

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

        main.clear()
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

        main.clear()
        # Reloads path select menu, relflecting any changes.
        select_paths_menu()

    # If the user doesnt make a choice and just presses ENTER, the program exits this menu and moves forward
    else:
        main.clear()

def other_options_menu():
    other_options = """
Type in one of the following numbers and press ENTER to specify your choice:

[0] Return to main menu.

[1] Fetch updated list of compatible courts.
    (You use these names in your input CSV.                                          )
    (The list is always being updated and changes are not immediately added to Github)

[2] Log Out of Docket Alarm.

Enter your response below.[0/1/2]
    """
    print(other_options)
    userChoice = input()
    if userChoice == "0":
        main.clear()
        main.welcome()
    elif userChoice == "1":
        main.clear()
        print("Fetching updated court list...")
        fetch_updated_court_list.fetch_updated_court_list()
        print("Done.")
        input()
        main.welcome()
    elif userChoice == "2":
        main.clear()
        user = login.Credentials()
        print("\nAre you sure you want to log out of Docket Alarm?[Y/n]")
        userChoice = input()
        if userChoice.upper() == "Y":
            user.logout()
            main.clear()
            login.login_interface()
        else:
            main.clear()
            other_options_menu()
    else:
        print("Please Enter Valid input (0, 1 or 2)")


