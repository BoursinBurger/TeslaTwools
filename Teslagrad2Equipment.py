from enum import Flag, auto


# Equipment flags for defining requirements for exiting to a connecting scene or collecting a scroll
class Equipment(Flag):
    BLINK = auto()
    CLOAK = auto()
    WATER_BLINK = auto()
    SLIDE = auto()
    MJOLNIR = auto()
    AXE = auto()
    RED_CLOAK = auto()
    BLINK_WIRE_AXE = auto()
    DOUBLE_JUMP = auto()
    DIRECTIONAL_BLINK = auto()
