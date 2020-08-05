#!/usr/bin/env python3
import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
import menus
import config

def run():
    menus.welcome()


if __name__ == '__main__':
    if config.isGUI == False:
        # If isGUI is set to False in config/config.py, then the program will run in the command line when this file is executed.
        run()
    if config.isGUI == True:
        # If isGUI is set to True in config/config.py, Then the program will open with an experimental GUI. (This is not reccomended as of yet.)
        menus.gui_run()
