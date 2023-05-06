# TeslaTwools

#### Speedrunning Tools for Teslagrad 2

## Features:
#### File Watcher
* Automatically reads the save file.
* Detects save slot creation and deletion.
* Parses and diffs save contents with the previous checkpoint, displaying new events as they occur.
* Keeps a historical timestamped log of events. 
* Displays realtime playtime, calculated from save slot creation timestamp.
#### Splits Editor & Tracker
* Create, Edit, Save, and Load sets of Splits, which will be tracked as you play.
* Ability to save logs of File Watcher and Completed Splits to the Teslagrad 2 Save directory.
#### Save Editor
* Save Slot selector gives an overview of progress for all save slots at a glance.
* Modify a save slot's collected Equipment, defeated Bosses, explored Map Sections, collected Scrolls, triggered Triggers, and the Scene of Lumina's current location.
* Save updates to the save file, and be able to tell if there are unsaved changes.

### How to use the File Watcher:
Run it and play Teslagrad 2. The window will update automatically as game events are recorded to the save file.

### How to use the Splits Editor:
Splits are checked when new items are added to the save file, or existing items are updated. Splits are NOT checked when an item is removed. (It doesn't happen very often anyway.) Split times prioritize realtime playtime first, then in-game playtime if realtime is not available. The splits checker is case-insensitive. There are three types of data in the save file. Here's how to create splits for them:

####  Key-Value Items
These are the simplest. When adding a new split, set the Split Event to the key and the Split Value to the value. Examples:

| Split Event           | Split Value    |
|:----------------------|:---------------|
| blinkUnlocked         | true           |
| respawnScene          | Viking Hilltop |
| hulderBossfightBeaten | true           |

#### List Items
Several save attributes accumulate items underneath them. These include: triggersSet, mapShapesUnlocked, and scrollsPickedUp. When adding a new split, set the Split Event to the attribute and the Split Value to the item added. Examples:

| Split Event       | Split Value                                 |
|:------------------|:--------------------------------------------|
| triggersSet       | HulderJumpscare1                            |
| mapShapesUnlocked | Uncover_Now you are thinking with Magnets 1 |
| scrollsPickedUp   | 14                                          |

#### Dictionary Items
The savedCharges attribute keeps a list of dictionaries, each dictionary holding charge metadata. When adding a new split, set the Split Event to savedCharges and write a Python Dictionary holding the metadata for the Split Value. Example:

| Split Event  | Split Value                                                        |
|:-------------|:-------------------------------------------------------------------|
| savedCharges | {'saveID': 'Attractor-Teleporter--146440836', 'charge': 'Neutral'} |

### Ideas for future improvements:
* Hotkey trigger for LiveSplit.
* Dropdown selection and typing with autocomplete for Splits events.
* Support for Randomizer save file generation

#### Version History:
1.3: Fully implemented the Save Editor. Added a Teslagrad2Data module to hold game-specific metadata, and created classes for the Save File and its list of Save Slots. Refactored the entire program to leverage these class objects. Added the deepdiff package to easily diff save objects with each other. Substituted the PyYAML package for ruamel.yaml due to some difficulties in writing the save file in Teslagrad 2's YAML format and the need to apply a transformation after string serialization.

1.2.3: Added Retry button when save file is not found.

1.2.2: Fixed a crash when savedCharges is updated in the save file.

1.2.1: Fully implemented Splits tab. Splits can be created, edited, saved, and loaded. Splits are tracked and connected to File Watcher. Added checkboxes to save Activity Log and Completed Splits.   

1.2: UI Redesign. Separated File Watcher and UI into separate classes. Split Add/Edit/Delete UI is functional, but not yet hooked into File Watcher.

1.1.3: Wipe the activity log on save slot deletion.

1.1.2: Renamed main.py to TeslaTwools.py and set up exe build. Watcher now aborts if save file does not exist.

1.1.1: Caught YAML parsing exception.

1.1: Added historical activity log.

1.0: Save file parsing and diffing. Realtime playtime.