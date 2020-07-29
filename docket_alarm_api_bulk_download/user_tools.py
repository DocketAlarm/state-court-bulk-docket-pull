import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
import requests
import pprint
import pprint
import re
import json
import get_pdfs
from retrying import retry


# End user will be able to import this module and create instances of the Docket class to work with the DA API
# without needing to know how to work with APIs

# The class and functions here are also used by the command line program to do the bulk downloads.

class Docket:
    """
    Creates a Docket object.
    Takes in your Docket Alarm username and password as a tuple,
    followed by the docket number as a string,
    and then the court name as a string as arguments.
    Optional arguments are a string reperesenting the client matter,
    whether or not the docket should be the cached version,
    (Getting uncached dockets may result in extra charges)
    and whether or not you want party names to be normalized.

    The attributes you can call on a Docket object are:
    Docket.info,
    Docket.docket_report,
    Docket.parties,
    and Docket.related.
    Each returns a dictionary with information about the docket.
    """

    def __init__(self, auth_tuple, docket_number, court_name, client_matter="", cached=True, normalize=True):
        auth_token = authenticate(auth_tuple)
        docket = get_docket(auth_token, docket_number, court_name, client_matter, cached, normalize)
        if docket['success'] == True:
            self.all = docket
            self.info = docket['info']
            self.docket_report = docket['docket_report']
            self.parties = docket['parties']
        else:
            # If there is no exact result in docket alarm for what the user typed in. We run a docket alarm search to see if
            # there are similar results. If there is a single match, we get the data the result.
            # This helps with making the program not so 'sensitive', requiring an input with perfect formatting for docket numbers
            # and court names.
            search = search_docket_alarm(auth_tuple, f"is:docket court:({court_name}) docket:({docket_number})")
            if len(search) == 1:
                search = search[0]
                foundDocket = get_docket(auth_token, search['docket'], search['court'], client_matter, cached, normalize)
                self.all = foundDocket
                self.info = foundDocket['info']
                self.docket_report = foundDocket['docket_report']
                self.parties = foundDocket['parties']
            else:
                self.all = None
                self.info = None
                self.docket_report = None
                self.parties = None
                if len(search) < 1:
                    raise NameError("Exact match not found. Searched docket alarm for similar dockets. No dockets found.")
                if len(search) > 1:
                    raise NameError("Exact match not found. Searched docket alarm for similar dockets. Too many results.")


    def links(self):

        pdf_list = []

        docket_report = self.docket_report
        
        # If it exists, it saves the value for the docket_report key in a variable.            

        # docket_report will be a list of dictionaries. This loops through each dictionary in the list.
        for item in docket_report:
            
            docName = get_pdfs.cleanhtml(item['contents'])

            docNum = item['number']


            # Checks to see if any of the dictionaries inside the list contain a 'link' key
            if 'link' in item:

                # The 'link' key contains a link to a PDF file associated with that item in the docket report.
                link = item['link']

                link_dict = {
                    'number': docNum,
                    'name': docName,
                    'link': link,
                    'exhibit': None,
                }
                # Add the found link to the list, which will ultimately be returned at the end of the function.
                pdf_list.append(link_dict)

            # Some PDF's are inside the exhibits key, which doesnt always exist. Here, we check to see if the exhibits key exists.
            if 'exhibits' in item:

                # if it does exist, we save its contents in an exhibits variable.
                exhibits = item['exhibits']
                
                # The data contained inside 'exhibits' will be a list of dictionaries. So we loop through the list to access the data.
                for exhibit in exhibits:

                    # We chck to see if any links exist inside exhibits
                    if 'link' in exhibit:

                        exhibitNumber = f"{exhibit['exhibit']}"

                        # If a link to a PDF does exist, we store it in a variable.
                        exhibitLink = exhibit['link']
                        
                        exhibit_link_dict = {
                            'number':docNum,
                            'name':docName,
                            'link': exhibitLink,
                            'exhibit': exhibitNumber,
                        }

                        pdf_list.append(exhibit_link_dict)
        return pdf_list

@retry
def search_docket_alarm(auth_tuple, query_string, limit=10, result_order=None):
    """
    Args:
    auth tuple - a tuple containing the username, followed by the password.
    query_string - Your search query as a string.
    (optional) limit - the number of results you want to display (Default 10) (Max 50).
    """
    limit = str(limit)
    endpoint = "https://www.docketalarm.com/api/v1/search/"

    if result_order != None:
        parameters = {
            "login_token": authenticate(auth_tuple),
            "q": query_string,
            "o": result_order,
            "limit": limit,
        }
    else:
        parameters = {
        "login_token": authenticate(auth_tuple),
        "q": query_string,
        "limit": limit,
        }
    result = requests.get(endpoint, params=parameters,timeout=60).json()
    search_results = result['search_results']
    return search_results

@retry
def authenticate(auth_tuple):
    """
    Takes in a username, followed by a password in a tuple as an argument.
    Returns the authentication token used to authenticate API calls.
    """
    username, password = auth_tuple
    login_url = "https://www.docketalarm.com/api/v1/login/"
    data = {
        'username': username,
        'password': password,
        }
    result = requests.post(login_url, data=data, timeout=60)
    result.raise_for_status()
    result_json = result.json()
    login_token = result_json['login_token']
    return login_token

@retry
def get_docket(auth_token, docket_number, court_name, client_matter="", cached=True, normalize=True):
    endpoint = "https://www.docketalarm.com/api/v1/getdocket/"
    params = {
        'login_token':auth_token,
        'client_matter':client_matter,
        'court':court_name,
        'docket':docket_number,
        'cached':cached,
        'normalize':normalize,
    }
    result = requests.get(endpoint, params, timeout=60).json()
    return result