import requests
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
from urllib.error import HTTPError


#Ignore this
def get_prev_date(date):
    dt = datetime.datetime.strptime(date, '%Y%m%d')
    prev_date_obj = dt - datetime.timedelta(days=1)
    return prev_date_obj.strftime('%Y%m%d')


# Ignore this
def get_change_day(date=None):
    """Gives the change in positive cases from previous day to given date. If no date is give, uses today's date"""
    if not date:
        date = datetime.datetime.today().strftime('%Y%m%d')
    interested_fields = ['state', 'positiveIncrease', 'totalTestResultsIncrease']

    reference = get_response(date)
    ref_df = pd.DataFrame(reference)
    ref_df = ref_df[interested_fields]

    previous = get_response(get_prev_date(date))
    prev_df = pd.DataFrame(previous)
    prev_df = prev_df[interested_fields]

    ref_df = pd.merge(prev_df, ref_df, on="state", suffixes=("_prev", "_cur"))


#Ignore this
def get_response(date, state=None):
    """Gives the json response of a query for a given date, if no date provided, uses today's date"""
    payload = {"date": date}
    if state:
        payload["state"] = state

    r = requests.get("https://covidtracking.com/api/states/daily.json", params=payload)
    if r.status_code == 200:
        return r.json()
    else:
        raise HTTPError


# USE THIS
def get_data_state(state):
    # TODO: clean up the code
    # TODO: Do this for all other states
    # TODO: Do this for the other function
    # Call the API to get data
    payload = {"state": state}
    r = requests.get("https://covidtracking.com/api/states/daily", params=payload)
    res = r.json()

    # Convert into a pandas dataframe
    df = pd.DataFrame(res)

    # Get relevant fields
    interested_fields = ['date', 'state', 'positiveIncrease', 'totalTestResultsIncrease']
    df = df[interested_fields]

    # Calculate our metric: positiveIncrease / totalTestResultsIncrease
    df['positive_ratio'] = np.nan
    df['positive_ratio'].loc[df['totalTestResultsIncrease'] > 0] = df['positiveIncrease']/df['totalTestResultsIncrease']

    # Drop all other columns we don't need anymore
    df = df[['date', 'positive_ratio']]

    # Interpolate the missing values. This fills up missing values with the mean of the next and prev non missing value
    df['inter'] = df['positive_ratio'].interpolate()

    # Convert the date to a date format
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d', errors='ignore')

    # Calculate 5 day moving average on the data. We reverse the data because the
    # MA function begins the MA calculation from top row of the data.
    df = df.iloc[::-1]
    df['rolling_ma'] = df['inter'].rolling(window=5).mean()

    ax = plt.gca()

    # Plot the data
    df.plot(kind='line', x='date', y='rolling_ma', ax=ax, title=state)
    plt.xlabel("Date")
    plt.ylabel("Ratio of test showing +ve")
    plt.show()
    print(df)

# analyze()
get_data_state('TX')