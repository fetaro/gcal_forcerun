import datetime
import os.path
import re
from abc import ABCMeta, abstractmethod
from pathlib import Path

from gcal_forcerun.conf import LAUNCH_APPLICATION

TZ_JST = datetime.timezone(datetime.timedelta(hours=9))
THIS_DIR = Path(__file__).parent.resolve()


class Event(metaclass=ABCMeta):
    """
    Googleカレンダーのイベント
    """

    def __init__(self, event):
        self.id = event["id"]
        self.event = event
        self.start_at = datetime.datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
        self.summary = event['summary']
        self.url = self._parse_url()

    @abstractmethod
    def _parse_url(self) -> str:
        pass

    def is_online_meeting(self) -> bool:
        return self.url != ""

    def open_event_url(self):
        os.system(f"open -a '{LAUNCH_APPLICATION}' {self.url}")

    def __str__(self):
        return f"{self.start_at} {self.summary} {self.url}"

    def time_to_start_sec(self):
        # あと何秒で開始するか
        return self.start_at.timestamp() - datetime.datetime.now(tz=TZ_JST).timestamp()


class GoogleMeet(Event):
    """
    GoogleMeetのイベント
    """

    def _parse_url(self) -> str:
        for entry_point in self.event.get("conferenceData", {}).get("entryPoints", []):
            if entry_point['entryPointType'] == 'video':
                return entry_point['uri']
        return ""


class Zoom(Event):
    """
    Zoomのイベント
    """

    def _parse_url(self) -> str:
        """
        locationもしくは本文にURLがあれば抽出する
        """
        location = self.event.get("location", "")
        if location.find("zoom.us") > -1:
            return location
        description = self.event.get("description", "")
        reg_url = re.compile(r"<a href=\"(https://zoom.us/.*)\">")
        _m = reg_url.search(description)
        if _m is not None:
            return _m.group(1)
        return ""


class Teams(Event):
    """
    Teamsのイベント
    """

    def _parse_url(self) -> str:
        """
        本文にURLがあれば抽出する
        """
        description = self.event.get("description", "")
        reg_url = re.compile(r'<(https://teams.microsoft.com/l/meetup-join.*)>')
        _m = reg_url.search(description)
        if _m is not None:
            return _m.group(1)
        return ""
