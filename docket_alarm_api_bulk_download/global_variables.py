import os

CURRENT_DIR = os.path.dirname(__file__)
### This file is for storing global variables that can be accessed between modules ###

# The path to the csv file containing the docket numbers
CSV_INPUT_PATH = os.path.join(CURRENT_DIR, "csv")

# The path where json files are saved to, and where the program will look for to find links when downloading pdfs
JSON_INPUT_OUTPUT_PATH = os.path.join(CURRENT_DIR, "json-output")

# The path wherer the folders full of pdfs will be saved to
PDF_OUTPUT_PATH = os.path.join(CURRENT_DIR, "pdf-output")

# The reason for using the script. Used for billing purposes.
CLIENT_MATTER = ""

IS_CACHED = True