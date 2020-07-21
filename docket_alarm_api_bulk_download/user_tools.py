import requests
import pprint
import pprint

# Experimental feature.
# End user will be able to import this module and create instances of the Docket class to work with the DA API
# without needing to know how to work with APIs

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
        self.info = docket['info']
        self.docket_report = docket['docket_report']
        self.parties = docket['parties']
        self.related = docket['related']

def search_docket_alarm(auth_tuple, query_string, limit=10):
    """
    Args:
    auth tuple - a tuple containing the username, followed by the password.
    query_string - Your search query as a string.
    (optional) limit - the number of results you want to display (Default 10) (Max 50).
    """
    limit = str(limit)
    endpoint = "https://www.docketalarm.com/api/v1/search/"
    parameters = {
        "login_token": authenticate(auth_tuple),
        "q": query_string,
        "limit": limit,
    }
    result = requests.get(endpoint, params=parameters).json()
    search_results = result['search_results']
    return search_results


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
    result = requests.post(login_url, data=data)
    result.raise_for_status()
    result_json = result.json()
    login_token = result_json['login_token']
    return login_token

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
    result = requests.get(endpoint, params).json()
    return result


