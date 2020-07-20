import requests
import pprint
import pprint

# Experimental feature.
# End user will be able to import this module and create instances of the Docket class to work with the DA API
# without needing to know how to work with APIs

class Docket:

    def __init__(self, auth_tuple, docket_number, court_name, client_matter="", cached=True, normalize=True):
        auth_token = authenticate(auth_tuple)
        docket = get_docket(auth_token, docket_number, court_name, client_matter, cached, normalize)
        self.info = docket['info']
        self.docket_report = docket['docket_report']
        self.parties = docket['parties']
        self.related = docket['related']


def authenticate(auth_tuple):

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
    pprint.pprint(result, indent=2)
    return result


