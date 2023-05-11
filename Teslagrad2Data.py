import os
import re
import ruamel.yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Union, Any


# Class object representing a save slot within the save file
class SaveSlot:
    version: float = 1.6
    name: str = "Slot"
    dateModified: datetime = None
    timeSpent: str = "00:00:00.00"
    respawnScene: str = "Lumina Landed"
    respawnFacingRight: bool = True
    respawnPoint: Dict[str, float] = {"x": -117.732597, "y": -173.997604}
    blinkUnlocked: bool = False
    cloakUnlocked: bool = False
    waterblinkUnlocked: bool = False
    mjolnirUnlocked: bool = False
    powerSlideUnlocked: bool = False
    axeUnlocked: bool = False
    blinkWireAxeUnlocked: bool = False
    redCloakUnlocked: bool = False
    omniBlinkUnlocked: bool = False
    doubleJumpUnlocked: bool = False
    secretsMapUnlocked: bool = False
    mapUnlocked: bool = False
    hasMetGalvan: bool = False
    hulderBossfightBeaten: bool = False
    mooseBossFightBeaten: bool = False
    fafnirBossFightBeaten: bool = False
    halvtannBossFightBeaten: bool = False
    galvanBossFightBeaten: bool = False
    trollMiniBossFightBeaten: bool = False
    invasionSequenceDone: bool = False
    vikingBlimpOnTheHunt: bool = True
    vikingBlimpPosition: float = 0.0
    HulderUnderworldChaseProgression: int = 0
    hulder_PreBossDiscoverTraversed: bool = False
    hulder_PreBossLevelChaseDone: bool = False
    hulder_DarkRoomLevelChaseDone: bool = False
    hulder_GrueEyesLevelChaseDone: bool = False
    triggersSet: List[str] = list()
    mapShapesUnlocked: List[Union[str, int]] = list()
    activitiesUnlocked: List[Any] = list()
    scrollsPickedUp: List[int] = list()
    scrollsSeenInCollection: List[Any] = list()
    savedCharges: List[Dict[str, str]] = list()
    savedResetInfos: List[Any] = list()
    gameWasCompletedOnce: bool = False

    # If initiated with a dictionary, set the object's properties to those of the dictionary, otherwise use the defaults
    def __init__(self, save_slot_dict: Dict[str, Any] = None):
        if save_slot_dict:
            for k, v in save_slot_dict.items():
                setattr(self, k, v)
        else:
            self.dateModified = datetime.now(timezone.utc).astimezone()

    # Helper functions for querying the equipment booleans
    def equipment(self):
        return (self.blinkUnlocked, self.cloakUnlocked, self.waterblinkUnlocked, self.powerSlideUnlocked,
                self.mjolnirUnlocked, self.axeUnlocked, self.mapUnlocked, self.redCloakUnlocked,
                self.blinkWireAxeUnlocked, self.doubleJumpUnlocked, self.omniBlinkUnlocked, self.secretsMapUnlocked)

    def equipment_count(self):
        return self.equipment().count(True)

    # Helper functions for querying the boss booleans
    def bosses(self):
        return (self.hulderBossfightBeaten, self.mooseBossFightBeaten, self.fafnirBossFightBeaten,
                self.halvtannBossFightBeaten, self.galvanBossFightBeaten, self.trollMiniBossFightBeaten)

    def boss_count(self):
        return self.bosses().count(True)

    # Exports the class object to a dictionary as preparation for serializing the save file to YAML
    def export(self):
        return {
            "version": self.version,
            "name": self.name,
            # ruamel.yaml imports dateModified as an instance of its TimeStamp object.
            # It adds the timezone offset to the timestamp and then drops the tzinfo.
            # To restore the tzinfo to the timestamp, we create a new datetime from the TimeStamp object and
            # set it to the UTC timezone, then convert to the local timezone, and finally export to ISO format.
            # And that's not all! More transformation happens in SaveFile.write().
            "dateModified": datetime(self.dateModified.year, self.dateModified.month, self.dateModified.day,
                                     self.dateModified.hour, self.dateModified.minute, self.dateModified.second,
                                     self.dateModified.microsecond, timezone.utc).astimezone().isoformat(),
            "timeSpent": self.timeSpent,
            "respawnScene": self.respawnScene,
            "respawnFacingRight": self.respawnFacingRight,
            "respawnPoint": {"x": self.respawnPoint.get("x"), "y": self.respawnPoint.get("y")},
            "blinkUnlocked": self.blinkUnlocked,
            "cloakUnlocked": self.cloakUnlocked,
            "waterblinkUnlocked": self.waterblinkUnlocked,
            "mjolnirUnlocked": self.mjolnirUnlocked,
            "powerSlideUnlocked": self.powerSlideUnlocked,
            "axeUnlocked": self.axeUnlocked,
            "blinkWireAxeUnlocked": self.blinkWireAxeUnlocked,
            "redCloakUnlocked": self.redCloakUnlocked,
            "omniBlinkUnlocked": self.omniBlinkUnlocked,
            "doubleJumpUnlocked": self.doubleJumpUnlocked,
            "secretsMapUnlocked": self.secretsMapUnlocked,
            "mapUnlocked": self.mapUnlocked,
            "hasMetGalvan": self.hasMetGalvan,
            "hulderBossfightBeaten": self.hulderBossfightBeaten,
            "mooseBossFightBeaten": self.mooseBossFightBeaten,
            "fafnirBossFightBeaten": self.fafnirBossFightBeaten,
            "halvtannBossFightBeaten": self.halvtannBossFightBeaten,
            "galvanBossFightBeaten": self.galvanBossFightBeaten,
            "trollMiniBossFightBeaten": self.trollMiniBossFightBeaten,
            "invasionSequenceDone": self.invasionSequenceDone,
            "vikingBlimpOnTheHunt": self.vikingBlimpOnTheHunt,
            "vikingBlimpPosition": self.vikingBlimpPosition,
            "HulderUnderworldChaseProgression": self.HulderUnderworldChaseProgression,
            "hulder_PreBossDiscoverTraversed": self.hulder_PreBossDiscoverTraversed,
            "hulder_PreBossLevelChaseDone": self.hulder_PreBossLevelChaseDone,
            "hulder_DarkRoomLevelChaseDone": self.hulder_DarkRoomLevelChaseDone,
            "hulder_GrueEyesLevelChaseDone": self.hulder_GrueEyesLevelChaseDone,
            "triggersSet": self.triggersSet,
            "mapShapesUnlocked": self.mapShapesUnlocked,
            "activitiesUnlocked": self.activitiesUnlocked,
            "scrollsPickedUp": self.scrollsPickedUp,
            "scrollsSeenInCollection": self.scrollsSeenInCollection,
            "savedCharges": self.savedCharges,
            "savedResetInfos": self.savedResetInfos,
            "gameWasCompletedOnce": self.gameWasCompletedOnce
        }


