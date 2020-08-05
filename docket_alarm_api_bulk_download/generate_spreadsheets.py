# Built-in Modules
import datetime
import os
import re
# Third-party Modules
import pandas as pd
from progress.bar import Bar
from colorama import init, Fore, Back, Style
# Internal Modules
import user_tools
import login
import global_variables
import menus
from get_pdfs import cleanhtml


# We store the directory of this file in a variable so we can access it as needed.
CURRENT_DIR = os.path.dirname(__file__)

# This module is for creating csv files from a Docket Alarm search query

# Here we initialize our blank dataframes with their column headers. We append each of these throughout the script.
# Dataframes are tables that are easy to work with in python. They can be easily exported to a variety of formats.
docketInformation = pd.DataFrame(columns=['Docket Number', 'Court Name','Case Title', 'Case Info Field', 'Case Info Values'])
docketEntries = pd.DataFrame(columns=['Docket Number', 'Court Name','Case Title', 'Docket Entry Date', 'Docket Entry Numbers', 'Docket Entry Contents'])
parties = pd.DataFrame(columns=['Docket Number', 'Court Name','Case Title', 'Party Name', 'Party Type'])
attorneysAndFirms = pd.DataFrame(columns=['Docket Number', 'Court Name','Attorney Name', 'Attorney Firm', 'Attorney Email', 'Attorney Phone'])


# We create this function to remove the HTML tags from the docket entries returned by the API.
def removehtml(html_string):
    """
    Takes in a string that may contain HTML tags as an input.
    Returns the string with the tags replaced with spaces.
    """

    # Specifies a regular expression you want to isolate. Here, we isolate HTML tags.
    html_text = re.compile('<.*?>')

    # We replace the HTML tags with a space in our input.
    html_removed = re.sub(html_text, ' ', html_string)

    # We return the string with the HTML tags removed.
    return html_removed


