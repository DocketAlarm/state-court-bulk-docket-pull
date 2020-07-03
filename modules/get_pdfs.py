import os
import json
from progress.bar import IncrementalBar
import requests
from config import config
import re

# This file contains 2 functions.
# cleanhtml() will be used inside of download_pdfs().
# download_pdfs() is used for downloading pdf files from Docket Alarm,
# while cleanhtml() is used for creating valid filenames that download_pdf() can use.
# The name of the document comes between HTML tags, so cleanhtml() removes those tags
# and returns a string that can be used as a filename.


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

    return cleantext

def download_pdfs():
    """ 
    Scans through JSON files in results folder,
    downloads any PDF links listed in the JSON data,
    and outputs the PDF's to the result_filtered folder
    """

    # The absolute path of the 'result' folder
    directory = 'json-output'

    if os.path.isdir(directory) == False:
        print("[ERROR] Could not write PDF files.\nMake sure 'json-output' folder exists in the root directroy of the program.\nCheck documentation for more information.\n")
        input()

    # The amount of files in the 'result' folder. Used for the loading bar.
    max = len(os.listdir(directory))

    # Creates a loading bar
    bar = IncrementalBar("Downloading PDFs", max=max)

    # Loops through every file in the 'result' directory.
    for file in os.listdir(directory):

        # Tells the progress bar to move forward on each iteration of the loop/
        bar.next()

        # Saves the name of each file in the folder to a variable
        filename = os.fsdecode(file)

        # Checks to ensure that we only run our code on .JSON files
        if not filename.lower().endswith(".json"):
            continue
        # Stores the absolute path of the current JSON file in the loop as a variable. 
        path = os.path.join(directory, filename)
        
        # The filename of the current JSON file in the loop without '.JSON' included.
        # Used for creating folder names correstponding to the JSON file the PDF's 
        # within the folder were created from.
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

                    # The name of the document. We will use this later for the filenames.
                    docName = item['contents']

                    # We run the cleanhtml() function on the document name to remove the HTML tags and acharcters that can't be used in filenames
                    docName = cleanhtml(docName)

                    # The ID number of the document. We use this later for the file names
                    docNum = item['number']

                    # Checks to see if any of the dictionaries inside the list contain a 'link' key
                    if 'link' in item:

                        # The 'link' key contains a link to a PDF file associated with that item in the docket report.
                        link = item['link']
                        


                        # Makes a request to access the PDF file stored at the link.
                        r = requests.get(link, stream=True)

                        # Creates a string that will be used as a uniques name for the PDF file we'll be saving.
                        # Here we use the document number.
                        filename = f"{docNum} - {docName}.pdf"

                        # String variable that represents the absolute path complete with the filename we will be saving to.
                        # It saves in a folder named after the original JSON file and the PDF will be named after it's 
                        # corresponding document number.
                        pathname = os.path.join('pdf-output', base_filename, filename)

                        # The same as above, but this variable only lists the path to the directory we will be saving it.
                        # We create this variable to check for the existence of this directory and create it if it does not exist.
                        dirpath = os.path.join('pdf-output', base_filename)

                        # If the folder does not exist...
                        if not os.path.exists(dirpath):

                            # Then, create it!
                            os.makedirs(dirpath)

                        # Once the folder is created, we can create a file inside it, open it, and...
                        with open(pathname, "wb") as f:

                            # Write the contents of the PDF to the place we specify.
                            # ( Again, in this case, the 'result_filtered' folder)
                            f.write(r.content)

                    # Some PDF's are inside the exhibits key, which doesnt always exist. Here, we check to see if the exhibits key exists.
                    if 'exhibits' in item:

                        # if it does exist, we save its contents in an exhibits variable.
                        exhibits = item['exhibits']

                        # The data contained inside 'exhibits' will be a list of dictionaries. So we loop through the list to access the data.
                        for exhibit in exhibits:

                            # We chck to see if any links exist inside exhibits
                            if 'link' in exhibit:

                                # If a link to a PDF does exist, we store it in a variable.
                                exhibitLink = exhibit['link']
                                exhibitNumber = f"{exhibit['exhibit']}"
                                exhibitRequest = requests.get(exhibitLink, stream=True)

                                exhibitFileName = f"Exhibit {exhibitNumber} - {docNum} - {docName}"
                                exhibitPathName = os.path.join('pdf-output', base_filename, exhibitFileName)
                                dirpath = os.path.join('pdf-output', base_filename)

                                # If the folder does not exist...
                                if not os.path.exists(dirpath):

                                    # Then, create it!
                                    os.makedirs(dirpath)
                                
                                try:
                                # Once the folder is created, we can create a file inside it, open it, and...
                                    with open(exhibitPathName, "wb") as e:

                                        # Write the contents of the PDF to the place we specify.
                                        # ( Again, in this case, the 'result_filtered' folder)
                                        e.write(exhibitRequest.content)
                            
                                except Exception as e:
                                    print("[ERROR] Could not write PDF file.\nPlease ensure that 'pdf-output' folder is present at the root directory of the program.\nSee documentation for more details.\n")
                                    input()
                                    print(e)

            # We close the file when we are done. This also ensures that the file is saved.    
            jsonFile.close()
    bar.finish()
    try:
        os.startfile("pdf-output")
    except Exception:
        pass  
        

