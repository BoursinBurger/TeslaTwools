import csv
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
        self.tesla_2_path = (Path(os.getenv('APPDATA')) / '../LocalLow/Rain/Teslagrad 2').resolve()
        self.save_path = (self.tesla_2_path / 'Saves.yaml').resolve()
        self.file_watcher_path = (self.tesla_2_path /
                                  (datetime.datetime.now().strftime('File_Watcher_%Y%m%d_%H%M%S.log')))
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
                self.file_watcher_path = (self.tesla_2_path /
                                          (datetime.datetime.now().strftime('File_Watcher_%Y%m%d_%H%M%S.log')))
                self.activity_log.append(f"New Game started at {self.start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')}")

            elif active_slot_count < prev_slot_count:
                # A save slot was deleted, but which one?
                for index, save_data in enumerate(prev_save_list):
                    if index == active_slot_count or save_data != active_save_list[index]:
                        self.active_slot_number = index + 1
                        self.activity_log = list()
                        self.state = States.SAVE_SLOT_DELETED
                        self.file_watcher_path = (self.tesla_2_path /
                                                  (datetime.datetime.now().strftime('File_Watcher_%Y%m%d_%H%M%S.log')))
                        break

            else:
                # A save changed its data
                self.state = States.SAVE_SLOT_UPDATED
                for index, save_data in enumerate(active_save_list):
                    prev_save_data = prev_save_list[index]
                    if save_data != prev_save_data:
                        new_events = list()
                        self.active_slot_data = save_data
                        self.prev_slot_data = prev_save_data
                        self.time_spent = datetime.timedelta(seconds=save_data.get('timeSpent'))

                        if self.start_datetime is not None:
                            self.real_playtime = save_data.get('dateModified') - self.start_datetime

                        # Compare the rest of the keys to see if any have been changed, added, or removed
                        ignored_keys = {"dateModified", "timeSpent", "respawnFacingRight"}
                        list_keys = {"triggersSet", "mapShapesUnlocked", "activitiesUnlocked", "scrollsPickedUp",
                                     "scrollsSeenInCollection", "savedResetInfos"}
                        list_dict_keys = {"savedCharges"}
                        # For non-list keys, simply display 'key: value'
                        non_list_keys = set(save_data.keys()) - list_keys - list_dict_keys
                        for key in non_list_keys:
                            active_value = save_data.get(key)
                            prev_value = prev_save_data.get(key)
                            if active_value != prev_value:
                                new_events.append({key: str(active_value)})
                                if key not in ignored_keys:
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
                                        new_events.append({key: item})
                                if items_removed:
                                    for item in items_removed:
                                        self.log_activity(f"{key}: -{item}")
                        # For list-of-dictionary keys, display the dictionary entries that were added or removed
                        for key in list_dict_keys:
                            active_dict_items = save_data.get(key)
                            prev_dict_items = prev_save_data.get(key)
                            dicts_added = [i for i in active_dict_items if i not in prev_dict_items]
                            dicts_removed = [i for i in prev_dict_items if i not in active_dict_items]
                            if dicts_added or dicts_removed:
                                if dicts_added:
                                    for dict_item in dicts_added:
                                        self.log_activity(f"{key}: +{str(dict_item)}")
                                        new_events.append({key: str(dict_item)})
                                if dicts_removed:
                                    for dict_item in dicts_removed:
                                        self.log_activity(f"{key}: -{str(dict_item)}")

                        # Check the splits tracker and see if a split was triggered
                        if self.ui.tracker_active:
                            _, _, split_key, split_value = self.ui.tracker_next_split.values()
                            for event in new_events:
                                if split_key in event.keys() and event.get(split_key).lower() == split_value.lower():
                                    self.log_activity(f"Split '{split_key}: {split_value}' Completed")
                                    self.ui.advance_splits_tracker(self)
                                    if self.ui.tracker_completed:
                                        self.log_activity(f"All Splits Completed")
                                        if self.ui.save_run.get() == 1:
                                            completed_splits_path = (self.tesla_2_path /
                                                                     (datetime.datetime.now().strftime(
                                                                              'Completed_Run_%Y%m%d_%H%M%S.log')))
                                            with completed_splits_path.open('w') as run_log:
                                                csv_writer = csv.writer(run_log, delimiter='|', lineterminator='\n')
                                                for iid in self.ui.tv_tracker.get_children():
                                                    row = self.ui.tv_tracker.item(iid).get('values')
                                                    csv_writer.writerow(row)

                        if self.ui.save_log.get() == 1:
                            with self.file_watcher_path.open('w') as file_watcher_log:
                                file_watcher_log.writelines('\n'.join(self.activity_log))
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
    app.save_directory = watcher.tesla_2_path
    app.run()
    watcher.stop()


if __name__ == '__main__':
    main()
