import requests
import pandas as pd
import datetime
import numpy as np
from matplotlib import pyplot
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
    payload = {"state": state}
    r = requests.get("https://covidtracking.com/api/states/daily", params=payload)
    res = r.json()
    df = pd.DataFrame(res)
    interested_fields = ['date', 'state', 'positiveIncrease', 'totalTestResultsIncrease']
    df = df[interested_fields]
    df['positive_ratio'] = ""
    df['positive_ratio'].loc[df['totalTestResultsIncrease'] > 0] = df['positiveIncrease']/df['totalTestResultsIncrease']
    df['positive_ratio'].loc[df['totalTestResultsIncrease'] == 0] = 1

    print(df[['date', 'positive_ratio']])

# analyze()
get_data_state('CA')