# Class object representing the save file: a list of SaveSlot objects with saveDataSlots as a dictionary header
class SaveFile:
    saveDataSlots: List[SaveSlot] = list()
    save_file_path = (Path(os.getenv('APPDATA')) / '../LocalLow/Rain/Teslagrad 2/Saves.yaml').resolve()

    # Initialize the class object with a list of SaveSlot objects, or leave the list of SaveSlots empty
    def __init__(self, save_slot_list: List[SaveSlot] = None):
        if save_slot_list:
            self.saveDataSlots = save_slot_list

    # Read the YAML save file
    def read(self):
        yaml = ruamel.yaml.YAML()
        with self.save_file_path.open('rt', encoding='utf-8') as save:
            save_file_dict = yaml.load(save)
        save_list = save_file_dict.get("saveDataSlots")
        self.saveDataSlots = list()
        for save_dict in save_list:
            self.saveDataSlots.append(SaveSlot(save_dict))

    # Correct the integrity of the save file when equipment and boss flags do not match the associated pin triggers
    # And when collected scrolls do not match their respective map shapes
    def checksum(self):
        for slot in self.saveDataSlots:

            for flag, trigger in ((slot.waterblinkUnlocked, "pinCollected_WaterBlinkPickup"),
                                  (slot.powerSlideUnlocked, "pinCollected_SlidePickup"),
                                  (slot.mjolnirUnlocked, "pinCollected_MjolnirPickup"),
                                  (slot.blinkWireAxeUnlocked, "pinCollected_BlinkAxe"),
                                  (slot.doubleJumpUnlocked, "pinCollected_DoubleJump"),
                                  (slot.redCloakUnlocked, "pinCollected_RedCloak"),
                                  (slot.omniBlinkUnlocked, "pinCollected_OmniBlink"),
                                  (slot.secretsMapUnlocked, "pinCollected_MapSecretsPickup"),
                                  (slot.hulderBossfightBeaten, "pinCollected_HuldrFight"),
                                  (slot.mooseBossFightBeaten, "pinCollected_MooseFight"),
                                  (slot.fafnirBossFightBeaten, "pinCollected_FafnirFight"),
                                  (slot.halvtannBossFightBeaten, "pinCollected_HalvtannFight"),
                                  (slot.galvanBossFightBeaten, "pinCollected_GalvanFight")):

                # Set the triggersSet collected pins of collected equipment and defeated bosses.
                if flag is True and trigger not in slot.triggersSet:
                    slot.triggersSet.append(trigger)
                # Remove the triggersSet collected pins of uncollected equipment and undefeated bosses.
                if flag is False and trigger in slot.triggersSet:
                    slot.triggersSet = [item for item in slot.triggersSet if trigger != item]

            for scroll in scrolls:
                # Set the mapShapesUnlocked of collected scrolls.
                if scroll in slot.scrollsPickedUp and scroll not in slot.mapShapesUnlocked:
                    slot.mapShapesUnlocked.append(scroll)
                # Remove the mapShapesUnlocked of uncollected scrolls.
                if scroll not in slot.scrollsPickedUp and scroll in slot.mapShapesUnlocked:
                    slot.mapShapesUnlocked = [item for item in slot.mapShapesUnlocked if scroll != item]

    # Overwrite the save file with the contents of the updated class objects
    def write(self):
        # Correct any inconsistent save data
        self.checksum()

        # dateModified has two anomalies when exporting it to YAML.
        #
        # First, the YAML standard apparently wants to surround an ISO timestamp with single quotes. Rain's YAML
        # doesn't do that, and even though that would paint Rain as being in the wrong, I still need to imitate their
        # formatting, and it's impossible to tell these YAML parsers "No, I really do want to write it incorrectly."
        #
        # Second, Teslagrad 2 writes the microseconds with 7 digits of precision. A Python datetime object will only
        # hold 6. Unfortunately, Teslagrad 2 will not recognize the save slot when dateModified only has 6.
        #
        # To solve both of these issues, ruamel.yaml allows us to define a function to transform the YAML after
        # serializing it. So here we place a regular expression to strip the single quotes and to add a zero to the
        # end of the 6-digit microseconds to bring it to 7 digits. Please forgive me for not being able to preserve
        # the ten-millionths of a second precision. You'll just have to deal with millionths of a second.
        def fix_datemodified(yaml_string):
            return re.sub(r"dateModified: '(.*\.)(\d+)(.*)'", r"dateModified: \g<1>\g<2>0\g<3>", yaml_string)

        # Convert the class objects to a dictionary
        out_dict = {"saveDataSlots": [slot.export() for slot in self.saveDataSlots]}

        # Convert the dictionary to YAML and write to the file, applying the transform function
        yaml = ruamel.yaml.YAML()
        with self.save_file_path.open('w', encoding='utf-8') as save:
            yaml.dump(out_dict, save, transform=fix_datemodified)


