from modules import get_json
from modules import get_pdfs
from tools import utilities
import os
from colorama import init, Fore, Back, Style
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
    clear()
    print(msg)
    print(Style.RESET_ALL)
    print("\n")
    print("Welcome!")
    input("Press ENTER key to begin!")
    clear()
    instructions = """
Instructions:

This program takes in a csv file full of docket numbers and will automatically
populate 2 folders with the raw JSON data and all of the PDF documents associated
with that docket.

Make sure to edit config.py and auth.py before running this program.
For more information, please visit the Github page for this project.

Press ENTER for options.

    """
    print(instructions)
    input()
    clear()

    options = """
Type in one of the following numbers and press ENTER to specify your choice:

[1] Get all JSON files and PDF files.

[2] Get JSON files only.

[3] Get PDF files only.
    ( Only select 3 if your 'json-output' folder already contains JSON )
    ( files for the cases you want PDFs for.                           )

Enter your response below.
    """
    print(options)

    def handle_input():
        userChoice = input()
        if userChoice == "1":
            clear()
            print(msg)
            get_json_and_pdfs()
        elif userChoice == "2":
            clear()
            print(msg)
            get_json.loop_dataframe()
        elif userChoice == "3":
            clear()
            print(msg)
            get_pdfs.download_pdfs()
        else:
            print("Please Enter Valid input (1, 2 or 3)")
            return handle_input()

    handle_input()

    print("\nDone.")
    input()



def get_json_and_pdfs():

    get_json.loop_dataframe()

    get_pdfs.download_pdfs()

    print("done")

if __name__ == '__main__':
    welcome()

else:
    pass