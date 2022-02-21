import subprocess
import requests
from uuid import UUID
from typing import Union
from dataclasses import dataclass
from datetime import datetime as dt
from typing import List
from dataclasses import replace
from time import sleep
import os

@dataclass(frozen=True)
class InitialState():
    fileName: str
    APIkey: str
    nodes: List[str]
    unixTime: int
    unixEndTime: int

    @classmethod
    def from_data(cls, data):
        return cls(
            str(data['APIkey']),
            str(data['nodes']),
            int(data['unixTime']),
            int(data['unixEndTime'])
        )

@dataclass(frozen=True)
class DownloadPendingState():
    initial_state: InitialState
    export_id: UUID
    last_check: int

    @classmethod
    def from_data(cls, data):
        return cls(
            InitialState.from_data(data['initial_state']),
            UUID(data['export_id']),
            int(data['last_check']),
        )

@dataclass(frozen=True)
class DownloadFailedState():
    initial_state: InitialState
    fail_count: int
    fail_time: int
    fail_reason: str

    @classmethod
    def from_data(cls, data):
        return cls(
            InitialState.from_data(data['intial_state']),
            int(data['fail_count']),
            int(data['fail_time']),
            str(data['fail_reason']),
        )

@dataclass(frozen=True)
class DownloadReadyState():
    url: str
    export_id: UUID
    initial_state: InitialState

    @classmethod
    def from_data(cls, data):
        return cls(
            url = str(data['url']),
            initial_state = InitialState.from_data(data['initial_state']),
            export_id = UUID(str(data['export_id']))
        )

@dataclass(frozen=True)
class DownloadedState():
    APIkey: str
    nodes: List[str]
    unixTime: int
    unixEndTime: int
    export_id: UUID

    @classmethod
    def from_data(cls, data):
        return cls(
            str(data['APIkey']),
            str(data['nodes']),
            int(data['unixTime']),
            UUID(data['export_id']),
        )

State = Union[
    InitialState,
    DownloadPendingState,
    DownloadFailedState,
    DownloadReadyState,
    DownloadedState,
]

state_types = (
    InitialState,
    DownloadPendingState,
    DownloadFailedState,
    DownloadReadyState,
    DownloadedState,
)

rate_limited = False

def initiate_download(state: InitialState) -> Union[InitialState, DownloadPendingState, DownloadFailedState]:
    global rate_limited
    if rate_limited:
        return state

    url = 'https://sd.kcftech.com/public/exports/burstData?apiKey={}'.format(
        state.APIkey)
    data = {
        'NodeSerialNumbers': state.nodes,
        'StartTime': state.unixTime,
        'EndTime': state.unixEndTime,
        'SampleSize': 0,
        'EmbedMetadata': False
    }
    

    response = requests.post(
        url = url,
        params = {'APIkey' : state.APIkey},
        json = data,
        )

    if response.status_code == 429:
        print("Rate Limited | Patience is a virtue or something", response.text)
        rate_limited = True
        return state
    elif response.status_code != 200:
        failed_state = DownloadFailedState(
            initial_state = state,
            fail_count = 1,
            fail_time = int(dt.now().timestamp()),
            fail_reason = '[{}]: {}'.format(response.status_code, response.text)
            )
        print('initiate download failed', failed_state.fail_reason)
        return failed_state
    export_id = UUID(response.json())
    return DownloadPendingState(
        initial_state = state,
        export_id = export_id,
        last_check = int(dt.now().timestamp()))

def check_download(state: DownloadPendingState) -> Union[DownloadReadyState, DownloadPendingState, DownloadFailedState]:
    """ hit the status route and figure out what's going on """
    global rate_limited
    if rate_limited:
        return state
    print("still downloading")
    if dt.now().timestamp() - state.last_check < 10:
        print("Slow your roll, hoss.  You tried this less than ten seconds ago.")
        return state
    url = "https://sd.kcftech.com/public/exports/{export_id}/status?apiKey={api_key}"
    url = url.format(export_id=state.export_id, api_key=state.initial_state.APIkey)
    response = requests.get(url=url)
    if response.status_code == 429:
        rate_limited = True
        print("Slow your roll, hoss.  You tried this less than ten seconds ago.")
        return state
    if response.status_code == 404:
        fail_reason = "[404]: {}".format(response.text)
        print("Status route failed:", fail_reason)
        return DownloadFailedState(
            initial_state=state.initial_state,
            fail_count=1,
            fail_time=int(dt.now().timestamp()),
            fail_reason="[{}]: {}".format(response.status_code, response.text),
        )
    elif response.status_code != 200:
        fail_reason = "[{}]: {}".format(response.status_code, response.text)
        print("Status route failed:", fail_reason)
        return state
    status = response.json()
    if status['exportCompleted'] is True:
        print("Download ready for {}".format(state.initial_state.APIkey))
        return DownloadReadyState(
            status['downloadUrl'],
            state.export_id,
            state.initial_state,
        )
    print("Progress {} for {}".format(status['progress'], state.initial_state.nodes))
    return replace(state, last_check=dt.now().timestamp())


def get_data(state: DownloadReadyState) -> Union[DownloadedState, DownloadFailedState]:
    commandline = ['curl', state.url, '-o', state.initial_state.fileName]
    print(commandline)
    print(os.getcwd())
    returncode = subprocess.call(commandline)
    if returncode == 0:
        return DownloadedState(
            state.initial_state.APIkey,
            state.initial_state.nodes,
            state.initial_state.unixTime,
            state.initial_state.unixEndTime,
            state.export_id
        )
    return DownloadFailedState(
        initial_state=state.initial_state,
        fail_count = 1,
        fail_time = int(dt.now().timestamp()),
        fail_reason = "Unable to download from {}".format(state.url)
    )

def dateToUNIX(date: str, time: str) -> int:
    newDate = date + time
    unixTime = dt.strptime(newDate, "%Y%m%d%H%M%S").timestamp() * 1000
    return int(unixTime)

def runit(fileName, apikey, node, unixTime):
    unixEndTime = unixTime + 600000 #600000ms = 10min
    initState = InitialState(fileName, apikey, node, unixTime, unixEndTime)
    pendState = initiate_download(initState)
    print(pendState)
    if isinstance(pendState, DownloadPendingState):
        ready = check_download(pendState)
        while not isinstance(ready, DownloadReadyState):
            sleep(11)
            ready = check_download(pendState)
    downloaded = get_data(ready)
    return str(downloaded.export_id) + '.zip'