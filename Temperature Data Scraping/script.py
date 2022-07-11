# Importing Necessary Libraries

"""
I installed the following python libraries:
* requests for the API calls.
* bs4 for Web Scraping.
* sqlite3 for Database.
* matplotlib for Plotting.
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
from pandas import DataFrame
import matplotlib.pyplot as plt



# Ingesting Data and Loading data in the Database

"""
Firstly, I created a 'temperature_data' database using sqlite3.
For every month,
    * Created a new table with the month name, like 'temperature_january'.
    * Ingested the data from the internet through web scraping.
    * Parsed the response using BeautifulSoup.
    * Extracted each Location, Maximum Temperature and Minimum Temperature.
    * Stored them in the table using sqlite3.
"""

months = ['january', 'february', 'march', 'april', 'may', 'june',
          'july', 'august', 'september', 'october', 'november', 'december']
databaseConnection = sqlite3.connect('temperature_data.db')
for month in months:
    try:
        databaseConnection.execute('drop table temperature_' + month + ';')
    except:
        print("Cannot delete table: " + month)
    finally:
        createTableStatement = 'create table temperature_' + month + ' (location varchar2(20), ' + month[:3].upper() \
                               + '_MaxTemp number, ' + month[:3].upper() + '_MinTemp number);'
        databaseConnection.execute(createTableStatement)
        print("Successfully created table: " + month)
    websiteLink = "https://www.skymetweather.com/holidaydestinations/seasonal-forecast/"
    response = requests.get(websiteLink + month)  # Extract
    soup = BeautifulSoup(response.content, "html.parser")
    for item in soup.find_all(class_=["bestplacesItem radius5"]):
        location = item.find(class_='bestplacesName ellipsis').text
        maxTemp = item.find_all(class_='c')[0].text
        minTemp = item.find_all(class_='c')[1].text
        try:
            insertStatement = 'insert into temperature_' + month + ' values (\'' + location + '\',' + maxTemp + ',' \
                              + minTemp + ');'
            databaseConnection.execute(insertStatement)  # Load
        except:
            print(
                "Insert data failed: " + insertStatement)
    databaseConnection.commit()
    print("Operations completed on table: " + month)



# Transforming Data

"""
I did a simple transformation as I wanted to keep the data as original as possible.
I joined all the tables based on the Location column.
"""

databaseConnection = sqlite3.connect('temperature_data.db')
selectTableNamesStatement = 'select name from sqlite_master where type= "table";'
tableNames = [''.join(tableName) for tableName in databaseConnection.execute(selectTableNamesStatement).fetchall()]
selectStatement = 'select * from '
for tableNum in range(len(tableNames)):
    if tableNum == 0:
        selectStatement += tableNames[tableNum]
    else:
        selectStatement += ' natural join ' + tableNames[tableNum]
selectStatement += ';'
df = DataFrame(databaseConnection.execute(selectStatement).fetchall())  # Transform
df.columns = [item[0] for item in databaseConnection.execute(selectStatement).description]



# Storing Data and Visualizing Data

"""
I stored the entire dataframe in the destination folder.
I took a single location ,i.e, Kolkata and visualized the variation of seasonal temperature.
"""

df.to_csv("./destination/temperatureData.csv", index=False)
df1 = df[df['location'] == 'Kolkata']
monthList = []
maxTempList = []
minTempList = []
for column in df1.columns:
    if column[-7:] == 'MaxTemp':
        monthList.append(column[:3])
        maxTempList.append(df1[column].values[0])
    elif column[-7:] == 'MinTemp':
        minTempList.append(df1[column].values[0])
plt.plot(monthList, maxTempList, color='red', label="Maximum Temperature")
plt.plot(monthList, minTempList, color='blue', label="Minimum Temperature")
plt.fill_between(monthList, maxTempList, minTempList, color='green', alpha=0.1)
plt.xlabel("Month", fontsize=10)
plt.ylabel("Temperature (in Celsius)", fontsize=10)
plt.title('Seasonal Temperature Forecast of Kolkata', fontsize=16)
plt.rcParams["figure.figsize"] = (24, 8)
plt.legend(loc="upper right", prop={'size': 12})
plt.grid(axis='y')
plt.show()
