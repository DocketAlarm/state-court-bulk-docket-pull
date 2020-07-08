import tkinter
from tkinter import filedialog 


def browseCSVFiles():
    """
    Opens a file browser window in the 'csv' directory and prompts the
    user to select a csv file.
    """

    # If this code is not included, TKinter will try to open a blank window that can't be closed.
    # Including it makes sure the root window is not shown, since this is a command line application
    # and there is no root. We only use this small gui menu for file browsing.
    root = tkinter.Tk()
    root.withdraw()


    # This code has the file browser come up in focus.
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()

    # Opens the file browser GUI.
    # The initialdir argument specifies which folder the browser will open to by default.
    # Title allows you to display text instructions on the box.
    # filetypes allows you to specify what filetypes the user is allowed to select,
    # the first filetype listed is the default.
    root.filename = filedialog.askopenfilename(initialdir = "csv", 
                                          title = "Select a File", 
                                          filetypes = (("Comma Separated Values files", 
                                                        "*.csv*"), 
                                                       ("all files", 
                                                        "*.*")))


    return root.filename

def browseDirectories(initialdir):
    """
    Opens a file browser in the 'pdf-output' directory that looks for directories.
    Takes 1 argument: the relative path to the directory you want the browser to start in.
    """

    # Gets rid of the blank tkinter root window that will show up alongside the script if you don't include this code.
    root = tkinter.Tk()
    root.withdraw()

    # Opens the file browser and returns the path to the directory the user selected as a string.
    root.directory = filedialog.askdirectory(initialdir = initialdir, title ="Choose PDF Output Directory")
    return root.directory