def query_to_tables(query, results_limit, output_path, result_order=None, input_csv=None):
    """
    Takes in a search query as a sting,
    the amount of results you want returned as a string,
    the path you want to save to as a string,
    and optionally, the order of your results as a string.

    Generates a folder within the folder you specify and
    populates it with 4 spreadsheets containing the docket data
    from your search.
    """




    # We convert the amount of results the user wants to an integer so we can work with the number.
    if input_csv == None:
        results_limit = int(results_limit)

    def fill_docketInformation(result,docket):
        """
        This nested function populates the docketInformation dataframe.
        """
        if not 'info' in docket:
            return
        # We loop through all the keys present in the dockets info dictionary.
        for key in docket['info']:
            
            # We create the new row we want to add as a dictionary.
            # Using .get() allows us to specify the key that we want, and specify a default value as the second argument in
            # case the key doesn't exist.
            new_docketInformation_row = {
                'Docket Number':result['docket'],
                'Court Name':result['court'],
                'Case Title':docket['info'].get('title',result.get("title", None)),
                'Case Info Field':key,
                'Case Info Values': docket['info'][key],
            }

            # We append the global dataframe with the row we want represented as a dictionary. 
            # ignore_index=True specifies that we don't want to generate an index column.
            global docketInformation
            appender = docketInformation.append(new_docketInformation_row, ignore_index=True)

            # When we append a dataframe, the original is not changed, rather a new version of the dataframe with the added row is generated.
            # We replace the original with the new version so our changes get saved.
            docketInformation = appender


    def fill_docketEntries(result,docket):
        """
        This nested function populates the docketEntries dataframe.
        """

        # We loop through each dictionary within the docket_report list
        if not 'docket_report' in docket:
            print(docket)
            return

        for document in docket['docket_report']:

            # We create the new row we want to add as a dictionary.
            # Using .get() allows us to specify the key that we want, and specify a default value as the second argument in
            # case the key doesn't exist.
            new_docketEntries_row = {
                'Docket Number':result['docket'],
                'Court Name':result['court'],
                'Case Title':docket['info'].get('title',result.get("title", None)),
                'Docket Entry Date': document.get('entry_date', None),
                'Docket Entry Numbers': document.get('number', None),
                'Docket Entry Contents': removehtml(document.get('contents', None)),
            }

            # We append the global dataframe with the row we want represented as a dictionary. 
            # ignore_index=True specifies that we don't want to generate an index column.
            global docketEntries
            appender = docketEntries.append(new_docketEntries_row, ignore_index=True)

            # When we append a dataframe, the original is not changed, rather a new version of the dataframe with the added row is generated.
            # We replace the original with the new version so our changes get saved.
            docketEntries = appender


    def fill_parties(result,docket):
        """
        This nested function populates the parties dataframe.
        """

        # The parties key is not always present in our response.
        if not 'parties' in docket:
            # If it's not present, we don't add to the dataframe and we exit the function.
            print(docket)
            return

        for party in docket.get('parties', None):

            # We create the new row we want to add as a dictionary.
            # Using .get() allows us to specify the key that we want, and specify a default value as the second argument in
            # case the key doesn't exist.
            new_parties_row = {
            'Docket Number':result.get('docket', None),
            'Court Name': result.get('court', None),
            'Case Title': docket['info'].get('title', result.get("title", None)),
            'Party Name': party.get('name_normalized', party.get('name')),
            'Party Type': party.get('type', None),
            }


            # We append the global dataframe with the row we want represented as a dictionary. 
            # ignore_index=True specifies that we don't want to generate an index column.
            global parties
            appender = parties.append(new_parties_row, ignore_index=True)

            # When we append a dataframe, the original is not changed, rather a new version of the dataframe with the added row is generated.
            # We replace the original with the new version so our changes get saved.
            parties = appender

    def fill_attorneysAndFirms(result, docket):
        """
        This nested function populates the attorneysAndFirms dataframe.
        """

        # The parties key is not always present in our response.
        if not 'parties' in docket:
            # If it's not present, we don't add to the dataframe and we exit the function.
            return

        # We loop through each dictionary within the parties list of dictionaries.
        for party in docket['parties']:

            # The counsel key will not always be present in the dictionary.
            if not 'counsel' in party:
                # If it's not, we don't write to the dataframe and we exit the function.
                return
            for counsel in party['counsel']:

                # We create the new row we want to add as a dictionary.
                # Using .get() allows us to specify the key that we want, and specify a default value as the second argument in
                # case the key doesn't exist.
                new_attorneysAndFirms_row = {
                    'Docket Number': result.get('docket', None),
                    'Court Name': result.get('court', None),
                    'Attorney Name': counsel.get("name", None),
                    'Attorney Firm': counsel.get("firm", None),
                    'Attorney Email': counsel.get("email", None),
                    'Attorney Phone': counsel.get("phone", None),
                }

                # We append the global dataframe with the row we want represented as a dictionary. 
                # ignore_index=True specifies that we don't want to generate an index column.
                global attorneysAndFirms
                appender = attorneysAndFirms.append(new_attorneysAndFirms_row, ignore_index=True)

                # When we append a dataframe, the original is not changed, rather a new version of the dataframe with the added row is generated.
                # We replace the original with the new version so our changes get saved.
                attorneysAndFirms = appender
    
    if input_csv != None:
        # The path to the input spreadsheet is the path that the user specified in the main menu.

        # The path where the JSON files will be downloaded to is the path that the user specified in the main menu.
        JSON_INPUT_OUTPUT_PATH = global_variables.JSON_INPUT_OUTPUT_PATH

        # The client matter is the string that the user specified in the main menu.
        CLIENT_MATTER = global_variables.CLIENT_MATTER

        IS_CACHED = global_variables.IS_CACHED

        # This list starts out empty, gets a tuple appended to it with every iteration of the loop below, and will eventually
        # be the value returned by this function.
        output_list_of_tuples = []

        try:
            # We try to open the csv as a pandas dataframe. Pandas dataframes make working with tabular data in python faster and easier.
            df = pd.read_csv(input_csv)

        except Exception as e:
            # If there are any errors with opening the dataframe, we print the data to the console to alert the user.
            print(f"{e}")
            input()
        
        searchResults = []
        # We loop through every row of the input spreadsheet, the row value allows us to access each value in each row through indexing.
        searching_from_csv_bar = Bar("Reading CSV, Querying Docket Alarm...", max=df.shape[0])
        for index, row in df.iterrows():
            # We use indexing to store each value in the appropriate variables so they are more human-readable.
            caseName = row[0]
            caseNo = row[1]
            caseCourt = row[2]
            # We place the values into a tuple that will serve as parameters for download_json_from_list_of_tuples()
            # when we call it inside the thread_download_json() wrapper.

            query = f"is:docket court:({caseCourt}) docket:({caseNo})"
            user = login.Credentials()
            searchResult = user_tools.search_docket_alarm((user.username,user.password),query,limit=1, result_order=result_order)
            searchResults += searchResult
            searching_from_csv_bar.next()
        searching_from_csv_bar.finish()

    else:


        # After defining all of our nested functions, this is where the query_to_tables() function begins.

        # First we let the user know to wait, so they don't press any buttons that get entered as the input they will be prompted for when this is done loading.
        print("\n")
        print("Querying, please wait...")
        # We create our user object to log in. We can use attributes and methods to access the username, password, and authentication token of our currently signed in user.
        user = login.Credentials()


        

        # We run our search, using the query, the number of results, and the order that the user specified in the menu.
        searchResults = user_tools.search_docket_alarm((user.username,user.password),query,limit=results_limit, result_order=result_order)

        searchResults = searchResults[0:results_limit]

    

    # We let the user know how many results were returned for their search and ask them to confirm to proceed.
    print(f"\nThis search query resulted in {len(searchResults)} results. Proceed? [Y/n]")

    # We store their answer in a variable.
    user_proceed_choice = input()

    # If the user says no...
    if user_proceed_choice.lower() == "n":
        # We do not proceed. The user is returned to the menu.
        menus.spreadsheet_generator_menu()
    # If answers something other than y or n (yes or no)...
    elif user_proceed_choice.lower() != "y" and user_proceed_choice.lower() != "n":
        # We let them know their response was invalid...
        print("Invalid response. Returning to menu.")
        # We pause the script until they press enter, so we know they're aware of whats happening...
        input()
        # And we return them to the menu.
        menus.spreadsheet_generator_menu()
    # If the user answers Y (yes), then the script continues.
    menus.clear()

    # We clear the menu and display ascii art in red.
    print(Fore.RED + menus.msg2)

    # We are about to initialize our progress bar. When we do this, we need to specify the maximum number of loops that the
    # progress bar is tracking. This gets passed as an argument.
    progressbar_maximum = len(searchResults)

    # We initialize our progress bar, specifying the text that will be displayed alongside the bar, and the maximum amount of loops
    # the bar will track.
    bar = Bar('Generating CSVs', max=progressbar_maximum)

    # The search results that are returned are a list of dictionaries. We begin to iterate through them.
    for result in searchResults:

        # We use the get_docket() function to return the docket data for every result in our search query.
        # To pull the docket, we specify the docket number and the court. We specify if the data is cached or uncached, and what the client matter is.
        docket = user_tools.get_docket(user.authenticate(), result['docket'], result['court'], cached=global_variables.IS_CACHED, client_matter=global_variables.CLIENT_MATTER)

        # through every iteration over our results, we pass the result data, and the docket data for each result to each of the
        # nested functions we defined at the beginning of this funciton. The dataframes that are declared as global variables at the
        # top of this module are appended with new data with each iteration.
        fill_docketInformation(result,docket)
        fill_docketEntries(result,docket)
        fill_parties(result,docket)
        fill_attorneysAndFirms(result,docket)

        # With each iteration, we move our progress bar forward until it hits its maximum.
        bar.next()

    # We get the current date and time to use in the name of the output folder we will generate. This helps us generate
    # unique folder names each time we run the script.
    timeNow = datetime.datetime.now().strftime("%I%M%p %B %d %Y")

    # The complete name of the folder will be the search entered, followed by the current time.
    # We use the cleanhtml function to remove any characters that are not allowed in file or folder names.
    # cleanhtml() is imported from get_pdfs.py.
    if input_csv == None:
        containing_folder_name = f"{cleanhtml(query)} - {timeNow}"
    else:
        containing_folder_name = f"{timeNow}"

    # We put together the absolute path to the folder we want to create and populate it.
    output_directory = os.path.join(output_path, containing_folder_name)

    # We check to see if the folder already exists...
    if not os.path.exists(output_directory):
        # If it doesn't, we create it.
        os.makedirs(output_directory)

    # We create strings for the absolute paths to each individual csv file we will be creating, with the .csv extension included.
    docketInformation_outputFile = os.path.join(output_directory, "docketInformation.csv") 
    docketEntries_outputFile = os.path.join(output_directory, "docketEntries.csv")
    parties_outputFile = os.path.join(output_directory, "parties.csv")
    attorneysAndFirms_outputFile = os.path.join(output_directory, "attorneysAndFirms.csv")

    # We use the .to_csv() method on our dataframe object to save the filled out dataframes to csv files at the paths we specified above.
    # index=False specifies that we do not want to generate a numerical index column.
    docketInformation.to_csv(docketInformation_outputFile, index=False)
    docketEntries.to_csv(docketEntries_outputFile, index=False)
    parties.to_csv(parties_outputFile, index=False)
    attorneysAndFirms.to_csv(attorneysAndFirms_outputFile, index=False)

    # We set the progress bar to it's completed state.
    bar.finish()