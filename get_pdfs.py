import os
import json
from progress.bar import IncrementalBar
import requests

def download_pdfs():
    """ Scans through JSON files in results folder,
        downloads any PDF links listed in the JSON data,
        and outputs the PDF's to the result_filtered folder
    """
    directory = os.path.join(os.getcwd(), 'result')
    max = len(os.listdir(directory))
    bar = IncrementalBar("Gathering Links", max=max)
    for file in os.listdir(directory):
        bar.next()
        filename = os.fsdecode(file)
        if filename.endswith(".JSON") or filename.endswith(".json"): 
            path = os.path.join(directory, filename)
            
            base_filename = filename.split(".")[0]
            # print(base_filename)

            # print(path)
            with open(path) as jsonFile:
                jsonObject = json.load(jsonFile)
                # print(jsonObject)
                if "docket_report" in jsonObject:
                    docket_report = jsonObject['docket_report']
                    for item in docket_report:
                        if 'link' in item:
                            link = item['link']
                            # print(link)
                            r = requests.get(link, stream=True)
                            filename = f"{item['number']}.pdf"
                            pathname = os.path.join(os.getcwd(),'result_filtered', base_filename, filename)
                            dirpath = os.path.join(os.getcwd(),'result_filtered', base_filename)
                            if not os.path.exists(dirpath):
                                os.makedirs(dirpath)
                            else:
                                pass
                            with open(pathname, "wb") as f:
                                f.write(r.content)
                            pass
                        else:
                            pass
                        if 'exhibits' in item:
                            exhibits = item['exhibits']
                            for exhibit in exhibits:
                                if 'link' in exhibit:
                                    link = exhibit['link']

                                else:
                                    pass
                        else:
                            pass


                else:
                    pass       
                jsonFile.close()
            continue
        else:
            continue

