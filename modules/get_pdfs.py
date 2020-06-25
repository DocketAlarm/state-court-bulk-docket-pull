import os
import json
from progress.bar import IncrementalBar
import requests
import config


def download_pdfs():
    """ Scans through JSON files in results folder,
        downloads any PDF links listed in the JSON data,
        and outputs the PDF's to the result_filtered folder
    """

    # The absolute path of the 'result' folder
    directory = os.path.join(config.cwd, 'json-output')

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
        if filename.endswith(".JSON") or filename.endswith(".json"):

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

                        # Checks to see if any of the dictionaries inside the list contain a 'link' key
                        if 'link' in item:

                            # The 'link' key contains a link to a PDF file associated with that item in the docket report.
                            link = item['link']
                            
                            # Makes a request to access the PDF file stored at the link.
                            r = requests.get(link, stream=True)

                            # Creates a string that will be used as a uniques name for the PDF file we'll be saving.
                            # Here we use the document number.
                            filename = f"{item['number']}.pdf"

                            # String variable that represents the absolute path complete with the filename we will be saving to.
                            # It saves in a folder named after the original JSON file and the PDF will be named after it's 
                            # corresponding document number.
                            pathname = os.path.join(config.cwd,'pdf-output', base_filename, filename)

                            # The same as above, but this variable only lists the path to the directory we will be saving it.
                            # We create this variable to check for the existence of this directory and create it if it does not exist.
                            dirpath = os.path.join(config.cwd,'pdf-output', base_filename)

                            # If the folder does not exist...
                            if not os.path.exists(dirpath):

                                # Then, create it!
                                os.makedirs(dirpath)
                            else:
                                pass

                            # Once the folder is created, we can create a file inside it, open it, and...
                            with open(pathname, "wb") as f:

                                # Write the contents of the PDF to the place we specify.
                                # ( Again, in this case, the 'result_filtered' folder)
                                f.write(r.content)
                            pass
                        else:
                            pass

                        # Some PDF's are inside the exhibits key, which doesnt always exist. Here, we check to see if the exhibits key exists.
                        if 'exhibits' in item:

                            # if it does exist, we save its contents in an exhibits variable.
                            exhibits = item['exhibits']

                            # The data contained inside 'exhibits' will be a list of dictionaries. So we loop through the list to access the data.
                            for exhibit in exhibits:

                                # We chck to see if any links exist inside exhibits
                                if 'link' in exhibit:

                                    # If a link to a PDF does exist, we store it in a variable.
                                    link = exhibit['link']
                                    # TODO: Specify a file name and save the exhibit links in their appropriate folder.
                                else:
                                    pass
                        else:
                            pass


                else:
                    pass   

                # We close the file when we are done. This also ensures that the file is saved.    
                jsonFile.close()
            continue
        else:
            continue

