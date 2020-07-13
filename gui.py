import PySimpleGUI as sg

from modules import global_variables

from modules import get_pdfs

from modules import get_json

from modules import login

import os

import main
import pandas as pd

import requests

import json


def declare_globals(event, values):
    global_variables.CSV_INPUT_PATH = values['pathCSV']
    global_variables.JSON_INPUT_OUTPUT_PATH = values['pathJSON']
    global_variables.PDF_OUTPUT_PATH = values['pathPDF']
    print(f"CSV GLOBAL = {global_variables.CSV_INPUT_PATH}\nJSON GLOBAL = {global_variables.JSON_INPUT_OUTPUT_PATH}\nPDF GLOBAL = {global_variables.PDF_OUTPUT_PATH}")
    pass



layout = [
    [sg.Txt('Input CSV')],
    [sg.Input(os.path.abspath(os.path.join("csv", "input.csv")),size=(50,1), key="pathCSV"), sg.FileBrowse("Browse", key="browseCSV")],
    [sg.Txt('JSON Directory')],
    [sg.Input(os.path.abspath("json-output"),size=(50,1), key="pathJSON"), sg.FolderBrowse("Browse", key="browseJSON")],
    [sg.Txt('PDF Directory')],
    [sg.Input(os.path.abspath("pdf-output"),size=(50,1), key="pathPDF"), sg.FolderBrowse("Browse", key="browsePDF")],
    [sg.Button("Get JSON & PDFs", key="getJSON_PDF"), sg.Button("Get JSON", key="getJSON"), sg.Button("Get PDFs", key="getPDF")],
    [sg.Image("img/spinner.gif", key="spinner")]
]

loginLayout = [
    [sg.Txt("Log in to Docket Alarm")],
    [sg.Txt("Username:"), sg.Input(size=(50,1), key="username")],
    [sg.Txt("Password:"), sg.Input(size=(50,1), key="password")],
    [sg.Txt("Client Matter:"), sg.Input(size=(50,1), key="clientMatter")],
    [sg.Button("Submit", key="submit")]
]



window = sg.Window('Bulk-Docket-Pull', layout)
loginWindow = sg.Window("Log In", loginLayout)


def display_login_window():
    while True:
        event, values = loginWindow.read()

        window.Element('spinner').UpdateAnimation("img/spinner.gif",  time_between_frames=50)

        if event == "submit":
            login_url = "https://www.docketalarm.com/api/v1/login/"

            data = {
                'username':values['username'],
                'password':values['password'],
                'client_matter':values['clientMatter'],
                }

            result = requests.post(login_url, data=data)

            result_json = result.json()

            if result_json['success'] != True:
                sg.popup_error("Invalid Username or Password.")
            else:
                login.store_user_info_locally(values['username'], values['password'], values['clientMatter'])
                sg.popup_ok("Login successful!")
                loginWindow.close()
                display_main_window()

def display_main_window():
    while True:
        event, values = window.read()
        print(event, values)
        if event == "getJSON_PDF":
            declare_globals(event, values)
            main.get_json_and_pdfs()
        if event == "getJSON":
            declare_globals(event, values)
            get_json.loop_dataframe()
        if event == "getPDF":
            declare_globals(event, values)
            link_list = get_pdfs.get_urls("json-output")
            sg.popup_animated("img/spinner.gif", time_between_frames=1)
            get_pdfs.thread_download_pdfs(link_list)

        if event == sg.WIN_CLOSED:
            break

def gui_run():
    if not os.path.isfile(os.path.join("sav", "credentials.pickle")):
        display_login_window()
    else:
        display_main_window()
    
if __name__ == "__main__":
    gui_run()