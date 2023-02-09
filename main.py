import os
import time
import datetime
import threading
import yaml
import tkinter as tk
from pathlib import Path
from yaml.parser import ParserError

version = "1.1.1"


class FileWatcher(threading.Thread):
    save_path = (Path(os.getenv('APPDATA')) / '../LocalLow/Rain/Teslagrad 2/Saves.yaml').resolve()
    refresh_delay_secs = 0.1

    def __init__(self, tk_root):
        threading.Thread.__init__(self)
        self.window = tk_root
        self.window.title("TeslaTwools")
        self.save_data_frame = tk.Frame(self.window)
        self.activity_frame = tk.Frame(self.window)
        self.font = "Arial 12"
        self.loop_active = True
        self.prev_mtime = 0
        self.prev_save = None
        self.start_datetime = None
        self.real_playtime = None
        self.time_spent = None
        self.activity_log = list()
        self.start()

    def log_activity(self, activity):
        self.activity_log.append(
            f"[{self.real_playtime if self.real_playtime is not None else self.time_spent}] {activity}")

    def watch(self):
        mtime = os.stat(self.save_path).st_mtime
        if mtime == self.prev_mtime:
            return
        # The save file has updated
        self.prev_mtime = mtime
        # Read the YAML save file
        try:
            with self.save_path.open('rt', encoding='utf-8') as save:
                all_saves = yaml.safe_load(save)
        # If parsing the YAML fails, abandon the current cycle. It will retry on the next loop.
        except ParserError:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}] YAML Parser Error!")
            return
        # Prepare new window frames
        new_sd_frame = tk.Frame(self.window)
        new_ac_frame = None

        if self.prev_save is None:
            # First time the save file has been read
            label_msg = tk.Label(new_sd_frame, font=self.font, width=50,
                                 text="Teslagrad 2 Save Data Loaded!")
            label_msg.pack(anchor="w")
            label_msg2 = tk.Label(new_sd_frame, font=self.font, width=50,
                                  text="You may now play Teslagrad 2")
            label_msg2.pack(anchor="w")
        else:
            # Find the difference between the previous and current save files
            prev_save_list = self.prev_save.get("saveDataSlots")
            curr_save_list = all_saves.get("saveDataSlots")
            prev_slot_count = len(prev_save_list)
            curr_slot_count = len(curr_save_list)
            if curr_slot_count > prev_slot_count:
                # A new save slot was added
                label_msg = tk.Label(new_sd_frame, font=self.font, width=50,
                                     text=f"Save Slot #{curr_slot_count} has been added!")
                label_msg.pack()
                self.start_datetime = curr_save_list[curr_slot_count - 1].get("dateModified")
                label_time_start = tk.Label(new_sd_frame, font=self.font, width=50,
                                            text=f"Start Time: {self.start_datetime}")
                label_time_start.pack()
                self.activity_log = list()
            elif curr_slot_count < prev_slot_count:
                # A save slot was deleted, but which one?
                for index, save_data in enumerate(prev_save_list):
                    if index == curr_slot_count or save_data != curr_save_list[index]:
                        label_msg = tk.Label(new_sd_frame, font=self.font, width=50,
                                             text=f"Save Slot #{index + 1} was deleted!")
                        label_msg.pack()
                        break

            else:
                # A save changed its data
                for index, save_data in enumerate(curr_save_list):
                    prev_save_data = prev_save_list[index]
                    if save_data != prev_save_data:
                        # Update the labels that will always be displayed
                        label_name = tk.Label(new_sd_frame, font=self.font, anchor="w",
                                              text=f"Name: {save_data.get('name')}")
                        label_name.pack(anchor="w")
                        label_scene = tk.Label(new_sd_frame, font=self.font, anchor="w",
                                               text=f"Scene: {save_data.get('respawnScene')}")
                        label_scene.pack(anchor="w")
                        label_coords = tk.Label(new_sd_frame, font=self.font, anchor="w",
                                                text=f"Coords: ({save_data.get('respawnPoint').get('x')}, "
                                                     f"{save_data.get('respawnPoint').get('y')})")
                        label_coords.pack(anchor="w")
                        self.time_spent = datetime.timedelta(seconds=save_data.get('timeSpent'))
                        label_playtime = tk.Label(new_sd_frame, font=self.font, anchor="w",
                                                  text=f"In-Game Playtime: {self.time_spent}")
                        label_playtime.pack(anchor="w")

                        if self.start_datetime is not None:
                            self.real_playtime = save_data.get('dateModified') - self.start_datetime
                            label_realtime = tk.Label(new_sd_frame, font=self.font, anchor="w",
                                                      text=f"Realtime Playtime: {self.real_playtime}")
                            label_realtime.pack(anchor="w")

                        # Compare the rest of the keys to see if any have been changed, added, or removed
                        ignored_keys = {"name", "dateModified", "timeSpent", "respawnFacingRight", "respawnPoint"}
                        list_keys = {"triggersSet", "mapShapesUnlocked", "activitiesUnlocked", "scrollsPickedUp",
                                     "scrollsSeenInCollection", "savedCharges", "savedResetInfos"}
                        # For non-list keys, simply display 'key: value'
                        non_list_keys = set(save_data.keys()) - ignored_keys - list_keys
                        for key in non_list_keys:
                            curr_value = save_data.get(key)
                            prev_value = prev_save_data.get(key)
                            if curr_value != prev_value:
                                # Ignore respawnScene for non-list updates, but log activity when it changes
                                if key != "respawnScene":
                                    label_non_list = tk.Label(new_sd_frame, font=self.font, anchor="w",
                                                              text=f"{key}: {curr_value}")
                                    label_non_list.pack(anchor="w")
                                self.log_activity(f"{key}: {curr_value}")
                        # For list keys, display the list name underlined, then display the series of values
                        # that have been added to or removed from the list
                        for key in list_keys:
                            curr_key_items = set(save_data.get(key))
                            prev_key_items = set(prev_save_data.get(key))
                            items_added = curr_key_items.difference(prev_key_items)
                            items_removed = prev_key_items.difference(curr_key_items)
                            if items_added or items_removed:
                                label_list = tk.Label(new_sd_frame, font=f"{self.font} underline", anchor="w",
                                                      text=f"{key}")
                                label_list.pack(anchor="w")
                                if items_added:
                                    for item in items_added:
                                        label_list_add = tk.Label(new_sd_frame, font=self.font, anchor="w",
                                                                  text=f"    Added: {str(item)}")
                                        label_list_add.pack(anchor="w")
                                        self.log_activity(f"{key}: +{item}")
                                if items_removed:
                                    for item in items_removed:
                                        label_list_remove = tk.Label(new_sd_frame, font=self.font, anchor="w",
                                                                     text=f"    Removed: {str(item)}")
                                        label_list_remove.pack(anchor="w")
                                        self.log_activity(f"{key}: -{item}")

                        # Prepare a new activity frame
                        new_ac_frame = tk.Frame(self.window)
                        activity_textbox = tk.Text(new_ac_frame, height=9)
                        activity_textbox.insert(tk.END, "\n".join(self.activity_log))
                        activity_textbox.see(tk.END)
                        activity_textbox.config(state=tk.DISABLED)
                        activity_textbox.bind("<1>", lambda event: activity_textbox.focus_set())
                        # Add a vertical scrollbar
                        v = tk.Scrollbar(new_ac_frame, orient='vertical', command=activity_textbox.yview)
                        v.pack(side=tk.RIGHT, fill='y')
                        activity_textbox.pack()

                        break
        # Replace the old frames with the new ones
        self.save_data_frame.destroy()
        self.save_data_frame = new_sd_frame
        self.save_data_frame.pack(fill="both", expand=True, padx=0, pady=0, side=tk.LEFT)
        if new_ac_frame is not None:
            self.activity_frame.destroy()
            self.activity_frame = new_ac_frame
            self.activity_frame.pack(fill="y", expand=True, padx=0, pady=0, side=tk.RIGHT)
        # Update the cached save data
        self.prev_save = all_saves

    def run(self):
        while self.loop_active:
            try:
                time.sleep(self.refresh_delay_secs)
                self.watch()
            except KeyboardInterrupt:
                break

    def stop(self):
        self.loop_active = False
        self.join()


def main():
    window = tk.Tk()
    watcher = FileWatcher(window)
    window.mainloop()
    watcher.stop()


if __name__ == '__main__':
    print(f"TeslaTwools version {version}")
    main()
