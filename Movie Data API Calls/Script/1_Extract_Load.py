"""
Description:        I made iterative calls to the TMDB website, to get the content of the first 500 pages within a year
                    range of 2012 to 2021. Then saved the response in a separate JSON file for each API call.
                    I also maintained a log.csv file to monitor the execution and track the errors.
Python Libraries:   datetime, os, requests, json, pandas
Input files:        key.json
Output files:       year_page.json, log.csv
Author:             Sandip Palit
"""

import datetime
import os
import requests
import json
import pandas as pd

# ------------------------------------------------------------------
#                         Monitoring section
# ------------------------------------------------------------------

log_col_names = ['Stage', 'StartTime', 'EndTime', 'Duration', 'ErrorCount']
log = pd.DataFrame(columns=log_col_names)
start_time = datetime.datetime.utcnow()
errorCount = 0


# ------------------------------------------------------------------
#                         Extraction & Loading section
# ------------------------------------------------------------------

api_key = json.load(open("../Storage/0_Secrets/key.json"))['key']

for year in range(2012, 2022):
    for page in range(1, 501):
        try:
            url = "https://api.themoviedb.org/3/discover/movie?api_key=" + api_key \
                  + "&language=en-US&sort_by=popularity.desc&include_adult=false&page=" \
                  + str(page) + "&year=" + str(year)
            response = requests.get(url=url)  # Extraction part
            responseJson = response.json()
            with open("../Storage/1_Raw_Zone/" + str(year) + "_" + str(page) + ".json", 'w') as json_file:
                json.dump(responseJson, json_file)  # Loading part
        except:
            print('API call failed for Year: ', str(year), ' & Page: ', str(page))
            errorCount += 1


# ------------------------------------------------------------------
#                         Monitoring section
# ------------------------------------------------------------------

end_time = datetime.datetime.utcnow()
duration = str(end_time - start_time).split(".")[0]
log_details = {'Stage': "Extraction & Loading",
               'StartTime': start_time.strftime("%H:%M:%S"),
               'EndTime': end_time.strftime("%H:%M:%S"),
               'Duration': duration,
               'ErrorCount': errorCount}

log = log.append(log_details, ignore_index=True)
log.to_csv('../Storage/3_Monitoring/log.csv', index=False)
