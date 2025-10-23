import logging
from queue import Queue
from threading import Thread
from typing import Optional, Any
from dataclasses import dataclass, asdict
from .dictionary.base import CredentialPlatformEnum
from enum import Enum

@dataclass
class Credential:
    platform: CredentialPlatformEnum
    username: str
    password: str
    cookie: str


@dataclass
class ConfigType:
    deck: str
    selectedDict: int
    selectedApi: int
    selectedGroup: Optional[list[list[str]]]
    credential: list[Credential]
    briefDefinition: bool
    syncTemplates: bool
    termSpeaking: bool
    contextSpeaking: bool
    enableContext: bool
    disableSpeaking: bool
    GreatBritainSpeaking: bool
    USSpeaking: bool
    aporaApiToken: str

def asdict_with_enum(obj) -> Any:
    def _convert(value):
        if isinstance(value, Enum):
            return value.value  # 或 value.name
        elif isinstance(value, list):
            return [_convert(v) for v in value]
        elif isinstance(value, dict):
            return {k: _convert(v) for k, v in value.items()}
        else:
            return value

    return _convert(asdict(obj))

def safe_convert_config_to_dict(config: ConfigType) -> dict[str, Any]:
    return asdict_with_enum(config)


def safe_load_empty_config() -> ConfigType:
    config = ConfigType(
        deck="",
        selectedDict=0,
        selectedApi=0,
        selectedGroup=None,  # 可为 None
        credential=[],
        briefDefinition=False,
        syncTemplates=False,
        termSpeaking=False,
        contextSpeaking=False,
        enableContext=False,
        disableSpeaking=True,
        GreatBritainSpeaking=False,
        USSpeaking=True,
        aporaApiToken="",
    )
    return config


def safe_load_config(data: dict) -> ConfigType:
    creds = [Credential(**cred) for cred in data["credential"]]
    config = ConfigType(
        deck=data["deck"],
        selectedDict=data["selectedDict"],
        selectedApi=data["selectedApi"],
        selectedGroup=data["selectedGroup"],  # 可为 None
        credential=creds,
        briefDefinition=data["briefDefinition"],
        syncTemplates=data["syncTemplates"],
        termSpeaking=data["termSpeaking"],
        contextSpeaking=data["contextSpeaking"],
        enableContext=data["enableContext"],
        disableSpeaking=data["disableSpeaking"],
        GreatBritainSpeaking=data["GreatBritainSpeaking"],
        USSpeaking=data["USSpeaking"],
        aporaApiToken=data["aporaApiToken"],
    )
    return config


logger = logging.getLogger("dict2Anki.misc")


class Mask:
    def __init__(self, info):
        self.info = info

    def __repr__(self):
        return "*******"

    def __str__(self):
        return self.info


class Worker(Thread):
    def __init__(self, queue, result_queue):
        super(Worker, self).__init__()
        self._q = queue
        self.result_queue = result_queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            try:
                f, args, kwargs = self._q.get()
                if f:
                    result = f(*args, **kwargs)
                    if result:
                        self.result_queue.put(result)
            except Exception as e:
                logger.exception(e)
            finally:
                self._q.task_done()


class ThreadPool:
    def __init__(self, max_workers):
        self._q = Queue(max_workers)
        self.results_q = Queue()
        self.result = []
        # Create Worker Thread
        for _ in range(max_workers):
            Worker(self._q, self.results_q)

    def submit(self, f, *args, **kwargs):
        self._q.put((f, args, kwargs))

    def wait_complete(self):
        self._q.join()
        while not self.results_q.empty():
            self.result.append(self.results_q.get())
        return self.result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wait_complete()