# Set of values for mapShapesUnlocked
map_shapes = (
    "'Uncover_Grue Lake '",
    "HideSecret_Challenge2",
    "HideSecret_Challenge3",
    "HideSecret_Clallenge4",
    "HideSecret_East balchony",
    "HideSecret_JumpupConnector",
    "HideSecret_Pat Electric Stairs",
    "HideSecret_UndergroundBase5",
    "HideSecret_jumpup",
    "Uncover_Acid Reflux",
    "Uncover_Angry Vikings 1",
    "Uncover_Angry Vikings 2",
    "Uncover_Angry Vikings 3",
    "Uncover_Angry Vikings",
    "Uncover_Aqueduct",
    "Uncover_Axe Challenge Area 2",
    "Uncover_Axe Challenge Area",
    "Uncover_Blinkwire To Mountaintop",
    "Uncover_Bridge East",
    "Uncover_Bridge West",
    "Uncover_Broken Lamp Climb",
    "Uncover_Burial Chamber",
    "Uncover_Burial Tunnel",
    "Uncover_Cabin in the Woods",
    "Uncover_Cave",
    "Uncover_Challenge1",
    "Uncover_Challenge2",
    "Uncover_Challenge3",
    "Uncover_Clallenge4",
    "Uncover_CloakPickup",
    "Uncover_Connection to bridge",
    "Uncover_Crash before Halvtann",
    "Uncover_DampDark",
    "Uncover_DarkPond",
    "Uncover_Deeper Cave",
    "Uncover_DragonLurking",
    "Uncover_Dyspepsia Max",
    "Uncover_Dyspepsia",
    "Uncover_East Side 2",
    "Uncover_East balchony",
    "Uncover_Eating Hall",
    "Uncover_Electro Moose",
    "Uncover_Explosives Intro",
    "Uncover_Fafnir",
    "Uncover_FishboneField",
    "Uncover_Floating Water",
    "Uncover_Floor Smash",
    "Uncover_Galvan Living space",
    "Uncover_Galvan Room 1",
    "Uncover_Galvan Tower Calm Then Storm",
    "Uncover_Galvan Tower Rotating Killfield",
    "Uncover_Galvan Tower Top Axe Entrance",
    "Uncover_Galvan Tower Top Corridor",
    "Uncover_Galvan Tower Top Up and Around",
    "Uncover_GalvanBossfight",
    "Uncover_Give me a name!",
    "Uncover_Glacier Dock",
    "Uncover_GlacierBottom",
    "Uncover_GlacierMiddle",
    "Uncover_Glue Lake Bifurcation",
    "Uncover_Grave of the viking king",
    "Uncover_Grue Eyes",
    "Uncover_Grue Lake Dextral",
    "Uncover_Grue Lake Lower Lane",
    "Uncover_GrueCliff",
    "Uncover_Halvtann",
    "Uncover_Heist Top",
    "Uncover_Heist",
    "Uncover_Helping Hair",
    "Uncover_Hidden Fjord",
    "Uncover_Hub Level East",
    "Uncover_Hub Level West",
    "Uncover_Hub Level",
    "Uncover_Hulder Dies",
    "Uncover_HulderPassage",
    "Uncover_Huldr Boss",
    "Uncover_Huldr Pre Bossfight",
    "Uncover_Ice Climbers",
    "Uncover_Inside Ship",
    "Uncover_Invasion!",
    "Uncover_JumpupConnector",
    "Uncover_LightningStorm",
    "Uncover_Longjump 2",
    "Uncover_Longjump",
    "Uncover_Lower Sky",
    "Uncover_LowerSide",
    "Uncover_Lumina Landed",
    "Uncover_Mjolnir",
    "Uncover_Node 7",
    "Uncover_Now you are thinking with Magnets 1",
    "Uncover_Now you are thinking with Magnets 2",
    "Uncover_Nøkken Intro",
    "Uncover_Out of order",
    "Uncover_Pat Electric Stairs",
    "Uncover_Pat Mine 4",
    "Uncover_Path Of Galvan",
    "Uncover_Petter Test Level",
    "Uncover_Platform Hulder Escape",
    "Uncover_Platform",
    "Uncover_PowerSource",
    "Uncover_Scroll Room Below Death Machine",
    "Uncover_SecretMoose",
    "Uncover_Secret_2",
    "Uncover_Secret_3",
    "Uncover_Shaft to Invasion!",
    "Uncover_Sideroom",
    "Uncover_Sky Bridge",
    "Uncover_Sky Hub 2",
    "Uncover_Sky Hub 3",
    "Uncover_Sky Hub 4",
    "Uncover_Sky Hub 5",
    "Uncover_Sky Hub 6",
    "Uncover_Sky Hub 7",
    "Uncover_Slide Attack",
    "Uncover_Slide Tutorial",
    "Uncover_SmashingThrough",
    "Uncover_Smelt",
    "Uncover_SmeltPool",
    "Uncover_SmeltRafters",
    "Uncover_Snowball",
    "Uncover_Solid State Matter",
    "Uncover_Spiky Descent",
    "Uncover_SpikyChallenge",
    "Uncover_Standing Rock",
    "Uncover_Stave Church Secret",
    "Uncover_Swamp Elevator",
    "Uncover_Swamp Slide",
    "Uncover_Teleporter",
    "Uncover_Temple Pathway",
    "Uncover_Tended Gaves",
    "Uncover_Tesla Tower Entrance",
    "Uncover_Tesla Tower Outside East 2",
    "Uncover_Tesla Tower Outside East 3",
    "Uncover_Tesla Tower Outside East",
    "Uncover_TeslaThrone",
    "Uncover_The underworld",
    "Uncover_Throneroom",
    "Uncover_Time Trial Viking Altar",
    "Uncover_Tower Shaft",
    "Uncover_Triclecave",
    "Uncover_Underground Temple",
    "Uncover_UndergroundBase",
    "Uncover_UndergroundBase3",
    "Uncover_UndergroundBase4",
    "Uncover_UndergroundBase5",
    "Uncover_UndergroundBase6",
    "Uncover_Underwater Hub Secret",
    "Uncover_UpperVikingTower",
    "Uncover_VerticalBlinkChallenge",
    "Uncover_Viking Hilltop",
    "Uncover_Viking Platform Chase",
    "Uncover_Viking Platform Roof",
    "Uncover_Viking Platform West",
    "Uncover_Viking Tower Activate Field",
    "Uncover_Viking Tower Balcony",
    "Uncover_Viking Tower Hall",
    "Uncover_Viking Tower Hallway",
    "Uncover_Viking Tower Magnet Climb",
    "Uncover_Viking Tower Top Inside",
    "Uncover_Viking Tower Top Outside",
    "Uncover_Viking Tower Tussel Room",
    "Uncover_Viking Tower Wine Cellar",
    "Uncover_Viking Tower Wraith Miniboss",
    "Uncover_Viking_hall",
    "Uncover_Vikings VS Wraiths",
    "Uncover_Village",
    "Uncover_Water Blink",
    "Uncover_Water Mountain Entrance",
    "Uncover_Waterfall Climb",
    "Uncover_Waterfall Passage",
    "Uncover_Waterfalls",
    "Uncover_Winter Garden",
    "Uncover_hiddenhuldrheim",
    "Uncover_jumpup",
    "Uncover_jumpup2",
    "Uncover_mountaintop",
    "Uncover_rClimbArea",
    "Uncover_rClimbArea2",
    "Uncover_rMountainStart",
    "Uncover_rehammer",
    "Uncover_yet another slide level"
)

