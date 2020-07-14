import pandas as pd

class ErrorCSV:
    # Used for creating CSV Error logs.
    # Calling object.df will produce the pandas dataframe.
    # Calling object.append_error_csv(Three string arguments) will add the values to the csv log object.
    # Calling error_csv_save(path) will save the table as a csv to the path you specify.
    def __init__(self):
        """
        Initializes an empty dataframe with three column headers
        """
        self.df = pd.DataFrame(columns=['error', 'docket','document'])

    def __repr__(self):
        # returns the dataframe, using dropna() to remove any null values.
        # Null values usually get added to the class as a glitch.
        return pd.dropna(self.df)

    def append_error_csv(self, error, docket, document):
        """
        Takes 3 string arguments, adds them to the csv log in order
        """
        # Before adding a new row, the row must be structured as a dictionary.
        # We create a dictionary whenever this method is called, that has the column labels as keys,
        # and will fill in the values with the arguments passed to the method.
        new_row = {
            "error":error,
            "docket":docket,
            "document":document,
        }
        # Then we use append() to add the new values to the dataframe.
        appender = self.df.append(new_row, ignore_index=True)
        # Append() usually returns a new dataframe with the changes added, rather than actually 
        # changing the original, so we make self.df equal to the changed version.
        self.df = appender.dropna()

    def error_csv_save(self,path):
        """
        Saves the csv when you are done appending it.
        Must specify a a path as a string for the argument.
        """
        self.df.to_csv(path)

