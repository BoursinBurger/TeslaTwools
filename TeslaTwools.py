import os
import time
import datetime
import threading
import yaml
from pathlib import Path
from yaml.parser import ParserError
from TeslaTwoolsStatus import States, VERSION
from TeslaTwoolsUI import TeslaTwoolsUI


class FileWatcher(threading.Thread):

    def __init__(self, ui):
        threading.Thread.__init__(self)
        self.ui = ui
        self.save_path = (Path(os.getenv('APPDATA')) / '../LocalLow/Rain/Teslagrad 2/Saves.yaml').resolve()
        self.refresh_delay_secs = 0.1
        self.loop_active = True
        self.prev_mtime = 0
        self.active_save_file = None
        self.prev_save_file = None
        self.active_slot_number = None
        self.active_slot_data = None
        self.prev_slot_data = None
        self.start_datetime = None
        self.real_playtime = None
        self.time_spent = None
        self.activity_log = list()
        self.state = States.INITIALIZED
        self.start()

    def log_activity(self, activity):
        self.activity_log.append(
            f"[{self.real_playtime if self.real_playtime is not None else self.time_spent}] {activity}")

    def watch(self):
        # If the save file does not exist, terminate the watch loop
        if not self.save_path.exists():
            self.state = States.NO_SAVE_FILE
            self.loop_active = False
            return

        # Check the modified time on the save file. If the save file has not updated, abort this watch loop.
        mtime = os.stat(self.save_path).st_mtime
        if mtime == self.prev_mtime:
            self.state = States.UNCHANGED
            return

        # Read the YAML save file
        try:
            with self.save_path.open('rt', encoding='utf-8') as save:
                self.active_save_file = yaml.safe_load(save)
        # If parsing the YAML fails, abandon the current cycle. It will retry on the next loop.
        except ParserError:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}] YAML Parser Error!")
            return

        if self.prev_save_file is None:
            self.state = States.SAVE_FILE_FOUND
        else:
            # Find the difference between the previous and current save files
            prev_save_list = self.prev_save_file.get("saveDataSlots")
            active_save_list = self.active_save_file.get("saveDataSlots")
            prev_slot_count = len(prev_save_list)
            active_slot_count = len(active_save_list)
            if active_slot_count > prev_slot_count:
                # A new save slot was added
                self.start_datetime = active_save_list[active_slot_count - 1].get("dateModified")
                self.active_slot_number = active_slot_count
                self.activity_log = list()
                self.state = States.SAVE_SLOT_ADDED

            elif active_slot_count < prev_slot_count:
                # A save slot was deleted, but which one?
                for index, save_data in enumerate(prev_save_list):
                    if index == active_slot_count or save_data != active_save_list[index]:
                        self.active_slot_number = index + 1
                        self.activity_log = list()
                        self.state = States.SAVE_SLOT_DELETED
                        break

            else:
                # A save changed its data
                self.state = States.SAVE_SLOT_UPDATED
                for index, save_data in enumerate(active_save_list):
                    prev_save_data = prev_save_list[index]
                    if save_data != prev_save_data:
                        self.active_slot_data = save_data
                        self.prev_slot_data = prev_save_data
                        self.time_spent = datetime.timedelta(seconds=save_data.get('timeSpent'))

                        if self.start_datetime is not None:
                            self.real_playtime = save_data.get('dateModified') - self.start_datetime

                        # Compare the rest of the keys to see if any have been changed, added, or removed
                        ignored_keys = {"name", "dateModified", "timeSpent", "respawnFacingRight", "respawnPoint"}
                        list_keys = {"triggersSet", "mapShapesUnlocked", "activitiesUnlocked", "scrollsPickedUp",
                                     "scrollsSeenInCollection", "savedCharges", "savedResetInfos"}
                        # For non-list keys, simply display 'key: value'
                        non_list_keys = set(save_data.keys()) - ignored_keys - list_keys
                        for key in non_list_keys:
                            active_value = save_data.get(key)
                            prev_value = prev_save_data.get(key)
                            if active_value != prev_value:
                                self.log_activity(f"{key}: {active_value}")
                        # For list keys, display the series of values that have been added to or removed from the list
                        for key in list_keys:
                            active_key_items = set(save_data.get(key))
                            prev_key_items = set(prev_save_data.get(key))
                            items_added = active_key_items.difference(prev_key_items)
                            items_removed = prev_key_items.difference(active_key_items)
                            if items_added or items_removed:
                                if items_added:
                                    for item in items_added:
                                        self.log_activity(f"{key}: +{item}")
                                if items_removed:
                                    for item in items_removed:
                                        self.log_activity(f"{key}: -{item}")
                        break

        # Update the cached save data and last modified time of the save file
        self.prev_mtime = mtime
        self.prev_save_file = self.active_save_file

    def run(self):
        while self.loop_active:
            try:
                time.sleep(self.refresh_delay_secs)
                self.watch()
                self.ui.update(self)
            except KeyboardInterrupt:
                break

    def stop(self):
        self.loop_active = False
        self.join()


def main():
    print(f"TeslaTwools version {VERSION}")
    app = TeslaTwoolsUI()
    watcher = FileWatcher(app)
    app.run()
    watcher.stop()


if __name__ == '__main__':
    main()
