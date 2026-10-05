import asyncio
import uuid

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.config import settings

TIMEZONE = "Asia/Kolkata"


def _calendar():
    creds = Credentials(
        None,
        refresh_token=settings.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=["https://www.googleapis.com/auth/calendar.events"],
    )
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def _times(date, start_time, end_time):
    return (
        {"dateTime": f"{date}T{str(start_time)[:5]}:00", "timeZone": TIMEZONE},
        {"dateTime": f"{date}T{str(end_time)[:5]}:00", "timeZone": TIMEZONE},
    )


def _create(summary, date, start_time, end_time, attendee_emails):
    start, end = _times(date, start_time, end_time)
    event = {
        "summary": summary,
        "start": start,
        "end": end,
        "attendees": [{"email": e} for e in attendee_emails if e],
        "conferenceData": {
            "createRequest": {
                "requestId": str(uuid.uuid4()),
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }
    created = (
        _calendar()
        .events()
        .insert(
            calendarId="primary",
            body=event,
            conferenceDataVersion=1,  # required, otherwise no Meet link is created
            sendUpdates="all",        # emails the invite to attendees
        )
        .execute()
    )
    return created["hangoutLink"], created["id"]


def _update_time(event_id, date, start_time, end_time):
    start, end = _times(date, start_time, end_time)
    _calendar().events().patch(
        calendarId="primary",
        eventId=event_id,
        body={"start": start, "end": end},
        sendUpdates="all",
    ).execute()


def _delete(event_id):
    _calendar().events().delete(
        calendarId="primary", eventId=event_id, sendUpdates="all"
    ).execute()


# The Google client is synchronous, so run each call in a worker thread
# to avoid blocking FastAPI's event loop.
async def create_meet_event(summary, date, start_time, end_time, attendee_emails):
    return await asyncio.to_thread(_create, summary, date, start_time, end_time, attendee_emails)


async def update_meet_event_time(event_id, date, start_time, end_time):
    await asyncio.to_thread(_update_time, event_id, date, start_time, end_time)


async def delete_meet_event(event_id):
    await asyncio.to_thread(_delete, event_id)