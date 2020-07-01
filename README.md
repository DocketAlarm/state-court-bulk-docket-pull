# State Court Bulk Docket Pull

This program allows you to download court case data and documents in bulk.
A csv file full of case numbers will be taken as input, and the program will automatically download
all of the files from the Docket Alarm API.

## Getting Started

The first thing you need to do is enter your user authentication information.

To begin, enter the docs folder and open requirements.txt. This file lists all the dependencies for this project.
You will need to install all of these packages before the program can run.

Now you need to do is enter your user authentication information.

Go into auth.example.py inside the 'config' folder and enter the username and password for your Docket Alarm account.
Change the name of the file to simply "auth.py"

Next, go to the input.example.csv file in the 'csv' folder. Fill this out with the information for any dockets you
want to pull. You will need to select courts from the courts.txt file to enter into the csv. Copy and paste them
so they will be included exactly as they are written in courts.txt. Rename input.example.csv to simply: input.csv.

Then, just run main.py and follow the instructions.

There is plenty of inline documentation to help you out in case you want to modify the code.

## Walkthrough

1. Getting to the root 
  1. Download the project files as a .zip and extract them to a directory of your choosing.
  1. Enter the root of the project, the ```state-court-bulk-docket-pull``` folder.
1. Logging in to Docket Alarm
  1. Go into the ```config``` folder and copy the ```auth.example.py``` file inside the same directory.
  1. Rename the copy of ```auth.example.py``` to ```auth.py```.
  1. Open ```auth.py``` and set ```username = '[Your Docket Alarm Username]'``` (Keep the quotes)
  1. Continue to set ```password = '[Your Docket Alarm Password]'``` (Keep the quotes)
  1. Inside of the quotes on the right side of the equal sign next to ```client_matter```, enter a short description of what you are using the program for.
  1. Save and close ```auth.py```
1. Filling out the csv with the cases you want to download data for
  1. From the root directory of the project, ```state-court-bulk-docket-pull``` open the ```csv``` folder.
  1. Inside the ```csv``` folder, make a copy of ```input.example.csv```.
  1. Rename ```input.example.csv``` to ```input.csv```
  1. ```input.csv``` is a blank template you will edit to specify the API calls you want to make. The program will download any cases listed here.
  1. ```input.csv``` has 3 columns: Name, Docket Number, and Court.
    1. The Name column can be set to whatever you want. Name it something that will help you identify that individual case. It is used for the output filenames.
    1. The Docket Number column is where you will enter the docket numbers to be searched.
      1. It's a good idea to look for some of your cases on the Docket Alarm website to see what format the Docket Numbers should be in.
    1. The Court column is the court you are searching for that particular docket number. The spelling of the court name is very important.
      1. To find a court go to ```state-court-bulk-docket-pull\docs\courts.txt```. This file contains all the courts Docket Alarm can search.
        1. Copy and paste from here into your csv to ensure you have the proper spelling.
  1. You can save and close ```input.csv``` when you are done and leave it in the ```csv``` directory.
1. Installing Dependencies
  1. Before you can run the program, you need to ensure you have all of the dependencies installed.
  1. To install all the dependencies at once, open your command prompt and cd to the root directory.
    1. ```cd "C:\Users\Ryan\Documents\Programming\Python\state-court-bulk-docket-pull"```
      1. (This will be different for you, depending on where you saved your ```state-court-bulk-docket-pull``` folder)
    1. When the root of the project is your working directory, type: ```pip install -r docs/requirements.txt```
    1. When the install completes, stay in the current directory to launch the program.
1. Launching the Program
  1. If you haven't already, open your command prompt and choose the root of the project as your current working directory.
    1. The command will be something similar to ```cd "C:\Users\Ryan\Documents\Programming\Python\state-court-bulk-docket-pull"```
    1. Now that your current working directory is set to the root, simply enter ```python main.py``` to launch the program.
    1. From here, the instructions inside the program will guide you.
    1. When the program finishes running. Your results can be found in the directories: ```state-court-bulk-docket-pull\json-output``` and ```\pdf-output```.

## The Files:

### auth.example.py

The first place you'll need to go before experimenting with this script.
You need to enter your Docket Alarm login information here.
When you aredone, rename it to "auth.py" by removing the underscore,
and you are ready to go!

### death-penalty-project.csv

The example csv file used. Feel free to change the file and tweak the script to 
suit your own use case!

### JSON files.zip

A backup of the 'result' folder from when I ran this script with isCached=True on 6/22/20.
This contains all the cases specified in the spreadsheet as JSON files.

### result folder

Where your JSON files will appear when you run the main.py script.

### main.py

This is the file used to launch the program. It contains a variety of functions:

#### write_to_json_file(folder, fileName, data)

takes in the name of a folder in the current directory, the name of
the file you want to create, and the json object you want to write to
the file.

#### authenticate()

Returns the authentication token to make API calls.
Make sure that auth.py is filled out!

#### list_courts()

Prints all the courts to the console and returns a list of courts.

#### get_parameters()

Returns all of the parameters you can use when making a post request to the /searchdirect endpoint.

#### get_results(party_name, docketnum)

Takes in the name of a party and the docket number as a parameter,
returns the Docket Alarm search results. You can make calls to the
/getdocket endpoint with these results to get more detailed information
on the docket you are looking for.

#### get_docket(docket)

Takes in a docket number as an argument and returns all the JSON data
available from Docket Alarm.

#### format_case_number(unformatted_case_number)

Trims off excess data from the case numbers
provided, and returns the same number in a
form that Docket Alarm can search for.

#### loop_dataframe()

loops through the spreadsheet listed in the global variable toward the top of
this script. Returns docket info from each.
