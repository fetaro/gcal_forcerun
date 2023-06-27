import datetime
import logging
import os.path
import pickle
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from gcal_forcerun.conf import FORCERUN_EVENT_IDS_PATH, TOKEN_PATH, CREDENTIAL_APTH, API_MAX_RESULT, FORCERUN_MIN
from gcal_forcerun.event_parser import Zoom, GoogleMeet, Teams

TZ_JST = datetime.timezone(datetime.timedelta(hours=9))



# ロガー
log_format = logging.Formatter("%(asctime)s [%(levelname)8s] %(message)s")
logger = logging.getLogger()
if "DEBUG" in os.environ:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(log_format)
logger.addHandler(stdout_handler)



class Db:
    """
    強制開始したイベントIDを記録しておくDB
    """

    @staticmethod
    def save_id(id):
        logger.info(f"save id {id} to {FORCERUN_EVENT_IDS_PATH}")
        with open(FORCERUN_EVENT_IDS_PATH, "w") as f:
            f.write(id + "\n")

    @staticmethod
    def is_include(id):
        if not FORCERUN_EVENT_IDS_PATH.exists():
            # 初回は作る
            FORCERUN_EVENT_IDS_PATH.touch()
            os.chmod(FORCERUN_EVENT_IDS_PATH, 0o755)
            logger.info(f"created {FORCERUN_EVENT_IDS_PATH}")
        with open(FORCERUN_EVENT_IDS_PATH, "r") as f:
            for line in f.readlines():
                if line.find(id) > -1:
                    return True
        return False


def get_credentials() -> Credentials:
    """
    secret/credentails.jsonをもとにGoogleカレンダーAPIのトークンを取得する。
    トークンがない場合はブラウザによるOauth2認証を行う。
    取得したトークンは保存しておき、有効な限りそれを使う。
    このコードは https://developers.google.com/calendar/quickstart/python 参照にして作成した
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # ブラウザを用いて認証しトークンを取得
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIAL_APTH, ['https://www.googleapis.com/auth/calendar.readonly'])
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)
            os.chmod(TOKEN_PATH, 0o755)
            logger.info(f"make {TOKEN_PATH}")
    return creds


def call_calender_api(creds):
    service = build('calendar', 'v3', credentials=creds, cache_discovery=False)
    events_result = service.events().list(
        calendarId='primary',
        timeMin=datetime.datetime.utcnow().isoformat() + 'Z',  # 'Z' indicates UTC time,
        maxResults=API_MAX_RESULT,
        singleEvents=True,
        orderBy='startTime',
    ).execute()
    return events_result


def main():
    credentials: Credentials = get_credentials()
    results = call_calender_api(credentials)
    event_dict_list = results.get('items', [])
    if not event_dict_list:
        logger.info('No upcoming events found.')
    for event_dict in event_dict_list:
        for event in [Zoom(event_dict), GoogleMeet(event_dict), Teams(event_dict)]:
            if event.is_online_meeting():
                time_to_start_sec = event.time_to_start_sec()
                if (time_to_start_sec < 0):
                    logger.info(f"[already started] {event}")
                elif (time_to_start_sec < FORCERUN_MIN * 60):
                    logger.info(f"[start in {FORCERUN_MIN} min] {event}")
                    if Db.is_include(event.id):
                        # 一度強制起動しているため、スキップ
                        logger.info("skip")
                    else:
                        # 強制起動
                        logger.info("open event url")
                        event.open_event_url()
                        Db.save_id(event.id)
                else:
                    logger.info(f"[still ahead    ] {event}")


if __name__ == '__main__':
    main()
