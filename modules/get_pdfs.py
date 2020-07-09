import os
import json
from progress.bar import IncrementalBar
import requests
from config import config
import re
from multiprocessing import Pool, cpu_count
import datetime
from modules import file_browser
from modules import global_variables

# Reinforces that the variables defined in the global_variables module, and then edited from within other modules,
# continue to have the value that the user changed it to.
# It may look redundant, but without this line, the script only uses the default variable, without reflecting changes.
global_variables.PDF_OUTPUT_PATH = global_variables.PDF_OUTPUT_PATH


def cleanhtml(raw_html):
    """
    This function is for creating filenames from the HTML returned from the API call.
    It takes in a string containing HTML tags as an argument, and returns a string without HTML tags or any
    characters that can't be used in a filename.
    """

    # Created a regular expression pattern object for detecting HTML tags
    cleanr = re.compile('<.*?>')

    # Removes HTML tags from the string argument
    cleantext = re.sub(cleanr, '', raw_html)

    # Replaces spaces with underscores
    cleantext = str(cleantext).strip().replace(' ', '_')

    # Removes characters that can't be used in filenames
    cleantext = re.sub(r'(?u)[^-\w.]', '', cleantext)

    # Removes periods
    cleantext = cleantext.replace(".", "")

    # Cuts the name short so it doesn't go over the maximum amount of characters for a NTFS filename
    cleantext = cleantext[0:240]

    # Return the text free of html tags and symbols that can't be used in filenames.
    # It will also be cut to a length that doesn't go over the maximum length for a filename. 
    return cleantext

def get_urls(input_directory):
    """
    Takes in a directory full of JSON files as input, and returns the values for keys labeled 'link' for all of the files.
    The output is a list of tuples.
    The first item in each tuple is a string containing the link.
    The second item in each tuple is a string containing the name of the document the link is connected to.
    The third item in each tuple is a string containing the original file name of the json file that the link was retrieved from.
    """

    # This list will be appended throughout the function with every pdf link found within the json files.
    # It will ultimately be returned at the end of the function.
    pdf_list = []

    # The absolute path of the 'result' folder
    input_directory = global_variables.JSON_INPUT_OUTPUT_PATH

    if os.path.isdir(input_directory) == False:
        print("[ERROR] Could not write PDF files.\nMake sure 'json-output' folder exists in the root directroy of the program.\nCheck documentation for more information.\n")
        input()


    # Loops through every file in the 'result' directory.
    for file in os.listdir(input_directory):

        # Tells the progress bar to move forward on each iteration of the loop/
        # bar.next()

        # Saves the name of each file in the folder to a variable
        filename = os.fsdecode(file)

        # Checks to ensure that we only run our code on .JSON files
        if not filename.lower().endswith(".json"):
            continue
        # Stores the absolute path of the current JSON file in the loop as a variable. 
        path = os.path.join(input_directory, filename)

        base_filename = filename.split(".")[0]
        
        # Opens each individual JSON file
        with open(path) as jsonFile:

            # Allows us to work with JSON files the same way we would work with a Python dictionary.
            jsonObject = json.load(jsonFile)
            
            # Checks to see if a 'docket_report' key exists in the current JSON file in the loop.
            if "docket_report" in jsonObject:

                # If it exists, it saves the value for the docket_report key in a variable.
                docket_report = jsonObject['docket_report']

                # docket_report will be a list of dictionaries. This loops through each dictionary in the list.
                for item in docket_report:
                    
                    docName = item['contents']

                    # We run the cleanhtml() function on the document name to remove the HTML tags and acharcters that can't be used in filenames
                    docName = cleanhtml(docName)

                    # The ID number of the document. We use this later for the file names
                    docNum = item['number']

                    # Checks to see if any of the dictionaries inside the list contain a 'link' key
                    if 'link' in item:

                        # The 'link' key contains a link to a PDF file associated with that item in the docket report.
                        link = item['link']

                        link_filename = f"{docNum} - {docName}"

                        link_tuple = (link, link_filename, base_filename)
                        # Add the found link to the list, which will ultimately be returned at the end of the function.
                        pdf_list.append(link_tuple)

                    # Some PDF's are inside the exhibits key, which doesnt always exist. Here, we check to see if the exhibits key exists.
                    if 'exhibits' in item:

                        # if it does exist, we save its contents in an exhibits variable.
                        exhibits = item['exhibits']
                        
                        # The data contained inside 'exhibits' will be a list of dictionaries. So we loop through the list to access the data.
                        for exhibit in exhibits:

                            # We chck to see if any links exist inside exhibits
                            if 'link' in exhibit:

                                exhibitNumber = f"{exhibit['exhibit']}"

                                # If a link to a PDF does exist, we store it in a variable.
                                exhibitLink = exhibit['link']
                                
                                # We create a file name to save the exhibit pdf as
                                exhibitName = f"Exhibit {exhibitNumber} - {docNum} - {docName}"

                                # We package the name, link, and filename together in a tuple, that will be passed as an argument to our
                                # download_from_link_list() function within the multiprocess_download_pdfs() function where we use imap to
                                # downloading with multiprocessing functionality.
                                exhibitLink_tuple = (exhibitLink, exhibitName, base_filename)
                                pdf_list.append(exhibitLink_tuple)

            # We close the file when we are done. This also ensures that the file is saved.    
            jsonFile.close()
    # bar.finish()
    return pdf_list

