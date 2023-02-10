# TeslaTwools 1.1.2

#### Speedrunning Tools for Teslagrad 2
Yes, it's just a demo right now, but I'm willing to bet that the save file format won't change too much by the time it goes retail. 

### Features:
* Automatically reads the save file.
* Detects save slot creation and deletion.
* Parses and diffs save contents with the previous checkpoint, displaying new events as they occur.
* Keeps a historical timestamped log of events. 
* Displays realtime playtime, calculated from save slot creation.

### How to use:
Run it and play Teslagrad 2. The window will update automatically as game events are recorded to the save file.

### Ideas for future improvements:
* Split capture: Given a list of events, record the playtime when each event is achieved.
* Save file editor.

#### Version History:
1.1.2: Renamed main.py to TeslaTwools.py and set up exe build. Watcher now aborts if save file does not exist.

1.1.1: Caught YAML parsing exception.

1.1.0: Added historical activity log.

1.0.0: Save file parsing and diffing. Realtime playtime.