# Set of values for scrollsPickedUp
scrolls = (
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
    59,
    60,
    61,
    62,
    63,
    64,
    65,
    66,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    76,
    77,
    78,
    79,
    80,
    81
)

# Set of values for placing the checkboxes on the scroll chooser image canvas
scroll_image_coordinates = ((3663, 2356),  # Scroll 1
                            (4599, 2038),  # Scroll 2
                            (2962, 2706),  # Scroll 3
                            (1663, 2690),  # Scroll 4
                            (4588, 1188),  # Scroll 5
                            (2163, 1387),  # Scroll 6
                            (2107, 2199),  # Scroll 7
                            (1885, 2276),  # Scroll 8
                            (2175, 2673),  # Scroll 9
                            (2886, 2687),  # Scroll 10
                            (2526, 2431),  # Scroll 11
                            (2346, 2395),  # Scroll 12
                            (2823, 2325),  # Scroll 13
                            (835, 2706),   # Scroll 14
                            (1007, 2741),  # Scroll 15
                            (1765, 2591),  # Scroll 16
                            (1761, 2627),  # Scroll 17
                            (2548, 2274),  # Scroll 18
                            (2202, 2490),  # Scroll 19
                            (4615, 2283),  # Scroll 20
                            (1896, 2386),  # Scroll 21
                            (1975, 2636),  # Scroll 22
                            (3603, 1981),  # Scroll 23
                            (2222, 2336),  # Scroll 24
                            (2673, 2577),  # Scroll 25
                            (2502, 2548),  # Scroll 26
                            (2266, 2175),  # Scroll 27
                            (4490, 1343),  # Scroll 28
                            (4488, 1287),  # Scroll 29
                            (2530, 2803),  # Scroll 30
                            (2095, 1986),  # Scroll 31
                            (3374, 2647),  # Scroll 32
                            (2458, 1618),  # Scroll 33
                            (2713, 2736),  # Scroll 34
                            (4688, 2221),  # Scroll 35
                            (2287, 2487),  # Scroll 36
                            (3511, 2450),  # Scroll 37
                            (3395, 2516),  # Scroll 38
                            (2435, 2122),  # Scroll 39
                            (4345, 2003),  # Scroll 40
                            (4418, 1960),  # Scroll 41
                            (4447, 1877),  # Scroll 42
                            (4515, 2127),  # Scroll 43
                            (2151, 1924),  # Scroll 44
                            (4360, 2330),  # Scroll 45
                            (4352, 2073),  # Scroll 46
                            (2493, 2264),  # Scroll 47
                            (3146, 2659),  # Scroll 48
                            (2243, 2406),  # Scroll 49
                            (4389, 1802),  # Scroll 50
                            (4575, 2001),  # Scroll 51
                            (3562, 2555),  # Scroll 52
                            (3591, 2663),  # Scroll 53
                            (4514, 974),   # Scroll 54
                            (3023, 2735),  # Scroll 55
                            (4494, 1157),  # Scroll 56
                            (652, 2757),   # Scroll 57
                            (1289, 2752),  # Scroll 58
                            (2076, 2774),  # Scroll 59
                            (4444, 1333),  # Scroll 60
                            (3244, 1531),  # Scroll 61
                            (275, 2820),   # Scroll 62
                            (256, 2690),   # Scroll 63
                            (3089, 2665),  # Scroll 64
                            (3638, 2495),  # Scroll 65
                            (2017, 2551),  # Scroll 66
                            (2184, 1314),  # Scroll 67
                            (3792, 2585),  # Scroll 68
                            (4419, 752),   # Scroll 69
                            (3721, 2636),  # Scroll 70
                            (4870, 1892),  # Scroll 71
                            (3513, 2473),  # Scroll 72
                            (4585, 371),   # Scroll 73
                            (4349, 734),   # Scroll 74
                            (2054, 2710),  # Scroll 75
                            (3494, 3092),  # Scroll 76
                            (4868, 1821),  # Scroll 77
                            (2050, 2048),  # Scroll 78
                            (3540, 2612),  # Scroll 79
                            (4461, 2091),  # Scroll 80
                            (4576, 502))   # Scroll 81

