import os

cwd = f"{os.getcwd()}"

# These are your global variables. They are important to change if you want
# to repurpose this code to make API calls based on a different spreadsheet,
# or if you want to search within a different court.

court = "Florida State, Duval County, Fourth Circuit Court"
spreadsheet = "death-penalty-project.csv"
isCached = True