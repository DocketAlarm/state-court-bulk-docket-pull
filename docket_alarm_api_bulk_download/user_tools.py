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


def map_parallel(f, iter, max_parallel=10, _enforce_parallel=False):
    """Just like map(f, iter) but each is done in a separate thread.

    If an Exception is raised during one of the map calls, then we stop
    processing additional items, and re-raise the Exception. If multiple
    exceptions occur simultaneously, we the first item in the list appears in
    the list (not necessarily the first item that raised the Exception).
    """
    # Put all of the items in the queue, keep track of order.
    import six.moves.queue
    import logging, threading, traceback
    total_items = 0
    queue = six.moves.queue.Queue()
    for i, arg in enumerate(iter):
        queue.put((i, arg))
        total_items += 1
    # No point in creating more thread objects than necessary.
    if max_parallel > total_items:
        max_parallel = total_items
    msg = "map_parallel (%s/%s - %s)" % (max_parallel, total_items, f)
    if max_parallel > 100:
        logging.warning("%s Starting many threads.", msg)

    # Dictionary of results: index -> result.
    results = {}
    # Dictionary of exceptions: index -> exception info.
    errors = {}

    # The worker thread.
    class Worker(threading.Thread):
        def run(self):
            # Keep running until we find an error, or the queue is empty.
            while not errors:
                try:
                    # Get the next item from the queue.
                    num, arg = queue.get(block=False)
                    # Run the map.
                    try:
                        results[num] = f(arg)
                    except Exception as e:
                        errors[num] = sys.exc_info()
                except six.moves.queue.Empty:
                    break

    # Create the threads.
    threads = [Worker(name="map_parallel: %d" % i) for i in range(max_parallel)]
    # We're going to try to start threads, we may not be succesfull.
    started_threads, unstarted_threads = [], []
    # Start the threads.
    for t_i, t in enumerate(threads):
        try:
            t.start()
        except Exception as e:
            if _enforce_parallel:
                # If there's trouble starting, may want to know about it.
                raise
            # We can run out of resources if we start too many threads.
            logging.error("%s Cant start thread %s of %s, %d active: %s",
                          msg, t_i, len(threads), threading.active_count(), e)
            unstarted_threads.append(t)
        else:
            started_threads.append(t)

    logging.info("%s Finished starting threads %d (%s failed)",
                 msg, len(started_threads), len(unstarted_threads))

    if not started_threads and unstarted_threads:
        # If we weren't able to start any threads, for whatever reason,
        # try doing a normal map instead of map_parallel.
        logging.error("No threads were started, won't run in parallel")
        results = []
        while True:
            try:
                iter_i, item = queue.get()
            except six.moves.queue.Empty:
                break
            else:
                results.append(f(item))
    else:
        # Now wait for the threads, it's possible we weren't able to start all.
        if unstarted_threads:
            logging.error("%s Was not able to start all threads: %s - %s", msg,
                          len(started_threads), len(unstarted_threads))
        # Wait for the threads to finish.
        [t.join() for t in started_threads]

        if errors:
            if len(errors) > 1:
                logging.warning("%s multiple errors: %d:\n%s",
                                msg, len(errors), errors)
            # Just raise the first one.
            item_i = min(errors.keys())
            # exc_info returns the exception type, it's value and its traceback.
            type, value, tb = errors[item_i]
            # Print the original traceback
            logging.info("%s exception on item %s/%s:\n%s", msg, item_i,
                         total_items, "".join(traceback.format_tb(tb)))
            # Get the completed values.
            value.partial_results = []
            for idx in range(item_i):
                if idx in results:
                    value.partial_results.append(results[idx])
                else:
                    break
            # Raise the original exception.
            raise value

    return [results[i] for i in range(len(results))]

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

    # Determine how many results there are.
    parameters = {
        "login_token": authenticate(auth_tuple),
        "q": query_string,
        "limit": 1,
    }
    if result_order != None:
        # Add results older
        parameters["o"] = result_order
    result = requests.get(endpoint, params=parameters,timeout=60).json()
    # We store the maximum number of results from our API call above in a variable.
    total_results =  result['count']
    print("Total Results: %s"%total_results)

    # A hard limit for the maximum number of iterations.
    MAX_ITERATIONS = 10000
    # Number of parralel chunks to iterate through. When using the scrolling
    # API, data is split into a certain amount of chunks that we specify. Use
    # the number of results divided by 2500. This is optimal. The scrolling
    # API can only use up to 1023 chunks at once, so if our amount of chunks is
    # above that, then we default to 1023 chunks.
    num_parallel = min(max(5, math.ceil(total_results / 2500)), 1023)

    # Create an array to store our scroll IDs, with one storage slot for each
    # chunk. The scrolling API generates key with each a new batch of 50
    # results. We pass that to the next API call for the next set of results.
    scroll_ids = [None]*num_parallel

    def do_one_scroll_index(idx):
        print("   Scroll %d of %d Starting"%(idx, num_parallel))
        # Make our real first API call for gathering results. Each chunk has its
        # own first call. In the first call. Specify the scroll_parallel and the
        # scroll_index to let the API know which chunk you are accessing.
        parameters = {
            "login_token": authenticate(auth_tuple),
            "q": query_string,
            "limit": 50,
            "scroll_parallel": num_parallel,
            "scroll_index": idx,
        }
        if result_order != None:
            parameters["o"] = result_order

        # Get results and convert from json to a python dict.
        result = requests.get(endpoint, params=parameters, timeout=60).json()
        if 'error' in result:
            print("Error: %s"%result['error'])
            return

        # Store the first pass of results.
        scroll_results = result['search_results']
        if not scroll_results:
            return scroll_results

        # Store the scroll id for the next scroll. We use this on our next API
        # call to get to return the next results.
        scroll_id = result['scroll']

        while True:
            # For the next API calls, don't include the scroll_index and
            # scroll_parralel parameters. Instead all subsequent API calls get
            # a hashed scroll key as the 'scroll' parameter. This lets the API
            # know that you are requesting a continuation of an earlier chunk.
            parameters = {
                "login_token": authenticate(auth_tuple),
                "q": query_string,
                "limit": 50,
                "scroll": scroll_id,
            }
            if result_order != None:
                parameters["o"] = result_order

            # Make the API call, convert the results from json to a dictionary.
            result = requests.get(endpoint, params=parameters,
                                  timeout=60).json()

            # With each loop, the returned results are added to scroll_results.
            scroll_results += result['search_results']
            print("   Scroll %d: Total Results %d" % (idx, len(scroll_results)))

            # Overwrite the prior scroll ID. The next loop will access the next
            # 50 results when it looks for that value in the array.
            scroll_id = result['scroll']

            # Check if the results are more than the amount the user specified they want to return.
            if not result['search_results'] or len(scroll_results) >= int(limit):
                # If it reaches that limit, we return it.
                print("   Scroll %d of %d Completed"%(idx, num_parallel))
                return scroll_results

    # Run the above function in a separate thread.
    map_results = map_parallel(do_one_scroll_index, list(range(num_parallel)),
                               max_parallel = max(20, num_parallel))

    # The above will provide a list of lists, unwrap them.
    all_results = []
    for res in map_results:
        all_results += res
    print("Completed Download")
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