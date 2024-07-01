import os
import pathlib
import pickle
import uuid
from typing import Dict, List
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import yaml

class EventPlanner:
    def __init__(self, guests: Dict[str, str], schedule: Dict[str, str]):
        self.guests = [{"email": email} for email in guests.values()]
        self.schedule = schedule
        self.service = self._authorize()
        self.event_result = self._plan_event(self.guests, self.schedule, self.service)

    def _authorize(self) -> build:
        scopes = ["https://www.googleapis.com/auth/calendar"]
        config_file = pathlib.Path("./yaml/config.yaml")
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        flow = InstalledAppFlow.from_client_secrets_file(
            pathlib.Path("./client_secret.json"), scopes
        )
        credentials = flow.run_local_server(port=0)

        calendar_service = build("calendar", "v3", credentials=credentials)
        return calendar_service


    def _plan_event(self, attendees: List[Dict[str, str]], event_time: Dict[str, str], service: build) -> Dict:
        event = {
            "summary": "Test Meeting",
            "start": {"dateTime": event_time["start"]},
            "end": {"dateTime": event_time["end"]},
            "attendees": attendees,
            "conferenceData": {
                "createRequest": {
                    "requestId": f"{uuid.uuid4().hex}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
            "reminders": {"useDefault": True},
        }

        try:
            event_result = (
                service.events()
                .insert(calendarId="primary", sendNotifications=True, body=event, conferenceDataVersion=1)
                .execute()
            )
            return event_result
        except HttpError as error:
            print(f"Error creating event: {error}")
            return None


if __name__ == "__main__":
    planner = EventPlanner(
        {"test_guest": "test.guest@gmail.com"},
        {"start": "2020-07-31T16:00:00", "end": "2020-07-31T16:30:00"},
    )
    print(planner.event_result)
