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
import math
import pull_missing_docs

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
                if cached == True:
                    # If cached is turned on and a docket is not found with a docket alarm search, a direct search will be made as a last
                    # effort to try to find the docket
                    direct_search_results = pull_missing_docs.search_direct(docket_number, court_name)
                    if direct_search_results > 0:
                        first_result = direct_search_results[0]
                        foundDocket = get_docket(auth_token, first_result.get("docket", None), first_result.get("court", None), client_matter=client_matter,cached=cached, normalize = normalize)
                        self.all = foundDocket
                        self.info = foundDocket.get('info', None)
                        self.docket_report = foundDocket.get('docket_report', None)
                        self.parties = foundDocket.get('parties', None)
                    else:
                        # If nothing is found, all the attributes will be None
                        self.all = None
                        self.info = None
                        self.docket_report = None
                        self.parties = None
                if cached == False:
                    # An error will let the user know that an exact match wasn't found for a particular docket.
                    if len(search) < 1:
                        raise NameError("Exact match not found. Searched docket alarm for similar dockets. No dockets found.")
                    if len(search) > 1:
                        raise NameError("Exact match not found. Searched docket alarm for similar dockets. Too many results.")



    def links(self):
        """
        The links method will return a dictionary full of all the links to PDF documents associated with the docket.
        """

        # We create an empty list that will be populated with all of the dictionaries with the links
        pdf_list = []
        
        docket_report = self.docket_report
        
        # If it exists, it saves the value for the docket_report key in a variable.            

        # docket_report will be a list of dictionaries. This loops through each dictionary in the list.
        for item in docket_report:
            # We use the cleanhtml function to remove all html tags and symbols from document names.    
            docName = get_pdfs.cleanhtml(item['contents'])

            # We store the docket number in a variable.
            # .get() allows us to specify a key to get a value, and return None if the key isn't present in the dictionary.
            docNum = item.get('number', None)


            # Checks to see if any of the dictionaries inside the list contain a 'link' key
            if 'link' in item:

                # The 'link' key contains a link to a PDF file associated with that item in the docket report.
                link = item['link']

                # We create the dictionary full of PDF links that will be appended to the list that is returned from this method.
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
                        
                        # We create the dictionary full of PDF links that will be appended to the list that is returned from this method if there are exhibits
                        exhibit_link_dict = {
                            'number':docNum,
                            'name':docName,
                            'link': exhibitLink,
                            'exhibit': exhibitNumber,
                        }
                        
                        # Adds the dictionary above to the list that will be returned from this method.
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
    if int(limit) <= 50:
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

    # If the user specifies a limit larger than 50, we use the scrolling API, which allows us to get past the 50 result limit and access all results.
    if int(limit) > 50:

        # We make API call #0. This is not an API call we use to return results, we just want to see what the maximum number of returned
        # results are that we can access.
        if result_order != None:
            # Not passing an o (result order) parameter during our API call sorts the results by relevance. For any other method of sorting, we pass the o parameter
            # with the kind of order we want to sort by.
            parameters = {
                "login_token": authenticate(auth_tuple),
                "q": query_string,
                "o": result_order,
                "limit": 1,
            }
        else:
            parameters = {
            "login_token": authenticate(auth_tuple),
            "q": query_string,
            "limit": 1,
            }

        
        # Here we set up our variables

        # We get the result of our API call above. This call isn't for getting results, just for seeing how many results we can access.
        result = requests.get(endpoint, params=parameters,timeout=60).json()

        # We set a hard limit for the maximum number of iterations the function will make before quitting.
        MAX_ITERATIONS = 10000

        # We store the maximum number of results from our API call above in a variable.
        amount_of_results =  result['count']

        # Here we get the number of parralel chunks we can sort through. When using the scrolling API, data is split into a certain amount of chunks that we specify.
        # We use the number of results divided by 2500. This is optimal. The scrolling API can only use up to 1023 chunks at once, so if our amount of chunks is above that,
        # then we default to 1023 chunks.
        num_parallel = math.ceil(amount_of_results / 2500) if math.ceil(amount_of_results/2500) <= 1023 else 1023

        # We create an array to store our scroll IDs. We need one storage slot for every chunk. The scrolling API generates keys, each time we retrieve a new batch of 50 results
        # on each chunk, the API returns a hash key that we can pass into our next API call to get the next set of results in order.
        scroll_ids = [None]*num_parallel

        # This is the list that we will append with all of our results. This will be returned at the end when it is populated.
        all_results = []


        
        # Now we make our real first API call for gathering results. Each chunk has its own first call. In the first call, you specify the
        # scroll_parallel and the scroll_index to let the API know which chunk you are accessing.
        for scroll_index in range(num_parallel):
            
            if result_order != None:
                parameters = {
                "login_token": authenticate(auth_tuple),
                "q": query_string,
                "o": result_order,
                "limit": 50,
                "scroll_parallel": num_parallel,
                "scroll_index": scroll_index,
            }

            else:
                parameters = {
                "login_token": authenticate(auth_tuple),
                "q": query_string,
                "limit": 50,
                "scroll_parallel": num_parallel,
                "scroll_index": scroll_index,
                }

            # We convert our results from json to a python dictionary and store the dictionary in a variable.
            result = requests.get(endpoint, params=parameters,timeout=60).json()
            

            if 'error' in result:
                # print(result['error'])
                pass

            # We store each of our search results in each pass on each of our seperate chunks in the all_results list we created above.
            all_results += result['search_results']

            # We print the amount returned so the user can see that results are coming back and get a feel for how much longer the query will take.
            print(len(all_results))

            # We store the id for the next scroll in the array that holds on to scroll keys. We use this on our next API call to get to return the next results.
            # Each of those will overwrite that slot in the array and then continue looping to gather all of the results.
            scroll_ids[scroll_index] = result['scroll']
        
            # after each iteration, we check to see if the results are more than the amount the user specified they want to return.
            if len(all_results) >= int(limit):
                # If it reaches that limit, we return it.
                return all_results

            scroll_ids[scroll_index] = result['scroll']


        # This array has a slot for each chunk for the scrolling api. While the value is false, we continue. When a chunk stops producing results,
        # we change the value to true and we use this to stop the loop for that particular chunk.
        scroller_done = [False]*num_parallel

        # We loop until we reach the manually set max
        for i in range(MAX_ITERATIONS):
            
            # For each of our chunks...
            for scroll_index in range(num_parallel):
                
                # We check to see if the chunk has no more results to return. If it does, we skip it.
                if scroller_done[scroll_index]:
                    continue

                # For our second API call and on for each chunk, we no longer include the scroll_index and scroll_parralel parameters.
                # Instead all subsequent API calls get a hashed scroll key as the 'scroll' parameter. This lets the API know that you are requesting a
                # continuation of a chunk that was accessed earlier.
                if result_order != None:
                    parameters = {
                        "login_token": authenticate(auth_tuple),
                        "q": query_string,
                        "o": result_order,
                        "limit": 50,
                        "scroll":scroll_ids[scroll_index],
                    }

                else:
                    parameters = {
                        "login_token": authenticate(auth_tuple),
                        "q": query_string,
                        "limit": 50,
                        "scroll":scroll_ids[scroll_index],
                        }
                
                # We make our API call, convert the results from json to a dictionary, and store the dictionary in a variable.
                result = requests.get(endpoint, params=parameters,timeout=60).json()

                # With each loop, the returned results are added to our all_results list that will be returned at the end.
                all_results += result['search_results']

                # We store the next scroll ID for each chunk in the index, overwriting the prior scroll ID. That way, the next loop will be able to access the next
                # 50 results when it looks for that value in the array.
                scroll_ids[scroll_index] = result['scroll']
                
            # If our number of returned results goes above what the user specified. We stop and return it.
            # In the generate_spreadsheets.py file where this function is called, we slice the result to be the exact length that the user specified.
            # When called on its own, it will return slightly more results than what the user specified.
            if len(all_results) >= int(limit):
                return all_results
    return all_results
                


