import os



# These are your global variables. They are important to change if you want
# to repurpose this code to make API calls based on a different spreadsheet,
# or if you want to search within a different court.

court = "Florida State, Duval County, Fourth Circuit Court"
spreadsheet = "death-penalty-project.csv"
isCached = True


# This global variable should not be modified. This helps form abosulute paths
# with os.path.join() within any subdirectories. We can always use 'cwd' to call
# the root directory. 
# If you're in doubt about whether or not if you understand what this does, it's
# best not to change it.
cwd = f"{os.getcwd()}"