def download_from_link_list(link, fileName, folderName, outputPath):
    """
    Downloads PDF documents from the web and saves them in a specified folder.
    Takes in 3 string arguments:
    1. Link to a pdf file
    2. File name we will save as
    3. Name of the folder we will create to store our PDFs.
    Notice how the arguments are the same as what the get_urls() function returns.
    This function Isn't made to be used on its own, but can be.
    """
    
    # The directory where we will create the subdirectories within for each individual docket
    outputDirectoryPath = os.path.join(outputPath, folderName)
    # The path we are saving the file to, inside the subdirectory we will create.
    outputFilePath = os.path.join(outputDirectoryPath, f"{fileName}.pdf")

    # If the directory for the docket doesn't yet exist...
    if not os.path.exists(outputDirectoryPath):

        # Then, create it!
        os.makedirs(outputDirectoryPath)
    
    # We then make an http request to the pdf link and save the result in a variable.
    request = requests.get(link, stream=True)

    try:
    # Once the folder is created, we can create a file inside it, open it, and...
        with open(outputFilePath, "wb") as e:

            # Write the contents of the PDF to the place we specify.
            e.write(request.content)
    
    except Exception as a:
        print(a)


def multiprocess_download_pdfs(link_list):
    """
    Gets a list of PDF documents with appropriate output filenames and foldernames from the get_urls() function.
    We use multiprocessing to dedicate all of our cpu cores to running the download_from_link_list() function with the
    result of get_urls as the arguments for each pass through the function.
    """

    print("Downloading PDFs...")

    print(global_variables.PDF_OUTPUT_PATH)

    # The list of tuples we get in link_list will be passed as arguments when calling download_from_link_list() with imap below to
    # use multiprocessing. There is an issue where the function cannot find global variables when it is called from within imap.
    # We use the add_path_to_list_of_tuples() function to append each tuple in the list with the correct file path from the global variable
    # which is specified by the user within the menus. This ensures that the correct output path can be passed as an argument.
    link_list = add_path_to_list_of_tuples(link_list, global_variables.PDF_OUTPUT_PATH)

    # Initiates the pool, assigns different calls to a function to a specified amount of CPU cores.
    # In this case, we pass the cpu_count() which represents the amount of CPU cores in the current system.
    # This will ensure that all the systems cores get utilized, and the more cores the system has, the faster the files will download.
    with Pool(cpu_count()) as pool:
        # Starmap allows us to pass multiple arguments to the function of our choice. The arguments are fed in as a list of tuples.
        # download_from_link_list is the function we are passing the tuples to.
        # Files will not be downloaded in order, they are simply downloaded. When a process finishes on one core, it simply picks up
        # another call to the function with the tuple arguments that haven't been passed through yet.
        try:
            pool.starmap(download_from_link_list, link_list)
        except Exception as a:

            # If there is an error, the log file located at log\log.txt will be appended with the date and time, followed by the error that occured.
            # The program will not stop if an error is thrown.
            timeNow = datetime.datetime.now().strftime("%I:%M%p %B %d, %Y")
            with open(os.path.join('log', 'log.txt'), 'a') as errorlog:
                errorlog.write(f"\n{timeNow}\n")
                errorlog.write(a)
                
    # When the job is finished. We terminate the pool and free-up our cpu cores.
    pool.terminate()

def add_path_to_list_of_tuples(list_of_tuples, path):
    """
    The tuples that are returned from get_urls are the first 3 arguments that get passed to download_from_link_list
    with the imap multiprocessing function in multiprocess_download_pdfs.
    This function takes in that list of tuples and returns the same list with the specified file path added as the last
    Item on each tuple.
    This is important because the user needs to specify an output path in multiprocess_download_pdfs and it must be passed as
    an argument in every call to download_from_link_list.
    """

    # Creates the new list which we will populate in the loop below.
    new_list = []

    # We loop through the old list of tuples...
    for item in list_of_tuples:
        # Tuples are immutable, which means they cant be changes, so we convert each one to a list...
        to_list = list(item)
        # Then we add the file path specified in the argument passed to this function to the end of each list...
        to_list.append(path)
        # After adding to the list, we convert it back to a tuple...
        back_to_tuple = tuple(to_list)
        # We add the tuple to the new list above...
        new_list.append(back_to_tuple)
    # When the new list is populated with the updated tuples, we return it.
    return new_list








        
        
