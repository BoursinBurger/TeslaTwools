import os
import csv
import time
import threading
import livesplit
from pathlib import Path
from deepdiff import DeepDiff
from datetime import datetime, timedelta

import Teslagrad2Data
from TeslaTwoolsStatus import States, VERSION
from TeslaTwoolsUI import TeslaTwoolsUI


class FileWatcher(threading.Thread):

    def __init__(self, ui):
        threading.Thread.__init__(self)
        self.ui = ui
        self.tesla_2_path = (Path(os.getenv('APPDATA')) / '../LocalLow/Rain/Teslagrad 2').resolve()
        self.save_path = (self.tesla_2_path / 'Saves.yaml').resolve()
        self.file_watcher_path = (self.tesla_2_path /
                                  (datetime.now().strftime('File_Watcher_%Y%m%d_%H%M%S.log')))
        self.refresh_delay_secs = 0.1
        self.filewatcher_active = True
        self.differences = None
        self.new_events = None
        self.application_terminating = False
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
        self.livesplit_connection = None
        self.start()

    def log_activity(self, activity):
        self.activity_log.append(
            f"[{self.real_playtime if self.real_playtime is not None else self.time_spent}] {activity}")

    def livesplit_connect(self):
        self.livesplit_connection = livesplit.Livesplit()

    def livesplit_disconnect(self):
        self.livesplit_connection = None

    def livesplit_start(self):
        if self.livesplit_connection is not None:
            self.livesplit_connection.startTimer()
            self.livesplit_connection.startGameTimer()

    def livesplit_split(self):
        if self.livesplit_connection is not None:
            self.livesplit_connection.split()

    def livesplit_reset(self):
        if self.livesplit_connection is not None:
            self.livesplit_connection.reset()

    def watch(self):
        # If the save file does not exist, terminate the watch loop
        if not self.save_path.exists():
            self.state = States.NO_SAVE_FILE
            self.filewatcher_active = False
            return

        # Check the modified time on the save file. If the save file has not updated, abort this watch loop.
        mtime = os.stat(self.save_path).st_mtime
        if mtime == self.prev_mtime:
            self.state = States.UNCHANGED
            return

        # If the save file was modified by the save editor, clear the activity log and abort this watch loop.
        if self.state == States.SAVE_FILE_EDITED:
            self.activity_log = list()
            # Update the cached save data and last modified time of the save file
            self.prev_mtime = mtime
            self.prev_save_file = self.active_save_file
            # Reset the livesplit run
            self.livesplit_reset()
            return

        # Read the YAML save file
        self.active_save_file = Teslagrad2Data.SaveFile()
        self.active_save_file.read()

        if self.prev_save_file is None:
            self.state = States.SAVE_FILE_FOUND
        else:
            # Find the difference between the previous and current save files
            prev_save_list = self.prev_save_file.saveDataSlots
            active_save_list = self.active_save_file.saveDataSlots
            prev_slot_count = len(prev_save_list)
            active_slot_count = len(active_save_list)
            if active_slot_count > prev_slot_count:
                # A new save slot was added
                self.start_datetime = active_save_list[active_slot_count - 1].dateModified
                self.active_slot_number = active_slot_count
                self.activity_log = list()
                self.state = States.SAVE_SLOT_ADDED
                self.file_watcher_path = (self.tesla_2_path /
                                          (datetime.now().strftime('File_Watcher_%Y%m%d_%H%M%S.log')))
                self.activity_log.append(f"New Game started at {self.start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')}")
                # Reset and start the livesplit run
                self.livesplit_reset()
                self.livesplit_start()

            elif active_slot_count < prev_slot_count:
                # A save slot was deleted, but which one?
                for index, save_data in enumerate(prev_save_list):
                    if index == active_slot_count or len(DeepDiff(save_data, active_save_list[index])) > 0:
                        self.active_slot_number = index + 1
                        self.activity_log = list()
                        self.state = States.SAVE_SLOT_DELETED
                        self.file_watcher_path = (self.tesla_2_path /
                                                  (datetime.now().strftime('File_Watcher_%Y%m%d_%H%M%S.log')))
                        # Reset the livesplit run
                        self.livesplit_reset()
                        break

            else:
                # A save changed its data
                self.state = States.SAVE_SLOT_UPDATED
                for index, save_data in enumerate(active_save_list):
                    prev_save_data = prev_save_list[index]
                    # Compare the class objects to see if any have been changed, added, or removed
                    self.differences = DeepDiff(prev_save_data, save_data)
                    if len(self.differences) > 0:
                        self.new_events = list()
                        self.active_slot_data = save_data
                        self.prev_slot_data = prev_save_data
                        self.time_spent = timedelta(**{key: float(val)
                                                       for val, key in zip(save_data.timeSpent.split(":")[::-1],
                                                                           ("seconds", "minutes", "hours", "days"))
                                                       })
                        if self.start_datetime is not None:
                            self.real_playtime = save_data.dateModified - self.start_datetime

                        ignored_keys = {"dateModified", "timeSpent", "respawnFacingRight"}
                        list_keys = {"triggersSet", "mapShapesUnlocked", "activitiesUnlocked", "scrollsPickedUp",
                                     "scrollsSeenInCollection", "savedResetInfos", "savedCharges"}

                        # Iterate the keys of the DeepDiff differences

                        # Non-List key diffs are kept in "values_changed" - get new value and set a new event for each
                        values_changed = self.differences.get("values_changed", dict())
                        for key, value_dict in values_changed.items():
                            # Strip the root header from "root.key"
                            key = key.replace("root.", "")
                            # Skip ignored keys
                            if key in ignored_keys:
                                continue
                            # Get the new_value and append the new event, then log the new event
                            new_value = str(value_dict.get("new_value"))
                            self.new_events.append({key: new_value})
                            self.log_activity(f"{key}: {new_value}")

                        # New List keys are kept in "iterable_item_added" - get new values and set an event for the list
                        iterable_item_added = self.differences.get("iterable_item_added", dict())
                        # Iterate the list keys and get all diff entries for each
                        for list_key in list_keys:
                            new_values = list()
                            for diff_key, diff_value in iterable_item_added.items():
                                if list_key in diff_key:
                                    new_values.append(str(diff_value))
                                    self.log_activity(f"{list_key}: +{str(diff_value)}")
                            self.new_events.append({list_key: new_values})

                        # Check the splits tracker and see if a split was triggered
                        if self.ui.tracker_active:
                            _, _, split_key, split_value = self.ui.tracker_next_split.values()
                            for event_dict in self.new_events:
                                if split_key.lower() in (string.lower() for string in event_dict.keys()):
                                    event_value = event_dict.get(split_key)
                                    if type(event_value) is str and split_value.lower() == event_value.lower() or type(
                                            event_value) is list and split_value.lower() in (string.lower() for string
                                                                                             in event_value):
                                        # Send a split to livesplit
                                        self.livesplit_split()
                                        # Log the split
                                        self.log_activity(f"Split '{split_key}: {split_value}' Completed")
                                        # Move to the next split in the UI
                                        self.ui.advance_splits_tracker(self)
                                        # Check if we are finished tracking splits
                                        if self.ui.tracker_completed:
                                            self.log_activity(f"All Splits Completed")
                                            if self.ui.save_run.get() == 1:
                                                completed_splits_path = (self.tesla_2_path /
                                                                         (datetime.now().strftime(
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
        while not self.application_terminating:
            try:
                time.sleep(self.refresh_delay_secs)
                if self.filewatcher_active:
                    self.watch()
                    self.ui.update(self)
            except KeyboardInterrupt:
                break

    def stop(self):
        self.filewatcher_active = False
        self.application_terminating = True
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