# Set of values for triggersSet
triggers = (
    "AboveWinterGardenDoor",
    "AcidPoolButton1",
    "AcidPoolButton2",
    "AcidRefluxShortcut",
    "AirshipBackgroundTravel",
    "AxeDoor-East Side 2--932330024",
    "AxeDoor-Galvan Living space--1728489528",
    "AxeDoor-Galvan Living space--453346445",
    "AxeDoor-Galvan Living space--510822653",
    "AxeDoor-Galvan Living space--854468086",
    "AxeDoor-Galvan Sidescene-1166530932",
    "AxeDoor-Galvan Tower Calm Then Storm--1445354106",
    "AxeDoor-Galvan Tower Top Axe Entrance-1574004555",
    "AxeDoor-Ice Climbers-588613135",
    "AxeDoor-Invasion!--2116292917",
    "AxeDoor-Invasion!-24066703",
    "AxeDoor-Longjump-353703032",
    "AxeDoor-Mountaintop--1320435704",
    "AxeDoor-Now you are thinking with Magnets 2--224434375",
    "AxeDoor-Out of order--350940418",
    "AxeDoor-Tesla Tower Outside East 2--2044958547",
    "AxeDoor-Time Trial Viking Altar--2036902879",
    "AxeDoor-Tower Shaft-1624356224",
    "AxeDoor-VerticalBlinkChallenge--836660001",
    "Blink Prompt",
    "Breakable-Axe Challenge Area 2-1358854130",
    "Breakable-Axe Challenge Area 2-1683697837",
    "Breakable-Cave-601231003",
    "Breakable-Cave-950946374",
    "Breakable-Connection to bridge--361683439",
    "Breakable-DragonLurking--928260931",
    "Breakable-Dyspepsia Max-185600016",
    "Breakable-Dyspepsia--1000462004",
    "Breakable-Dyspepsia--1816849690",
    "Breakable-Dyspepsia-1744923997",
    "Breakable-Dyspepsia-1987343683",
    "Breakable-Electro Moose-565097134",
    "Breakable-Fafnir-305113621",
    "Breakable-Floor Smash--1371715032",
    "Breakable-Floor Smash--1763324606",
    "Breakable-Floor Smash--215522036",
    "Breakable-Floor Smash--428194330",
    "Breakable-Floor Smash--582578115",
    "Breakable-Floor Smash--631469263",
    "Breakable-Floor Smash-1013595669",
    "Breakable-Floor Smash-1059140397",
    "Breakable-Floor Smash-1145283531",
    "Breakable-Floor Smash-1672981893",
    "Breakable-Floor Smash-1674053949",
    "Breakable-Floor Smash-1709204993",
    "Breakable-Floor Smash-405489689",
    "Breakable-Galvan Tower Top Axe Entrance--1628566351",
    "Breakable-Galvan Tower Top Axe Entrance--1725466635",
    "Breakable-Galvan Tower Top Axe Entrance--504482123",
    "Breakable-Galvan Tower Top Axe Entrance--69683227",
    "Breakable-Galvan Tower Top Axe Entrance--727307129",
    "Breakable-Galvan Tower Top Axe Entrance--991042760",
    "Breakable-Galvan Tower Top Axe Entrance-1073369045",
    "Breakable-Galvan Tower Top Axe Entrance-1616973351",
    "Breakable-Galvan Tower Top Axe Entrance-2050233311",
    "Breakable-Galvan Tower Top Axe Entrance-680303141",
    "Breakable-Grue Eyes-299577765",
    "Breakable-GrueCliff--2049502695",
    "Breakable-Halvtann--3058969",
    "Breakable-Hub Level--1175335994",
    "Breakable-Hulder Dies--1138969236",
    "Breakable-Hulder Dies-489840395",
    "Breakable-Ice Climbers-636278171",
    "Breakable-Lower Sky-1644567515",
    "Breakable-LowerSide--131661065",
    "Breakable-LowerSide--846129328",
    "Breakable-LowerSide-278126765",
    "Breakable-LowerSide-602381887",
    "Breakable-Mjolnir--1284330112",
    "Breakable-Momentum Blink--2055046817",
    "Breakable-Mountaintop--589450317",
    "Breakable-Mountaintop-785694023",
    "Breakable-Now you are thinking with Magnets 2-1996518817",
    "Breakable-PathOfGalvan--144165163",
    "Breakable-PathOfGalvan-762012366",
    "Breakable-PowerSource--1219958260",
    "Breakable-PowerSource--1314279557",
    "Breakable-PowerSource--207521396",
    "Breakable-PowerSource--2083920514",
    "Breakable-PowerSource--591827751",
    "Breakable-PowerSource-9984600",
    "Breakable-Resist Temptation--2070493769",
    "Breakable-Resist Temptation--478607386",
    "Breakable-Resist Temptation--687876984",
    "Breakable-Resist Temptation-1693847260",
    "Breakable-Resist Temptation-733973187",
    "Breakable-Resist Temptation-860382180",
    "Breakable-Sideroom--940326738",
    "Breakable-Sky Hub 4--431618175",
    "Breakable-Sky Hub 4-607284005",
    "Breakable-Slide Tutorial--1041737674",
    "Breakable-Slide Tutorial--337807438",
    "Breakable-Slide Tutorial--612996882",
    "Breakable-Slide Tutorial-1298919149",
    "Breakable-Slide Tutorial-1312896763",
    "Breakable-Slide Tutorial-1819634119",
    "Breakable-Slide Tutorial-1917758514",
    "Breakable-Slide Tutorial-1939550337",
    "Breakable-Slide Tutorial-691102950",
    "Breakable-SmashingThrough--1093948779",
    "Breakable-SmashingThrough--1335639497",
    "Breakable-SmashingThrough--1388976180",
    "Breakable-SmashingThrough--1547157770",
    "Breakable-SmashingThrough--1869110015",
    "Breakable-SmashingThrough--2110241752",
    "Breakable-SmashingThrough--452293121",
    "Breakable-SmashingThrough--719765400",
    "Breakable-SmashingThrough--826380597",
    "Breakable-SmashingThrough--894359327",
    "Breakable-SmashingThrough--98818787",
    "Breakable-SmashingThrough-127372071",
    "Breakable-SmashingThrough-140960743",
    "Breakable-SmashingThrough-1751950232",
    "Breakable-SmashingThrough-364926951",
    "Breakable-SmashingThrough-473225375",
    "Breakable-SmashingThrough-775239883",
    "Breakable-SmashingThrough-793838895",
    "Breakable-Snowball-1194670852",
    "Breakable-Standing Rock--356686498",
    "Breakable-Standing Rock-1904179073",
    "Breakable-Tended Gaves--1739846700",
    "Breakable-Tended Gaves-31382350",
    "Breakable-Tower Shaft--1510570778",
    "Breakable-Tower Shaft--2008219447",
    "Breakable-Tower Shaft--2046602290",
    "Breakable-Tower Shaft--284682321",
    "Breakable-Tower Shaft-1167170134",
    "Breakable-Tower Shaft-1178692124",
    "Breakable-Tower Shaft-420312762",
    "Breakable-UndergroundBase6--1548952452",
    "Breakable-UndergroundBase6-91880611",
    "Breakable-UpperVikingTower--645493296",
    "Breakable-UpperVikingTower-1742153449",
    "Breakable-UpperVikingTower-1774416350",
    "Breakable-UpperVikingTower-221121281",
    "Breakable-Viking Platform West--1704096194",
    "Breakable-Viking Platform West--510120398",
    "Breakable-Viking Platform West-1933950303",
    "Breakable-Viking Tower Balcony--2060823437",
    "Breakable-Viking Tower Balcony--487783888",
    "Breakable-Viking Tower Balcony--574820428",
    "Breakable-Viking Tower Balcony-1567743415",
    "Breakable-Viking Tower Hall--1706372919",
    "Breakable-Viking Tower Hall--1783956776",
    "Breakable-Viking Tower Hall--1919839329",
    "Breakable-Viking Tower Hall-1061674777",
    "Breakable-Viking Tower Hall-275662884",
    "Breakable-Viking Tower Hall-385294013",
    "Breakable-Viking Tower Hallway--861667534",
    "Breakable-Viking Tower Hallway-1281093954",
    "Breakable-Viking Tower Hallway-709075319",
    "Breakable-Viking Tower Hallway-717395952",
    "Breakable-Viking Tower Magnet Climb--1445128805",
    "Breakable-Viking Tower Magnet Climb--2012704319",
    "Breakable-Viking Tower Magnet Climb--5928220",
    "Breakable-Viking Tower Wraith Miniboss--317195345",
    "Breakable-Vikings VS Wraiths-168850492",
    "Breakable-Vikings VS Wraiths-1780890928",
    "Breakable-Waterfall Climb--1535428871",
    "Breakable-Waterfalls-522669383",
    "Breakable-level_jumpupConnector-1305344334",
    "Breakable-level_jumpupConnector-1880179175",
    "Breakable-rehammer--136429578",
    "Breakable-rehammer-1901882263",
    "Breakable-rehammer-1911433650",
    "Breakable-rehammer-549329812",
    "Breakable-viking_hall--1803493672",
    "Breakable-viking_hall--733228729",
    "Breakable-viking_hall--947263211",
    "Breakable-viking_hall-1672776352",
    "Breakable-viking_hall-1909521936",
    "Breakable-viking_hall-2031706238",
    "Breakable-yet another slide level-2130103373",
    "Broke Wire Going To Glacier",
    "BurialChamberDoor",
    "DefeatedWraithMiniBoss",
    "DyspepsiaShortcutEast",
    "Entered Ship In Glacier Dock",
    "Escaped Halvtann",
    "GetMapCutsceneSeen",
    "GetSecondMapPart",
    "GetThirdMapPart",
    "GrueLakeDextralDoor",
    "Harpoon AcidRefluxToThoneEntrance",
    "Harpoon Bottom Glacier",
    "Harpoon Galvan Bossfight West",
    "Harpoon Hub East 2",
    "Harpoon Hub East",
    "Harpoon Hub West",
    "Harpoon Innermountain 1",
    "Harpoon Innermountain 2",
    "Harpoon InvasionToVikingGrave",
    "Harpoon PathOfGalvan",
    "Harpoon Top Of Drauggard",
    "Harpoon Tower Shaft West",
    "Harpoon TowerTopEast",
    "Harpoon VikingTowerTopEast",
    "Harpoon Waterfall Passage",
    "HasDoneDoubleJump",
    "HasPickedUpAnything",
    "HasUsedBlinkWireAxe",
    "HasUsedRedCloak",
    "Heist Top",
    "HulderGrueEyesChaseCompleted",
    "HulderIntroCutscene_HulderSpottedPlayer",
    "HulderIntroCutscene_PlayerFellDown",
    "HulderJumpscare1",
    "HulderPreBossChaseCompleted",
    "HulderReleaseEscape",
    "JensFishyBehaviour",
    "JensHungers",
    "LightningStormScrollDoor",
    "LuminaPettedJens",
    "Mjolnir Prompt",
    "Ninja Slide Prompt",
    "OneOffCameraOverrideArea-Lumina Landed-509199267",
    "OneOffCameraOverrideArea-Viking Hilltop--850223742",
    "OneOffCameraOverrideArea-Waterfalls-334246106",
    "OpenedFirstAxeDoor",
    "PickedUpFamilyPhoto",
    "PlayerTriggered-Blinkwire Sky Network-1388883652",
    "PlayerTriggered-Heist--1882704781",
    "PlayerTriggered-Heist--606881926",
    "PlayerTriggered-Heist-1055653598",
    "PlayerTriggered-Heist-183290385",
    "PlayerTriggered-Hub Level West-191737744",
    "PlayerTriggered-Hulder Dies--64122126",
    "PlayerTriggered-Hulder Dies-1693350798",
    "PlayerTriggered-Huldr Pre Bossfight--1604616815",
    "PlayerTriggered-Inside Ship--1858391447",
    "PlayerTriggered-Inside Ship--1928148228",
    "PlayerTriggered-Lumina Landed-394468903",
    "PlayerTriggered-Mountaintop--118134517",
    "PlayerTriggered-Platform Hulder Escape-253465467",
    "PlayerTriggered-Standing Rock-1528163835",
    "PlayerTriggered-Teleporter-1380369210",
    "PlayerTriggered-Viking Platform Chase--547681900",
    "PlayerTriggered-Viking Platform Chase-748221577",
    "PlayerTriggered-Village-1040941067",
    "Power Slide Prompt",
    "RehammerKillfield",
    "RichardsDoom",
    "ShaftToInvasionSpringButton",
    "Sky Bridge Fixed",
    "SkyBridgeVikingShipEncounterFinished",
    "SmashingThroughRocks",
    "SolidStateDoor",
    "SpikyChallengeDoor",
    "StartElectroCannon",
    "Time Trial 1",
    "Time Trial 2",
    "Time Trial 3",
    "Time Trial 4",
    "Waterblink Prompt",
    "WaterfallInHuldrCaveActive",
    "huldrSaved",
    "pinCollected_BlinkAxe",
    "pinCollected_DoubleJump",
    "pinCollected_FafnirFight",
    "pinCollected_GalvanFight",
    "pinCollected_HalvtannFight",
    "pinCollected_HuldrFight",
    "pinCollected_MapSecretsPickup",
    "pinCollected_MjolnirPickup",
    "pinCollected_MooseFight",
    "pinCollected_OmniBlink",
    "pinCollected_RedCloak",
    "pinCollected_SlidePickup",
    "pinCollected_WaterBlinkPickup",
    "pin_BlinkAxe",
    "pin_DoubleJump",
    "pin_FafnirFight",
    "pin_GalvanFight",
    "pin_HuldrFight",
    "pin_MapSecretsPickup",
    "pin_MjolnirPickup",
    "pin_MooseFight",
    "pin_OmniBlink",
    "pin_RedCloak",
    "pin_SlidePickup",
    "pin_TimeTrialDoor1",
    "pin_TimeTrialDoor2",
    "pin_TimeTrialDoor3",
    "pin_TimeTrialDoor4",
    "pin_WaterBlinkPickup",
    "rClimbAreaDoor"
)

