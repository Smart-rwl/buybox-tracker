import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_CREDS

def init_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_CREDS, scope)
    client = gspread.authorize(creds)

    return client.open_by_key("1v586BKfmCZSQW9cNV02-vbED3qoRveuRIHOTnz8dffY").sheet1
