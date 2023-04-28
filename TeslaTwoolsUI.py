#!/usr/bin/python3
import csv
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showwarning
from tkinter.filedialog import asksaveasfile, askopenfile
from TeslaTwoolsStatus import States, SplitEdit, VERSION


class TeslaTwoolsUI:
    def __init__(self, master=None):
        # build ui
        self.save_directory = None
        self.main_window = tk.Tk() if master is None else tk.Toplevel(master)
        self.main_window.configure(height=480, relief="flat", width=640)
        self.main_window.resizable(False, False)
        self.main_window.title(f"TeslaTwools v{VERSION}")
        self.font = "Arial 12"
        self.notebook = ttk.Notebook(self.main_window)
        self.notebook.configure(height=480, width=640)
        self.frame_filewatcher = ttk.Frame(self.notebook)
        self.frame_filewatcher.pack(side="top")
        self.frame_game_state = None
        self.label_name = None
        self.label_scene = None
        self.label_coords = None
        self.label_playtime = None
        self.label_realtime = None
        self.label_next_split = None
        self.frame_non_list_keys = None
        self.frame_list_keys = None
        self.frame_activity_log = None
        self.activity_textbox = None
        self.activity_scroll = None
        self.notebook.add(self.frame_filewatcher, text='File Watcher')
        self.filewatcher_elements_drawn = False
        self.frame_splits = ttk.Frame(self.notebook)
        self.labelframe_editor = ttk.Labelframe(self.frame_splits)
        self.labelframe_editor.configure(height=200, text='Splits Editor', width=320)
        self.tv_editor = ttk.Treeview(self.labelframe_editor)
        self.tv_editor.configure(height=16, selectmode="extended", show="headings")
        self.tv_editor_cols = ['editor_id', 'editor_event', 'editor_value']
        self.tv_editor_dcols = ['editor_id', 'editor_event', 'editor_value']
        self.tv_editor.configure(columns=self.tv_editor_cols, displaycolumns=self.tv_editor_dcols)
        self.tv_editor.column("editor_id", anchor="w", stretch=True, width=25, minwidth=20)
        self.tv_editor.column("editor_event", anchor="w", stretch=True, width=140, minwidth=20)
        self.tv_editor.column("editor_value", anchor="w", stretch=True, width=140, minwidth=20)
        self.tv_editor.heading("editor_id", anchor="w", text='#')
        self.tv_editor.heading("editor_event", anchor="w", text='Event')
        self.tv_editor.heading("editor_value", anchor="w", text='Value')
        self.tv_editor.grid(column=0, columnspan=5, padx=5, pady=10, row=0)
        self.tv_editor.bind('<ButtonRelease-1>', self.tv_editor_select)
        self.button_splits_add = ttk.Button(self.labelframe_editor)
        self.button_splits_add.configure(default="disabled", text='Add')
        self.button_splits_add.grid(column=0, row=1)
        self.button_splits_add.configure(command=self.splits_add)
        self.button_splits_moveup = ttk.Button(self.labelframe_editor)
        self.button_splits_moveup.configure(default="disabled", state="disabled", text='🡹', width=5)
        self.button_splits_moveup.grid(column=1, row=1)
        self.button_splits_moveup.configure(command=self.splits_moveup)
        self.button_splits_edit = ttk.Button(self.labelframe_editor)
        self.button_splits_edit.configure(default="disabled", state="disabled", text='Edit')
        self.button_splits_edit.grid(column=2, row=1)
        self.button_splits_edit.configure(command=self.splits_edit)
        self.button_splits_movedown = ttk.Button(self.labelframe_editor)
        self.button_splits_movedown.configure(default="disabled", state="disabled", text='🡻', width=5)
        self.button_splits_movedown.grid(column=3, row=1)
        self.button_splits_movedown.configure(command=self.splits_movedown)
        self.button_splits_delete = ttk.Button(self.labelframe_editor)
        self.button_splits_delete.configure(default="disabled", state="disabled", text='Delete')
        self.button_splits_delete.grid(column=4, row=1)
        self.button_splits_delete.configure(command=self.splits_delete)
        self.button_splits_save = ttk.Button(self.labelframe_editor)
        self.button_splits_save.configure(default="disabled", text='Save Splits...')
        self.button_splits_save.grid(column=0, columnspan=2, pady=20, row=2)
        self.button_splits_save.configure(command=self.splits_save)
        self.button_splits_default = ttk.Button(self.labelframe_editor)
        self.button_splits_default.configure(default="disabled", text='Default Splits')
        self.button_splits_default.grid(column=2, row=2)
        self.button_splits_default.configure(command=self.splits_default)
        self.button_splits_load = ttk.Button(self.labelframe_editor)
        self.button_splits_load.configure(default="disabled", text='Load Splits...')
        self.button_splits_load.grid(column=3, columnspan=2, pady=20, row=2)
        self.button_splits_load.configure(command=self.splits_load)
        self.labelframe_editor.pack(expand=False, fill="y", padx=5, pady=5, side="left")
        self.labelframe_editor.grid_propagate(False)
        self.labelframe_tracker = ttk.Labelframe(self.frame_splits)
        self.labelframe_tracker.configure(height=200, text='Splits Tracker', width=300)
        self.tracker_active = False
        self.tracker_completed = False
        self.tracker_next_split = {"tracker": "", "editor": "", "event": "", "value": ""}
        self.tv_tracker = ttk.Treeview(self.labelframe_tracker)
        self.tv_tracker.configure(height=16, selectmode="extended", show="headings")
        self.tv_tracker_cols = ['tracker_id', 'tracker_event', 'tracker_time']
        self.tv_tracker_dcols = ['tracker_id', 'tracker_event', 'tracker_time']
        self.tv_tracker.configure(columns=self.tv_tracker_cols, displaycolumns=self.tv_tracker_dcols)
        self.tv_tracker.column("tracker_id", anchor="w", stretch=True, width=25, minwidth=20)
        self.tv_tracker.column("tracker_event", anchor="w", stretch=True, width=160, minwidth=20)
        self.tv_tracker.column("tracker_time", anchor="w", stretch=True, width=100, minwidth=20)
        self.tv_tracker.heading("tracker_id", anchor="w", text='#')
        self.tv_tracker.heading("tracker_event", anchor="w", text='Event')
        self.tv_tracker.heading("tracker_time", anchor="w", text='Time')
        self.tv_tracker.grid(column=0, padx=5, pady=10, row=0)
        self.save_log = tk.IntVar()
        self.checkbutton_save_log = ttk.Checkbutton(self.labelframe_tracker)
        self.checkbutton_save_log.configure(text='Save File Watcher events to a log file', variable=self.save_log)
        self.checkbutton_save_log.grid(column=0, pady=10, row=1)
        self.save_run = tk.IntVar()
        self.checkbutton_save_run = ttk.Checkbutton(self.labelframe_tracker)
        self.checkbutton_save_run.configure(text='Save logs of completed splits', variable=self.save_run)
        self.checkbutton_save_run.grid(column=0, pady=10, row=2)
        self.labelframe_tracker.pack(expand=False, fill="y", padx=5, pady=5, side="right")
        self.labelframe_tracker.grid_propagate(False)
        self.split_editor_window = None
        self.label_split_event = None
        self.entry_split_event = None
        self.label_split_value = None
        self.entry_split_value = None
        self.button_split_ok = None
        self.button_split_cancel = None
        self.split_edit_type = None
        self.frame_splits.pack(side="top")
        self.notebook.add(self.frame_splits, text='Splits')
        self.frame_editor = ttk.Frame(self.notebook)
        self.frame_editor.configure(height=200, width=200)
        self.frame_editor.pack(side="top")
        self.notebook.add(self.frame_editor, text='Save Editor')
        self.notebook.pack(side="top")

        # Main widget
        self.mainwindow = self.main_window

    def run(self):
        self.mainwindow.mainloop()

    def clear_filewatcher_frame(self):
        for widgets in self.frame_filewatcher.winfo_children():
            widgets.destroy()
        self.filewatcher_elements_drawn = False

    def update(self, file_watcher):
        match file_watcher.state:
            case States.INITIALIZED:
                return
            case States.UNCHANGED:
                return
            case States.NO_SAVE_FILE:
                self.clear_filewatcher_frame()
                label_msg = ttk.Label(self.frame_filewatcher, font=self.font,
                                      text=f"Error: Teslagrad 2 save file not found at\n{str(file_watcher.save_path)}")
                label_msg.pack(side=tk.TOP, expand=tk.YES)
            case States.SAVE_FILE_FOUND:
                self.clear_filewatcher_frame()
                label_msg = ttk.Label(self.frame_filewatcher, font=self.font,
                                      text="Teslagrad 2 Save Data Loaded!\n\nYou may now play Teslagrad 2!")
                label_msg.pack(side=tk.TOP, expand=tk.YES)
            case States.SAVE_SLOT_ADDED:
                self.clear_filewatcher_frame()
                label_msg = ttk.Label(self.frame_filewatcher, font=self.font,
                                      text=f"Save Slot #{file_watcher.active_slot_number} has been added!")
                label_msg.pack(side=tk.TOP, expand=tk.YES)
            case States.SAVE_SLOT_DELETED:
                self.clear_filewatcher_frame()
                label_msg = ttk.Label(self.frame_filewatcher, font=self.font,
                                      text=f"Save Slot #{file_watcher.active_slot_number} was deleted!")
                label_msg.pack(side=tk.TOP, expand=tk.YES)
            case States.SAVE_SLOT_UPDATED:
                if not self.filewatcher_elements_drawn:
                    # Initialize all game state frame elements
                    self.clear_filewatcher_frame()
                    self.frame_game_state = ttk.Frame(self.frame_filewatcher, height=320)
                    self.frame_game_state.pack_propagate(False)
                    self.label_name = ttk.Label(self.frame_game_state, font=self.font, anchor="w")
                    self.label_scene = ttk.Label(self.frame_game_state, font=self.font, anchor="w")
                    self.label_coords = ttk.Label(self.frame_game_state, font=self.font, anchor="w")
                    self.label_playtime = ttk.Label(self.frame_game_state, font=self.font, anchor="w")
                    self.label_realtime = ttk.Label(self.frame_game_state, font=self.font, anchor="w")
                    self.label_next_split = ttk.Label(self.frame_game_state, font=self.font, anchor="se")
                    self.frame_non_list_keys = ttk.Frame(self.frame_game_state)
                    self.frame_list_keys = ttk.Frame(self.frame_game_state)
                    self.frame_activity_log = ttk.Frame(self.frame_filewatcher, height=200)

                    self.activity_textbox = tk.Text(self.frame_activity_log, height=9)
                    self.activity_textbox.bind("<1>", lambda event: self.activity_textbox.focus_set())
                    self.activity_scroll = ttk.Scrollbar(self.frame_activity_log, orient='vertical',
                                                         command=self.activity_textbox.yview)
                    self.activity_textbox['yscrollcommand'] = self.activity_scroll.set
                    self.label_name.pack(anchor="w", padx=5)
                    self.label_scene.pack(anchor="w", padx=5)
                    self.label_coords.pack(anchor="w", padx=5)
                    self.label_playtime.pack(anchor="w", padx=5)
                    self.label_realtime.pack(anchor="w", padx=5)
                    self.frame_non_list_keys.pack(anchor="w")
                    self.frame_list_keys.pack(anchor="w")
                    self.label_next_split.pack(side=tk.BOTTOM, fill="x", padx=5)
                    self.frame_game_state.pack(fill="both", anchor="n", expand=True, side=tk.TOP)
                    self.activity_scroll.pack(side=tk.RIGHT, fill='y')
                    self.activity_textbox.pack(fill="both", expand=True, side=tk.LEFT)
                    self.frame_activity_log.pack(fill="x", anchor="s", expand=True, side=tk.BOTTOM)

                # Set the text of the static game state labels
                self.label_name.config(text=f"Name: {file_watcher.active_slot_data.get('name')}")
                self.label_scene.config(text=f"Scene: {file_watcher.active_slot_data.get('respawnScene')}")
                self.label_coords.config(text=f"Coords: ({file_watcher.active_slot_data.get('respawnPoint').get('x')}, "
                                              f"{file_watcher.active_slot_data.get('respawnPoint').get('y')})")
                self.label_playtime.config(text=f"In-Game Playtime: {file_watcher.time_spent}")
                if file_watcher.start_datetime is not None:
                    self.label_realtime.config(text=f"Realtime Playtime: {file_watcher.real_playtime}")
                if self.tracker_active:
                    self.label_next_split.config(
                        text=f"Next Split: '{self.tracker_next_split.get('event')}: "
                             f"{self.tracker_next_split.get('value')}'",
                        justify="right")
                else:
                    self.label_next_split.config(text="")

                # Reset Non-List and List frames
                for widgets in self.frame_non_list_keys.winfo_children():
                    widgets.destroy()
                for widgets in self.frame_list_keys.winfo_children():
                    widgets.destroy()

                # Compare the rest of the keys to see if any have been changed, added, or removed
                ignored_keys = {"name", "dateModified", "timeSpent", "respawnFacingRight", "respawnPoint"}
                list_keys = {"triggersSet", "mapShapesUnlocked", "activitiesUnlocked", "scrollsPickedUp",
                             "scrollsSeenInCollection", "savedCharges", "savedResetInfos"}

                # For non-list keys, simply display 'key: value'
                non_list_keys = set(file_watcher.active_slot_data.keys()) - ignored_keys - list_keys
                for key in non_list_keys:
                    active_value = file_watcher.active_slot_data.get(key)
                    prev_value = file_watcher.prev_slot_data.get(key)
                    if active_value != prev_value:
                        if key != "respawnScene":
                            label_non_list = ttk.Label(self.frame_non_list_keys, font=self.font, anchor="w",
                                                       text=f"{key}: {active_value}")
                            label_non_list.pack(anchor="w", padx=5)

                # For list keys, display the list name underlined, then display the series of values
                # that have been added to or removed from the list
                for key in list_keys:
                    active_key_items = set(file_watcher.active_slot_data.get(key))
                    prev_key_items = set(file_watcher.prev_slot_data.get(key))
                    items_added = active_key_items.difference(prev_key_items)
                    items_removed = prev_key_items.difference(active_key_items)
                    if items_added or items_removed:
                        label_list = ttk.Label(self.frame_list_keys, font=f"{self.font} underline", anchor="w",
                                               text=f"{key}")
                        label_list.pack(anchor="w", padx=5)
                        if items_added:
                            for item in items_added:
                                label_list_add = ttk.Label(self.frame_list_keys, font=self.font, anchor="w",
                                                           text=f"    Added: {str(item)}")
                                label_list_add.pack(anchor="w", padx=5)
                        if items_removed:
                            for item in items_removed:
                                label_list_remove = ttk.Label(self.frame_list_keys, font=self.font, anchor="w",
                                                              text=f"    Removed: {str(item)}")
                                label_list_remove.pack(anchor="w", padx=5)

                # Update the activity textbox
                self.activity_textbox.config(state=tk.NORMAL)
                self.activity_textbox.delete(1.0, tk.END)
                self.activity_textbox.insert(1.0, "\n".join(file_watcher.activity_log))
                self.activity_textbox.see(tk.END)
                self.activity_textbox.config(state=tk.DISABLED)

                # Done with updates
                self.filewatcher_elements_drawn = True

    def create_split_edit_dialog(self, split_event="", split_value=""):
        # Dialog Window
        self.split_editor_window = tk.Toplevel(self.main_window)
        x = self.main_window.winfo_x()
        y = self.main_window.winfo_y()
        self.split_editor_window.geometry(f"320x175+{x + 320:d}+{y + 175:d}")
        self.split_editor_window.title("Configure Split Event")

        # Event Label
        self.label_split_event = ttk.Label(self.split_editor_window, width=50, text="Select Split Event")
        self.label_split_event.pack(side=tk.TOP, pady=5)

        # Event Entry
        self.entry_split_event = tk.Entry(self.split_editor_window, width=50)
        self.entry_split_event.pack(anchor="w", side=tk.TOP, padx=10, pady=5)
        self.entry_split_event.insert(0, split_event)

        # Value Label
        self.label_split_value = ttk.Label(self.split_editor_window, width=50, text="Select Split Value")
        self.label_split_value.pack(side=tk.TOP, pady=5)
        # Value Entry
        self.entry_split_value = tk.Entry(self.split_editor_window, width=50)
        self.entry_split_value.pack(anchor="w", side=tk.TOP, padx=10, pady=5)
        self.entry_split_value.insert(0, split_value)
        self.entry_split_value.bind("<Return>", self.split_edit_ok)
        # OK and Cancel Buttons
        self.button_split_ok = ttk.Button(self.split_editor_window, width=20,
                                          text="OK", command=self.split_edit_ok)
        self.button_split_ok.pack(side=tk.LEFT, padx=20)
        self.button_split_ok.bind("<Return>", self.split_edit_ok)
        self.button_split_cancel = ttk.Button(self.split_editor_window, width=20,
                                              text="Cancel", command=self.split_edit_cancel)
        self.button_split_cancel.pack(side=tk.RIGHT, padx=20)
        # Chain the dialog to its parent and prevent parent interaction until the dialog is closed
        self.split_editor_window.transient(self.main_window)
        self.split_editor_window.wait_visibility()
        self.split_editor_window.focus_force()
        self.split_editor_window.grab_set()
        self.entry_split_event.focus_set()
        self.split_editor_window.wait_window()

    def splits_add(self):
        self.split_edit_type = SplitEdit.ADD
        self.create_split_edit_dialog()

    def splits_edit(self):
        self.split_edit_type = SplitEdit.EDIT
        iid = self.tv_editor.focus()
        row_dict = self.tv_editor.item(iid)
        self.create_split_edit_dialog(row_dict.get('values')[1], row_dict.get('values')[2])

    def splits_delete(self):
        iid = self.tv_editor.focus()
        # Before we delete, get the next iid to put into focus
        # Try the next item in the tree
        next_iid = self.tv_editor.next(iid)
        # If no next item exists, try the previous item
        if not next_iid:
            next_iid = self.tv_editor.prev(iid)
        # Delete the original iid and rebuild the treeview indices
        self.tv_editor.delete(iid)
        self.reset_treeview_indices()
        # If either a next or previous item exists, select it and put it into focus
        if next_iid:
            self.tv_editor.selection_set(next_iid)
            self.tv_editor.focus(next_iid)
        self.tv_editor_select(None)
        self.reset_splits_tracker()

    def splits_moveup(self):
        iid = self.tv_editor.focus()
        self.tv_editor.move(iid, self.tv_editor.parent(iid), self.tv_editor.index(iid) - 1)
        self.tv_editor_select(None)
        self.reset_splits_tracker()

    def splits_movedown(self):
        iid = self.tv_editor.focus()
        self.tv_editor.move(iid, self.tv_editor.parent(iid), self.tv_editor.index(iid) + 1)
        self.tv_editor_select(None)
        self.reset_splits_tracker()

    def splits_save(self):
        # Get file object to export splits
        file = asksaveasfile(mode='w',
                             confirmoverwrite=True,
                             title="Save Splits As...",
                             defaultextension=".csv",
                             initialdir=self.save_directory,
                             filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        # Export splits as CSV to the file
        csv_writer = csv.writer(file, delimiter=',', lineterminator='\n')
        for iid in self.tv_editor.get_children():
            row = self.tv_editor.item(iid).get('values')
            csv_writer.writerow(row)
        file.close()

    def splits_default(self):
        for row in self.tv_editor.get_children():
            self.tv_editor.delete(row)
        self.tv_editor.insert('', tk.END, values=("x", "blinkUnlocked", "true"))
        self.tv_editor.insert('', tk.END, values=("x", "cloakUnlocked", "true"))
        self.tv_editor.insert('', tk.END, values=("x", "hulderBossfightBeaten", "true"))
        self.tv_editor.insert('', tk.END, values=("x", "mooseBossFightBeaten", "true"))
        self.tv_editor.insert('', tk.END, values=("x", "fafnirBossFightBeaten", "true"))
        self.tv_editor.insert('', tk.END, values=("x", "axeUnlocked", "true"))
        self.tv_editor.insert('', tk.END, values=("x", "galvanBossFightBeaten", "true"))
        self.reset_treeview_indices()
        self.reset_splits_tracker()

    def splits_load(self):
        # Get file object to import splits
        file = askopenfile(mode='r',
                           title="Load Splits",
                           defaultextension=".csv",
                           initialdir=self.save_directory,
                           filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        # Overwrite Treeview with CSV data
        for row in self.tv_editor.get_children():
            self.tv_editor.delete(row)
        csv_reader = csv.reader(file, delimiter=',')
        for row in csv_reader:
            self.tv_editor.insert('', tk.END, values=row)
        self.reset_splits_tracker()

    def split_edit_ok(self, _=None):
        # Read the entry attributes
        split_event = self.entry_split_event.get()
        split_value = self.entry_split_value.get()

        # If either split entry was blank, complain about it
        if not split_event or not split_value:
            showwarning(title="Invalid Split Entry", message="Split Event and Split Value must both be filled.")
            return

        # Check if an ADD or an EDIT
        if self.split_edit_type == SplitEdit.ADD:
            # Add the entry to the Treeview
            self.tv_editor.insert('', tk.END, values=("x", split_event, split_value))
        else:
            # Replace the entry in the Treeview
            iid = self.tv_editor.focus()
            self.tv_editor.item(iid, values=("x", split_event, split_value))

        self.reset_treeview_indices()
        self.reset_splits_tracker()
        self.split_editor_window.destroy()

    def split_edit_cancel(self):
        self.split_editor_window.destroy()

    def tv_editor_select(self, _):
        # Enable the Edit/Delete buttons when a treeview row is selected, otherwise disable them
        iid = self.tv_editor.focus()
        if iid:
            self.button_splits_edit.state(["!disabled"])
            self.button_splits_delete.state(["!disabled"])
            # Enable Move Up when a row other than the first one is selected
            index = self.tv_editor.index(iid)
            if index > 0:
                self.button_splits_moveup.state(["!disabled"])
            else:
                self.button_splits_moveup.state(["disabled"])
            # Enable Move Down when a row other than the last one is selected
            if index + 1 < len(self.tv_editor.get_children()):
                self.button_splits_movedown.state(["!disabled"])
            else:
                self.button_splits_movedown.state(["disabled"])
        else:
            self.button_splits_edit.state(["disabled"])
            self.button_splits_delete.state(["disabled"])

    def reset_treeview_indices(self):
        # Renumber the treeview indices
        for iid in self.tv_editor.get_children():
            index = self.tv_editor.index(iid)
            self.tv_editor.set(iid, 0, index + 1)

    def reset_splits_tracker(self):
        # Clear tracker treeview
        for row in self.tv_tracker.get_children():
            self.tv_tracker.delete(row)
        # Get splits from the editor
        splits = self.tv_editor.get_children()
        if len(splits) > 0:
            # Write splits in tracker
            for split in splits:
                split_values = self.tv_editor.item(split).get('values')
                self.tv_tracker.insert('', tk.END,
                                       values=(split_values[0], f"{split_values[1]}: {split_values[2]}", ""))
            # Highlight first split in tracker
            first_tracker_split = self.tv_tracker.get_children()[0]
            if first_tracker_split:
                self.tv_tracker.selection_set(first_tracker_split)
                # Read metadata from first split in editor
                first_editor_split = self.tv_editor.get_children()[0]
                values = self.tv_editor.item(first_editor_split).get('values')
                self.tracker_active = True
                self.tracker_completed = False
                self.tracker_next_split = {"tracker": first_tracker_split, "editor": first_editor_split,
                                           "event": values[1], "value": values[2]}

        else:
            self.tracker_active = False
            self.tracker_completed = False
            self.tracker_next_split = {"tracker": "", "editor": "", "event": "", "value": ""}

    def advance_splits_tracker(self, file_watcher):
        # Get timespan of the current event, prioritizing real playtime over in-game playtime
        timespan = file_watcher.real_playtime if file_watcher.start_datetime is not None else file_watcher.time_spent
        # Update the tracker with the timespan
        tracker_iid = self.tracker_next_split.get('tracker')
        editor_iid = self.tracker_next_split.get('editor')
        self.tv_tracker.set(tracker_iid, 2, timespan)
        # Select the next item in the tracker
        next_tracker_iid = self.tv_tracker.next(tracker_iid)
        next_editor_iid = self.tv_editor.next(editor_iid)
        if not next_tracker_iid:
            # Tracker is complete
            self.tv_tracker.selection_remove(tracker_iid)
            self.tracker_completed = True
            self.tracker_active = False
            self.tracker_next_split = {"tracker": "", "editor": "", "event": "", "value": ""}
        else:
            self.tv_tracker.selection_set(next_tracker_iid)
            values = self.tv_editor.item(next_editor_iid).get('values')
            self.tracker_next_split = {"tracker": next_tracker_iid, "editor": next_editor_iid,
                                       "event": values[1], "value": values[2]}