# Set of values for respawnScene and respawnPoint
scenes = {
    "Lumina Landed": {'x': -37.6993103, 'y': -167.896393},
    "Viking Hilltop": {'x': -20.3301716, 'y': -163.364365},
    "Standing Rock": {'x': 141.528397, 'y': -173.351456},
    "Village": {'x': 279.139893, 'y': -173.835785},
    "PathOfGalvan": {'x': 410.998932, 'y': -148.475662},
    "The underworld": {'x': 579.071411, 'y': -131.885681},
    "Waterfalls": {'x': 619.117065, 'y': -169.157593},
    "CloakPickup": {'x': 865.149963, 'y': -155.000015},
    "Now you are thinking with Magnets 1": {'x': 934.991028, 'y': -155.074249},
    "Now you are thinking with Magnets 2": {'x': 971.505737, 'y': -190.054596},
    "UndergroundBase6": {'x': 1036.33728, 'y': -215.729614},
    "Hub Level": {'x': 1115.43701, 'y': -147.899597},
    "Hub Level West": {'x': 1086.67749, 'y': -147.821899},
    "Water Mountain Entrance": {'x': 1006.93964, 'y': -146.913254},
    "Magnet Ore": {'x': 797.650513, 'y': -123.787598},
    "level_jumpup": {'x': 789.541931, 'y': -87.6039581},
    "level_jumpupConnector": {'x': 886.95459, 'y': -60.4136086},
    "Huldr Pre Bossfight": {'x': 844.826721, 'y': -20.6408768},
    "Grue Eyes": {'x': 719.175537, 'y': 13.1454048},
    "Huldr Boss": {'x': 762.368652, 'y': 61.8199997},
    "Waterfall Passage": {'x': 791.248657, 'y': 121.338882},
    "Floating Water": {'x': 864.81958, 'y': 95.2452545},
    "rClimbArea": {'x': 921.023926, 'y': 95.4240417},
    "Lower Sky": {'x': 1119.59998, 'y': 18.8277359},
    "Hub Level East": {'x': 1316.87341, 'y': -153.711426},
    "Viking Tower Hallway": {'x': 1409.6676, 'y': -167.5},
    "Viking Tower Wine Cellar": {'x': 1459.44238, 'y': -149.5},
    "Viking Tower Tussel Room": {'x': 1469.09705, 'y': -125.5},
    "Viking Tower Hall": {'x': 1472.6073, 'y': -116.5},
    "Viking Tower Wraith Miniboss": {'x': 1532.20093, 'y': -38.4999962},
    "Viking Tower Magnet Climb": {'x': 1580.03369, 'y': -77.5},
    "Node 7": {'x': 1528.18958, 'y': -7.00000191},
    "UpperVikingTower": {'x': 1525.10535, 'y': 17.0000019},
    "Viking Tower Balcony": {'x': 1581.90222, 'y': 36.4999962},
    "viking_hall": {'x': 1578.39966, 'y': 54.5},
    "Sky Bridge": {'x': 1583.22717, 'y': 158.000748},
    "Bridge East": {'x': 1862.42432, 'y': -28.7147312},
    "Electro Moose": {'x': 1982.25122, 'y': -29.4834328},
    "Slide Tutorial": {'x': 2064.08081, 'y': -43.5120811},
    "Cabin in the Woods": {'x': 2174.72998, 'y': -11.9075813},
    "Swamp Slide": {'x': 2087.96631, 'y': 25.9671783},
    "Tesla Tower Entrance": {'x': 2128.34131, 'y': 77.5},
    "Smelt": {'x': 2062.54004, 'y': 77.5},
    "SmeltRafters": {'x': 2060.56152, 'y': 127.003464},
    "SmeltPool": {'x': 1976.7251, 'y': 125.499992},
    "SmashingThrough": {'x': 1986.34998, 'y': 138.999969},
    "TeslaThrone": {'x': 1951.00476, 'y': 158.5},
    "Teleporter": {'x': 2045.94653, 'y': 166},
    "Aqueduct": {'x': 2101.36328, 'y': 322},
    "DragonLurking": {'x': 1979.40002, 'y': 365.5},
    "Mjolnir": {'x': 2014.9668, 'y': 367},
    "Floor Smash": {'x': 2046.7063, 'y': 346},
    "yet another slide level": {'x': 2069.8147, 'y': 415},
    "rehammer": {'x': 2036.5979, 'y': 473.5},
    "Tower Shaft": {'x': 1918.67578, 'y': 484.006989},
    "Pat Mine 4": {'x': 1991.22192, 'y': 545.273071},
    "Heist": {'x': 1945.9812, 'y': 626.551392},
    "PowerSource": {'x': 2024.23267, 'y': 645.658569},
    "Heist Top": {'x': 1942.34058, 'y': 699.658386},
    "Shaft to Invasion!": {'x': 2007.31494, 'y': 752.158386},
    "Invasion!": {'x': 2015.26318, 'y': 824.49939},
    "Sky Hub 5": {'x': 1921.79004, 'y': 824.5},
    "Mountaintop": {'x': 872.840027, 'y': 469.616821},
    "Grave of the viking king": {'x': 806.507935, 'y': 533.918091},
    "Galvan Tower Calm Then Storm": {'x': 1927.54895, 'y': 1082.5},
    "Tesla Tower Outside East 3": {'x': 2135.53174, 'y': 884.371216},
    "Tesla Tower Outside East 2": {'x': 2098.42407, 'y': 801.650024},
    "Tesla Tower Outside East": {'x': 2109.09473, 'y': 337},
    "Petter Test Level": {'x': 2106.61157, 'y': 322},
    "Bridge West": {'x': 1615.94995, 'y': -89.5},
    "LowerSide": {'x': 1626.25, 'y': -23.5000019},
    "Time Trial Viking Altar": {'x': 1575.40186, 'y': -102.915207},
    "Connection to bridge": {'x': 1569.79211, 'y': -89.5},
    "Sideroom": {'x': 1499.51941, 'y': -127},
    "Challenge1": {'x': 1551.83984, 'y': -119.499969},
    "Throneroom": {'x': 1486.01172, 'y': -167.5},
    "East Side 2": {'x': 1543.62329, 'y': -131.499969},
    "Solid State Matter": {'x': 1597.38525, 'y': -149.49942},
    "Sky Hub 4": {'x': 1356.90381, 'y': 458.138367},
    "Axe Challenge Area": {'x': 737.586304, 'y': 544.114868},
    "Axe Challenge Area 2": {'x': 751.20813, 'y': 575.240356},
    "Snowball": {'x': 712.124756, 'y': 429.588684},
    "GlacierMiddle": {'x': 717.401245, 'y': 400.125305},
    "GlacierBottom": {'x': 877.003845, 'y': 378.102661},
    "Spiky Descent": {'x': 856.533997, 'y': 261.929047},
    "Hulder Dies": {'x': 829.920288, 'y': 287.538696},
    "Glacier Dock": {'x': 646.323181, 'y': 336.881073},
    "Longjump": {'x': 893.309326, 'y': 219.439728},
    "UndergroundBase3": {'x': 831.487793, 'y': 209.162964},
    "UndergroundBase4": {'x': 784.957703, 'y': 191.443787},
    "UndergroundBase5": {'x': 749.855835, 'y': 191.508362},
    "rClimbArea2": {'x': 784.463379, 'y': 159.380188},
    "Waterfall Climb": {'x': 718.050476, 'y': 166.395554},
    "Momentum Blink": {'x': 609.213623, 'y': 54.2600174},
    "SecretMoose": {'x': 608.554077, 'y': 7.1094923},
    "Ice Climbers": {'x': 583.822632, 'y': 81.1582489},
    "Longjump 2": {'x': 663, 'y': 261.321777},
    "VerticalBlinkChallenge": {'x': 687.820007, 'y': 187.900085},
    "Triclecave": {'x': 645.578735, 'y': -131},
    "hiddenhuldrheim": {'x': 721.234253, 'y': -133.914139},
    "rMountainStart": {'x': 776.633057, 'y': -66.0817413},
    "Tended Gaves": {'x': -139.251724, 'y': -176.903595},
    "Burial Chamber": {'x': -248.215103, 'y': -236.24852},
    "Burial Tunnel": {'x': -242.620743, 'y': -236.279663},
    "Deeper Cave": {'x': -102.20723, 'y': -199.966614},
    "Grue Lake ": {'x': -30.2778721, 'y': -215.133011},
    "Broken Lamp Climb": {'x': 248.880005, 'y': -204.793396},
    "Glue Lake Bifurcation": {'x': 329.424438, 'y': -223.066452},
    "DampDark": {'x': 474.519714, 'y': -178.098129},
    "Grue Lake Lower Lane": {'x': 474.427551, 'y': -222.724396},
    "Grue Lake Dextral": {'x': 704.531982, 'y': -217.218628},
    "Nøkken Intro": {'x': 800.916992, 'y': -124.113762},
    "HulderPassage": {'x': 845.112427, 'y': -40.3005943},
    "Underground Temple": {'x': 1314.16553, 'y': -385.47229},
    "Temple Pathway": {'x': 1309.20874, 'y': -385.432434},
    "Pat Electric Stairs": {'x': 982.660645, 'y': -230.27066},
    "Cave": {'x': 125.882446, 'y': -174.938538},
    "GrueCliff": {'x': 644.40155, 'y': 53.7246361},
    "Sky Hub 7": {'x': 953.26062, 'y': -1.12403178},
    "Viking Tower Activate Field": {'x': 1472.83008, 'y': -142},
    "East balchony": {'x': 1469.12537, 'y': -41.5},
    "SpikyChallenge": {'x': 1430.05103, 'y': -101.5},
    "Viking Tower Top Inside": {'x': 1561.42993, 'y': 158},
    "Acid Reflux": {'x': 1919.35083, 'y': 205},
    "LightningStorm": {'x': 1949.61987, 'y': 305.505524},
    "Dyspepsia": {'x': 2002.66992, 'y': 268.005524},
    "Dyspepsia Max": {'x': 1950.30872, 'y': 269.505554},
    "Galvan Tower Top Corridor": {'x': 1941.76196, 'y': 1048},
    "Galvan Tower Top Axe Entrance": {'x': 2054.77783, 'y': 1048},
    "Galvan Sidescene": {'x': 2050.92163, 'y': 905.5},
    "Vikings VS Wraiths": {'x': 2066.18994, 'y': 935.5},
    "Scroll Room Below Death Machine": {'x': 1959.66211, 'y': 923.5},
    "Galvan Living space": {'x': 2050.771, 'y': 848.5},
    "Galvan Tower Top Up and Around": {'x': 1977.88062, 'y': 921.999878},
    "Secret_2": {'x': 2038.54175, 'y': 686.158569},
    "FishboneField": {'x': 2102.76343, 'y': 750.661865},
    "Secret_3": {'x': 2090.62451, 'y': 620.150024},
    "Winter Garden": {'x': 2036.54773, 'y': 510.259064},
    "Inside Ship": {'x': 271.448761, 'y': 1044.38782},
    "Explosives Intro": {'x': 68.0093689, 'y': 1048.61218},
    "Platform": {'x': 4.59353113, 'y': 1051.97412},
    "Eating Hall": {'x': -49.855545, 'y': 1089.01514},
    "Angry Vikings": {'x': -49.4567261, 'y': 1126.95239},
    "Angry Vikings 1": {'x': -116.137756, 'y': 1163.01636},
    "Angry Vikings 2": {'x': -74.3375931, 'y': 1165.68396},
    "Resist Temptation": {'x': -76.3953781, 'y': 1190.0874},
    "Platform Hulder Escape": {'x': -112.994003, 'y': 1226.5},
    "Viking Platform Roof": {'x': -24.1000004, 'y': 1226.43018},
    "Viking Platform West": {'x': -115.404968, 'y': 1271.08679},
    "Viking Platform Chase": {'x': -144.314102, 'y': 1121.73645},
    "Helping Hair": {'x': -47.9400024, 'y': 1033.54712},
    "Crash before Halvtann": {'x': 761.11731, 'y': 637.303467},
    "Out of order": {'x': 2049.93433, 'y': 970},
    "Galvan Tower Rotating Killfield": {'x': 1981, 'y': 982},
    "Galvan Room 1": {'x': 1992.72302, 'y': 1019.5},
    "Hidden Fjord": {'x': 2217.48193, 'y': -25.2010231}
}
