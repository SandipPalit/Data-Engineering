"""
Description:        I created a blank dataframe with the necessary columns. Then I extracted the details from each of
                    the JSON files and appended to the dataframe. Finally, performed some data cleaning like
                    removing nulls, removing duplicates, and sorting the values based on Release Date.
                    I also maintained a log.csv file to monitor the execution and track the errors.
Python Libraries:   datetime, requests, json, pandas, os
Input files:        key.json, year_page.json, log.csv
Output files:       movieDataset.csv, log.csv
Author:             Sandip Palit
"""

import datetime
import requests
import json
import pandas as pd
import os

# ------------------------------------------------------------------
#                         Monitoring section
# ------------------------------------------------------------------

log = pd.read_csv('../Storage/3_Monitoring/log.csv')
start_time = datetime.datetime.utcnow()
errorCount = 0


# ------------------------------------------------------------------
#                         Transformation section
# ------------------------------------------------------------------

api_key = json.load(open("../Storage/0_Secrets/key.json"))['key']
URL = "https://api.themoviedb.org/3/genre/movie/list?api_key=" + api_key + "&language=en-US"

response = requests.get(url=URL)
genre_dictionary = {}
for genre in response.json()['genres']:
    genre_dictionary[genre['id']] = genre['name']

col_names = ['ReleaseDate', 'Title', 'Overview', 'Genre', 'VoteAverage', 'VoteCount']
dataframe = pd.DataFrame(columns=col_names)
path = '../Storage/1_Raw_Zone/'

for file_name in os.listdir(path):
    eachFile = open(path + file_name)
    data = json.load(eachFile)
    for movie_details in data['results']:
        try:
            details = {'ReleaseDate': movie_details['release_date'],
                       'Title': movie_details['title'],
                       'Overview': movie_details['overview'],
                       'Genre': [genre_dictionary[genre_id] for genre_id in movie_details['genre_ids']],
                       'VoteAverage': movie_details['vote_average'],
                       'VoteCount': movie_details['vote_count']}
            if len(details['Genre']) == 0:  # Replacing blank Genre list with None, so that they can be dropped.
                details['Genre'] = None
            dataframe = dataframe.append(details, ignore_index=True)
        except:
            print('Transformation failed within File: ', str(file_name))
            errorCount += 1

dataframe = dataframe.dropna(axis=0)
dataframe = dataframe.drop_duplicates(subset="Overview")
dataframe = dataframe.sort_values('ReleaseDate')
dataframe.to_csv('../Storage/2_Curated_Zone/movieDataset.csv', index=False)


# ------------------------------------------------------------------
#                         Monitoring section
# ------------------------------------------------------------------

end_time = datetime.datetime.utcnow()
duration = str(end_time - start_time).split(".")[0]
log_details = {'Stage': "Transformation",
               'StartTime': start_time.strftime("%H:%M:%S"),
               'EndTime': end_time.strftime("%H:%M:%S"),
               'Duration': duration,
               'ErrorCount': errorCount}

log = log.append(log_details, ignore_index=True)
log.to_csv('../Storage/3_Monitoring/log.csv', index=False)
