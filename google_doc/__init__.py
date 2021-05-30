import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import os
import utils
import datetime


class GoogleDoc:
    def __init__(self):
        self.scope = ['https://www.googleapis.com/auth/spreadsheets',
                      "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        self.client = None
        self.records = None

    def authorize_client(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'cred/client_secret.json', self.scope)
        self.client = gspread.authorize(creds)

    def open_by_url(self, url):
        sheet = self.client.open_by_url(url).sheet1
        self.records = sheet.get_all_records()
        return self.records


def request_GoogleDocRecords(week):
    gd = GoogleDoc()
    gd.authorize_client()
    records = gd.open_by_url(os.getenv("DOC_LINK"))
    df = preprocess_records(records, week)
    return df


def preprocess_records(records, week):
    df = pd.DataFrame(records)
    df.drop(["Zeiten", ""], axis=1, inplace=True)
    df.loc[:, "Datum"] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')
    df.loc[:, 'Datum'] = df['Datum'].dt.date
    df.columns = [x.split("\n")[0].strip() for x in df.columns]
    df.replace(r'^\s*$', "-", regex=True, inplace=True)
    df.replace(r'x', "-", inplace=True)
    df.replace(r'xxx', "-", inplace=True)

    if week == "next":
        raid_week_starts = utils.get_next_weekday_date(
            datetime.datetime.now().date(), 1)
        raid_week_ends = raid_week_starts + datetime.timedelta(6)
    elif week == "current":
        raid_week_starts = utils.get_last_weekday_date(
            datetime.datetime.now().date(), 1)
        raid_week_ends = raid_week_starts + datetime.timedelta(6)

    df = df[(df['Datum'] >= raid_week_starts)
            & (df['Datum'] <= raid_week_ends)]
    return df


def calculate_available_days(df_copy):
    start_df = pd.DataFrame()
    end_df = pd.DataFrame()
    block_number = np.array([0]*7)
    df_copy.replace(r'^\s*$', "-", regex=True, inplace=True)
    df_copy.replace(r'x', "-", inplace=True)
    df_copy.replace(r'xxx', "-", inplace=True)
    for player in [x for x in df_copy.columns if x not in ["Wochentag", "Datum"]]:
        start_df.loc[:, player +
                     "_start"] = df_copy[player].apply(lambda x: get_start_time(x))
        end_df.loc[:, player +
                   "_end"] = df_copy[player].apply(lambda x: get_end_time(x))
        block_number += df_copy[player].isin(["-"]).astype(int).values

    df_copy.loc[:, "start_time"] = start_df.max(axis=1)
    df_copy.loc[:, "end_time"] = end_df.min(axis=1)
    df_copy.loc[:, "blocked"] = ~(df_copy != '-').all(1)
    df_copy.loc[:, "blocked_by"] = block_number
    return df_copy[~df_copy["blocked"]], df_copy[df_copy["blocked_by"] == 1]


def get_start_time(x):
    if x.strip() == "?":
        return 10
    elif x.strip() == "" or x.strip() == "-":
        return np.nan
    else:
        start = x.strip().split("-")[0]
        if start.strip() == "?" or start == "":
            return 10
        else:
            if len(start.strip().split(":")) == 2:
                return float(start.strip().split(":")[0]) + 0.5
            return int(start)


def get_end_time(x):
    if x.strip() == "?":
        return 24
    elif x.strip() == "" or x.strip() == "-":
        return np.nan
    else:
        end = x.strip().split("-")[1]
        if end.strip() == "?" or end == "":
            return 24
        else:
            if len(end.strip().split(":")) == 2:
                return float(end.strip().split(":")[0]) + 0.5
            return int(end)


def get_slacking_player(df):
    playerL = list()
    for player in [x for x in df.columns if x not in ["Wochentag", "Datum"]]:
        missingDays = df[player].value_counts().get("-", 0)
        if missingDays > 5:
            playerL.append(player)
    return playerL
