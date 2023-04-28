# TeslaTwools

#### Speedrunning Tools for Teslagrad 2

### Features:
* Automatically reads the save file.
* Detects save slot creation and deletion.
* Parses and diffs save contents with the previous checkpoint, displaying new events as they occur.
* Keeps a historical timestamped log of events. 
* Displays realtime playtime, calculated from save slot creation.
* Create, Edit, Save, and Load sets of Splits, which will be tracked as you play.
* Ability to save logs of File Watcher and Completed Splits to the Teslagrad 2 Save directory. 

### How to use:
Run it and play Teslagrad 2. The window will update automatically as game events are recorded to the save file.

### Ideas for future improvements:
* Save file editor. Example edit ideas: Change Respawn Point, Ability / Scroll / Boss collection flags, Reveal map.


#### Version History:
1.2.1: Fully implemented Splits tab. Splits can be created, edited, saved, and loaded. Splits are tracked and connected to File Watcher. Added checkboxes to save Activity Log and Completed Splits.   

1.2: UI Redesign. Separated File Watcher and UI into separate classes. Split Add/Edit/Delete UI is functional, but not yet hooked into File Watcher.

1.1.3: Wipe the activity log on save slot deletion.

1.1.2: Renamed main.py to TeslaTwools.py and set up exe build. Watcher now aborts if save file does not exist.

1.1.1: Caught YAML parsing exception.

1.1: Added historical activity log.

1.0.0: Save file parsing and diffing. Realtime playtime.