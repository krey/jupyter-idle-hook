import requests
import json
import dateutil.parser
from dateutil.tz import tzutc
import datetime
import os
import humanize

valid_execution_states = {'starting', 'idle', 'busy'}

from typing import List, TypedDict

class Session(TypedDict):
    path: str
    last_activity: datetime.datetime
    execution_state: str

def get_sessions(url: str, token: str) -> List[Session]:
    """
    return sessions sorted by last activity
    """
    sessions_url = f'{url}api/sessions'
    response = requests.get(sessions_url, params={'token': token})
    assert(response.status_code == 200)
    sessions_raw = json.loads(response.text)
    sessions = []
    for session_raw in sessions_raw:
        session = Session(
            path = session_raw['path'],
            last_activity = dateutil.parser.isoparse(session_raw['kernel']['last_activity']),
            execution_state = session_raw['kernel']['execution_state']
        )
        assert(session['execution_state'] in valid_execution_states)
        sessions.append(session)

    sessions.sort(key=lambda session: session['last_activity'], reverse=True)
    return sessions

def test_running(sessions: List[Session], url: str) -> bool:
    running = [session for session in sessions if session['execution_state'] != 'idle']
    if len(running) == 0:
        message = f"No notebooks currently running on {url}"
    else:
        plural = '' if len(running) == 1 else 's'
        message_lines = [f"{len(running)} notebook{plural} running on {url}"]
        for session in running:
            message_lines.append(f" - {session['path']}: {session['execution_state']}")
        message = os.linesep.join(message_lines)

    print(message)
    return len(running) > 0
    
def test_active(sessions: List[Session], url: str, timeout: datetime.timedelta) -> bool:
    now = datetime.datetime.now(tzutc())
    active = [session for session in sessions if session['last_activity'] >= now - timeout]
    if len(active) == 0:
        message = f"No notebooks active in {humanize.naturaldelta(timeout)} on {url}"
    else:
        plural = '' if len(active) == 1 else 's'
        message_lines = [f"{len(active)} notebook{plural} active in {humanize.naturaldelta(timeout)} on {url}"]
        for session in active:
            message_lines.append(f" - {session['path']}: {humanize.naturaldelta(now-session['last_activity'])}")
        message = os.linesep.join(message_lines)

    print(message)
    return len(active) > 0

