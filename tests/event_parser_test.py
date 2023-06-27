import pprint
import sys
from pathlib import Path

# 親ディレクトリをアプリケーションのホーム(${app_home})に設定
app_home = str(Path(__file__).parents[1])
# ${app_home}をライブラリロードパスに追加
sys.path.append(app_home)

from gcal_forcerun.main import Zoom, GoogleMeet, Teams


def test_zoom_description_parse():
    event_dict = {'description': '<a '
                                 'href="https://zoom.us/j/12345?pwd=xxx"><u>https://zoom.us/j/12345?pwd=xxx</u></a>',
                  'id': 'xxx',
                  'start': {'dateTime': '2023-06-26T10:30:00+09:00', 'timeZone': 'Asia/Tokyo'},
                  'summary': 'summary-1',
                  }
    z = Zoom(event_dict)
    assert z.is_online_meeting()
    assert z.url == 'https://zoom.us/j/12345?pwd=xxx'
    assert z.summary == 'summary-1'
    assert not GoogleMeet(event_dict).is_online_meeting()
    assert not Teams(event_dict).is_online_meeting()


def test_zoom_description_parse2():
    event_dict = {'description': '──────────<br><br>さんがあなたを予約されたZoomミーティングに招待しています。<br><br>Zoomミーティングに参加する<br><a '
                                 'href="https://zoom.us/j/223344?pwd=yyy">https://zoom.us/j/223344?pwd=yyy</a><br><br>ミーティングID: '
                                 '123 4567 7890<br>パスコード: '
                                 '123456<br><br><br>──────────',
                  'id': 'xxx',
                  'start': {'dateTime': '2023-06-28T12:00:00+09:00', 'timeZone': 'Asia/Tokyo'},
                  'summary': 'summary-2'}
    z = Zoom(event_dict)
    assert z.is_online_meeting()
    assert z.summary == 'summary-2'
    assert z.url == 'https://zoom.us/j/223344?pwd=yyy'
    assert not Teams(event_dict).is_online_meeting()
    assert not GoogleMeet(event_dict).is_online_meeting()


def test_teams_description_parse():
    event_dict = {'description': '________________________________________________________________________________\n'
                                'Microsoft Teams ミーティング\n'
                                'コンピュータ、モバイルアプリケーション、またはルームデバイスで参加する\n'
                                'ここをクリックして会議に参加してください<https://teams.microsoft.com/l/meetup-join/aaaaaaa>\n'
                                '会議 ID: 123 123 123 123\n'
                                'パスコード: aaaaaa\n'
                                'Teams '
                                'のダウンロード<https://www.microsoft.com/en-us/microsoft-teams/download-app> '
                                '| Web '
                                'に参加<https://www.microsoft.com/microsoft-teams/join-a-meeting>\n'
                                '詳細情報ヘルプ<https://aka.ms/JoinTeamsMeeting> | '
                                '会議のオプション<https://teams.microsoft.com/meetingOptions/?organizerId=ss>\n'
                                '________________________________________________________________________________\n'
                                '\n',
                  'id': 'xxx',
                  'start': {'dateTime': '2023-06-28T14:00:00+09:00', 'timeZone': 'Asia/Dili'},
                  'summary': 'Microsoft Teams 会議'}
    t = Teams(event_dict)
    assert t.is_online_meeting()
    assert t.url == "https://teams.microsoft.com/l/meetup-join/aaaaaaa"
    assert t.summary == 'Microsoft Teams 会議'
    assert not GoogleMeet(event_dict).is_online_meeting()
    assert not Zoom(event_dict).is_online_meeting()


def test_google_meet_parse():
    event_dict = {'conferenceData': {'conferenceId': 'aaa-bbbb-ccc',
                                     'entryPoints': [{'entryPointType': 'video',
                                                      'label': 'meet.google.com/aaa-bbbb-ccc',
                                                      'uri': 'https://meet.google.com/aaa-bbbb-ccc'},
                                                     {'entryPointType': 'more',
                                                      'pin': '123456789',
                                                      'uri': 'https://tel.meet/aaa-bbbb-ccc?pin=123456789'},
                                                     {'entryPointType': 'phone',
                                                      'label': '+81 3-1111-1111',
                                                      'pin': '123456789',
                                                      'regionCode': 'JP',
                                                      'uri': 'tel:+81-3-1111-1111'}]},
                  'id': 'xxx',
                  'start': {'dateTime': '2023-06-28T16:30:00+09:00', 'timeZone': 'Asia/Tokyo'},
                  'summary': 'Daily Sync'}
    pprint.pprint(event_dict)
    z = Zoom(event_dict)
    m = GoogleMeet(event_dict)
    t = Teams(event_dict)
    assert m.is_online_meeting()
    assert m.summary == 'Daily Sync'
    assert m.url == 'https://meet.google.com/aaa-bbbb-ccc'
    assert not z.is_online_meeting()
    assert not t.is_online_meeting()
