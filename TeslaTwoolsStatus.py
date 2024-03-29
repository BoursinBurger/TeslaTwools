from enum import Enum, auto

VERSION = "1.3.2"


class States(Enum):
    INITIALIZED = auto()
    NO_SAVE_FILE = auto()
    SAVE_FILE_FOUND = auto()
    SAVE_SLOT_ADDED = auto()
    SAVE_SLOT_DELETED = auto()
    SAVE_SLOT_UPDATED = auto()
    SAVE_FILE_EDITED = auto()
    UNCHANGED = auto()


class SplitEdit(Enum):
    ADD = auto()
    EDIT = auto()
