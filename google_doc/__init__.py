import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd



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
            "Kikio\n[DNC]"  : "Kikio", 
            "Mira\n[RDM]"   : "Mira"}
    df = pd.DataFrame(records)
    df.drop(["Datum", "Zeiten"], axis=1, inplace=True)
    df.rename(columns=cols, inplace=True)
    return df