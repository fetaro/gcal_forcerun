from pathlib import Path

THIS_DIR = Path(__file__).parent.resolve()

# オンライン会議の時間がこの分前になったら、自動的に起動する
FORCERUN_MIN = 2

# カレンダーAPIのcredentailsのパス
CREDENTIAL_APTH = THIS_DIR / "secret" / "credentials.json"

# イベントURLを起動するアプリケーション
LAUNCH_APPLICATION = '/Applications/Google Chrome.app'

# カレンダーAPIから最大何件取得するか
API_MAX_RESULT = 25

# APIトークンの保管場所
TOKEN_PATH = THIS_DIR / "work" / "token.pickle"

# 既に強制開始したイベントのIDを格納しておくファイルの場所
FORCERUN_EVENT_IDS_PATH = THIS_DIR / "work" / "forcerun_event_id.txt"
