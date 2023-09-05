from __future__ import print_function

import os.path
import requests
from bs4 import BeautifulSoup
import fake_useragent
import json
import gspread
import pickle
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1vRd3CxUpSzuYBujvHLHdtI2EL8nQ6FdqKTRuUP8JUX0'
SAMPLE_RANGE_NAME = 'Parsing!A1:G20000'

data_base={
    'first': 1,
    'id2':278200090968,
    'id': '#'
}

data_tiks={
    'id': 1
}

zapros='http://www.st-petersburg.vybory.izbirkom.ru/st-petersburg/ik_r_tree/278200090968?first=1&id2=278200090968&id=%23)'

class GoogleSheet:
    SPREADSHEET_ID = '1vRd3CxUpSzuYBujvHLHdtI2EL8nQ6FdqKTRuUP8JUX0'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = None

    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print('flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def updateRangeValues(self, range, values):
        data = [{
            'range': range,
            'values': values
        }]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
        result = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID, body=body).execute()
        print('{0} cells updated.'.format(result.get('totalUpdatedCells')))

def main():
    gs=GoogleSheet()

    session=requests.Session()
    base_link='http://www.st-petersburg.vybory.izbirkom.ru/st-petersburg/ik_r/278200090968'
    user=fake_useragent.UserAgent().random
    header = {'user-agent': user}

    response = session.get(zapros, headers=header, params=data_base)
    json_part=response.json()[0]
    child=json_part['children']# список Тиков
    iteration=2
    for item in child:
        Tik_value=[
            [item['text']]
        ]
        Tik_Range=f'Parsing!A{iteration}:A{iteration}'
        gs.updateRangeValues(Tik_Range, Tik_value)
        time.sleep(5)
        data_tiks['id']=item['id']
        r=requests.get(f"http://www.st-petersburg.vybory.izbirkom.ru/st-petersburg/ik_r_tree/?id={item['id']}", headers=header, params=data_tiks)
        json_tiks=r.json()
        for yik in json_tiks:
            time.sleep(5)
            Yik_value = [
                [yik['text']]
            ]
            yik_Range = f'Parsing!B{iteration}:B{iteration}'
            gs.updateRangeValues(yik_Range, Yik_value)
            yik_info=requests.get(f"http://www.st-petersburg.vybory.izbirkom.ru/st-petersburg/ik_r/{yik['id']}", headers=header).content
            soup=BeautifulSoup(yik_info, 'lxml')
            block = soup.find_all("tr")
            for call in block:
                if call.find("td"):
                    table_value = []
                    table_Range = f'Parsing!C{iteration}:F{iteration}'
                    for i in call.find_all("td"):
                        thing=str(i.text).replace("\t", '').replace("\n", '')
                        table_value.append(thing)
                    time.sleep(0.5)
                    gs.updateRangeValues(table_Range, [table_value])
                    iteration = iteration + 1


if __name__ == '__main__':
    main()





