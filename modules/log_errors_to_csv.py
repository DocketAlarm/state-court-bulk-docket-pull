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
        return pd.dropna(self.df)

    def append_error_csv(self, error, docket, document):
        """
        Takes 3 string arguments, adds them to the csv log in order
        """
        new_row = {
            "error":error,
            "docket":docket,
            "document":document,
        }
        appender = self.df.append(new_row, ignore_index=True)
        self.df = appender.dropna()

    def error_csv_save(self,path):
        """
        Saves the csv when you are done appending it.
        Must specify a a path as a string for the argument.
        """
        self.df.to_csv(path)