@retry
def authenticate(auth_tuple):
    """
    Takes in a username, followed by a password in a tuple as an argument.
    Returns the authentication token used to authenticate API calls.
    """

    # Unpacks the tuple into a username and password variable
    username, password = auth_tuple

    # The endpoint we will be sending the POST request to
    login_url = "https://www.docketalarm.com/api/v1/login/"

    # The parameters we will send to the endpoint in our API call, as a dictionary.
    data = {
        'username': username,
        'password': password,
        }

    # We make the API call and store the result in a variable.
    result = requests.post(login_url, data=data, timeout=60)

    # If the API call is unsuccessful, we raise an error.
    result.raise_for_status()

    # We convert the result of the API call from JSON to a Python dictionary so we can work with it in python.
    result_json = result.json()

    # We store the data in the login_token in a variable. If there is no login_token key, we return None
    login_token = result_json.get('login_token', None)

    # We return the login token as a string
    return login_token

@retry
def get_docket(auth_token, docket_number, court_name, client_matter="", cached=True, normalize=True):
    """
    Takes in an authentication token as a string,
    a docket number as a string, and the court name as a string,
    and returns the docket data as a dictionary.

    Optional parameters are client_matter, Cached, and normalize.

    Cached is True by default. If turned to false, the most recent docket data will be fetched directly,
    this can result in extra charges. set cached to False if you are having trouble retrieving data for a docket.

    Normalize normalizes the names of parties when possible.
    """

    # We specify the endpoint we will be making the api call to.
    endpoint = "https://www.docketalarm.com/api/v1/getdocket/"

    # We set the parameters we will send to the endpoint in a dictionary.
    # These values come from the arguments that are passed to this function.
    params = {
        'login_token':auth_token,
        'client_matter':client_matter,
        'court':court_name,
        'docket':docket_number,
        'cached':cached,
        'normalize':normalize,
    }

    # we make the api call and store the result in a variable.
    # We use the .json() method to convert the result to a python dictionary.
    result = requests.get(endpoint, params, timeout=60).json()

    # We return the results of the API call as a dictionary.
    return result