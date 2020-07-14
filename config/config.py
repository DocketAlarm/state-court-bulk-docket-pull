# These are your global variables. They are important to change if you want
# to repurpose this code to make API calls based on a different spreadsheet,
# or if you want to search within a different court.

# Where is the default path to the input spreadisheet?
spreadsheet = "input.csv"

# Do you want a cached version of the docket, or a new one?
# (UnCached versions may be more expensive.)
isCached = True

# Do you want to use the GUI version of the program, or the command-line-interface version?
isGUI = False

# This global variable also should not be changed unless you know for sure it suits
# your use case. In some situations, the case numbers provided may not come in a
# format that Docket Alarm recognizes. If this is set to True, then the program
# will attempt to reformat those case numbers.
formatCaseNos = False

