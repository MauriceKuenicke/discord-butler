import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np



class GoogleDoc:
    def __init__(self):
        self.scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        self.client = None
        self.records = None

    def authorize_client(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name('cred/client_secret.json', self.scope)
        self.client = gspread.authorize(creds)

    def open_by_url(self, url):  
        sheet = self.client.open_by_url(url).sheet1
        self.records = sheet.get_all_records()
        return self.records


def handle_records(records):
    cols = {"Dimi\n[WAR]"   : "Dimi",  
            "K'shefu\n[GNB]": "K'shefu", 
            "Minah\n[AST]"  : "Minah",
            "Test 1\n[WHM]": "Test 1", 
            "Kikio\n[DNC]"  : "Kikio", 
            "Mira\n[RDM]"   : "Mira",
            "Test 2 \n[MCH]": "Test 2",
            "Test 3 \n[SAM]": "Test 3"}
    df = pd.DataFrame(records)
    df.drop(["Zeiten"], axis=1, inplace=True)
    df.rename(columns=cols, inplace=True)
    return df


def calculate_available_days(df_copy):
    df_copy.drop([""], axis=1, inplace=True)
    start_df = pd.DataFrame()
    end_df = pd.DataFrame()
    df_copy.replace(r'^\s*$', "-", regex=True, inplace=True)
    df_copy.replace(r'x', "-", inplace=True)
    df_copy.replace(r'xxx', "-", inplace=True)
    for player in df_copy.columns[2:-1]:
        start_df.loc[:,player+"_start"] = df_copy[player].apply(lambda x: get_start_time(x))
        end_df.loc[:,player+"_end"] = df_copy[player].apply(lambda x: get_end_time(x))

    df_copy.loc[:,"start_time"] = start_df.max(axis=1)
    df_copy.loc[:,"end_time"] = end_df.min(axis=1)
    df_copy.loc[:,"blocked"] = ~(df_copy != '-').all(1)
    return df_copy[~df_copy["blocked"]]


def get_start_time(x):
    if x.strip() == "?":
        return 10
    elif x.strip() == "" or x.strip() == "-":
        return np.nan
    else:
        start = x.strip().split("-")[0]
        if start == "?" or start == "":
            return 10
        else:
            return int(start)
    
def get_end_time(x):
    if x.strip() == "?":
        return 24
    elif x.strip() == "" or x.strip() == "-":
        return np.nan
    else:
        end = x.strip().split("-")[1]
        if end == "?" or end == "":
            return 24
        else:
            return int(end)