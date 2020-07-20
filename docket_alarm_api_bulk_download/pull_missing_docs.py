import requests
import get_json

def search_direct(docketnum, court):
    """ Takes in the name of a party and the docket number as a parameter,
        returns the Docket Alarm search results. You can make calls to the
        /getdocket endpoint with these results to get more detailed information
        on the docket you are looking for.
    """
    searchdirect_url = "https://www.docketalarm.com/api/v1/searchdirect/"

    data = {
        'login_token':get_json.authenticate(),
        'client_matter':"",
        # 'party_name':party_name,
        'docketnum':docketnum,
        'court': court,
        # 'case_type':'CF',

    }
    
    result = requests.post(searchdirect_url, data)

    result_json = result.json()

    return result_json

def search_pacer(docketnum, court):
    url = "https://www.docketalarm.com/api/v1/searchpacer/"

    data = {
        'login_token':get_json.authenticate(),
        'client_matter':"",
        # 'party_name':party_name,
        'docket_num':docketnum,
        'court_region': court,
        # 'case_type':'CF',

    }
    
    result = requests.get(url, data)

    result_json = result.json()

    return result_json