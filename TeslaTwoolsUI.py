#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showwarning
from TeslaTwoolsStatus import States, SplitEdit, VERSION


class TeslaTwoolsUI:
    def __init__(self, master=None):
        # build ui
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
        self.frame_non_list_keys = None
        self.frame_list_keys = None
        self.frame_activity_log = None
        self.activity_textbox = None
        self.activity_scroll = None
        self.notebook.add(self.frame_filewatcher, text='File Watcher')
        self.filewatcher_elements_drawn = False
        self.frame_splits = ttk.Frame(self.notebook)
        self.treeview = ttk.Treeview(self.frame_splits)
        self.treeview.configure(selectmode="extended", show="headings")
        self.treeview_cols = ['column_id', 'column_event', 'column_value']
        self.treeview_dcols = ['column_id', 'column_event', 'column_value']
        self.treeview.configure(columns=self.treeview_cols, displaycolumns=self.treeview_dcols)
        self.treeview.column("column_id", anchor="w", stretch=True, width=25, minwidth=20)
        self.treeview.column("column_event", anchor="w", stretch=True, width=200, minwidth=20)
        self.treeview.column("column_value", anchor="w", stretch=True, width=200, minwidth=20)
        self.treeview.heading("column_id", anchor="w", text='#')
        self.treeview.heading("column_event", anchor="w", text='Event')
        self.treeview.heading("column_value", anchor="w", text='Value')
        self.treeview.place(anchor="nw", x=0, y=0)
        self.treeview.bind('<ButtonRelease-1>', self.treeview_select)
        self.button_splits_add = ttk.Button(self.frame_splits)
        self.button_splits_add.configure(default="disabled", text='Add')
        self.button_splits_add.pack(anchor="e", expand=False, padx=10, pady=10, side="top")
        self.button_splits_add.configure(command=self.splits_add)
        self.button_splits_edit = ttk.Button(self.frame_splits)
        self.button_splits_edit.configure(default="disabled", state="disabled", text='Edit')
        self.button_splits_edit.pack(anchor="e", expand=False, padx=10, pady=10, side="top")
        self.button_splits_edit.configure(command=self.splits_edit)
        self.button_splits_delete = ttk.Button(self.frame_splits)
        self.button_splits_delete.configure(default="disabled", state="disabled", text='Delete')
        self.button_splits_delete.pack(anchor="e", expand=False, padx=10, pady=10, side="top")
        self.button_splits_delete.configure(command=self.splits_delete)
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
                    self.label_name = ttk.Label(self.frame_game_state, font=self.font, anchor="w")
                    self.label_scene = ttk.Label(self.frame_game_state, font=self.font, anchor="w")
                    self.label_coords = ttk.Label(self.frame_game_state, font=self.font, anchor="w")
                    self.label_playtime = ttk.Label(self.frame_game_state, font=self.font, anchor="w")
                    self.label_realtime = ttk.Label(self.frame_game_state, font=self.font, anchor="w")
                    self.frame_non_list_keys = ttk.Frame(self.frame_game_state)
                    self.frame_list_keys = ttk.Frame(self.frame_game_state)
                    self.frame_activity_log = ttk.Frame(self.frame_filewatcher, height=200)

                    self.activity_textbox = tk.Text(self.frame_activity_log, height=9)
                    self.activity_textbox.bind("<1>", lambda event: self.activity_textbox.focus_set())
                    self.activity_scroll = ttk.Scrollbar(self.frame_activity_log, orient='vertical',
                                                         command=self.activity_textbox.yview)
                    self.activity_textbox['yscrollcommand'] = self.activity_scroll.set
                    self.label_name.pack(anchor="w")
                    self.label_scene.pack(anchor="w")
                    self.label_coords.pack(anchor="w")
                    self.label_playtime.pack(anchor="w")
                    self.label_realtime.pack(anchor="w")
                    self.frame_non_list_keys.pack(anchor="w")
                    self.frame_list_keys.pack(anchor="w")
                    self.frame_game_state.pack(fill="both", anchor="n", expand=True, padx=0, pady=0, side=tk.TOP)
                    self.activity_scroll.pack(side=tk.RIGHT, fill='y')
                    self.activity_textbox.pack(fill="both", expand=True, padx=0, pady=0, side=tk.LEFT)
                    self.frame_activity_log.pack(fill="x", anchor="s", expand=True, padx=0, pady=0, side=tk.BOTTOM)

                # Set the text of the static game state labels
                self.label_name.config(text=f"Name: {file_watcher.active_slot_data.get('name')}")
                self.label_scene.config(text=f"Scene: {file_watcher.active_slot_data.get('respawnScene')}")
                self.label_coords.config(text=f"Coords: ({file_watcher.active_slot_data.get('respawnPoint').get('x')}, "
                                              f"{file_watcher.active_slot_data.get('respawnPoint').get('y')})")
                self.label_playtime.config(text=f"In-Game Playtime: {file_watcher.time_spent}")
                if file_watcher.start_datetime is not None:
                    self.label_realtime.config(text=f"Realtime Playtime: {file_watcher.real_playtime}")

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
                            label_non_list.pack(anchor="w")

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
                        label_list.pack(anchor="w")
                        if items_added:
                            for item in items_added:
                                label_list_add = ttk.Label(self.frame_list_keys, font=self.font, anchor="w",
                                                           text=f"    Added: {str(item)}")
                                label_list_add.pack(anchor="w")
                        if items_removed:
                            for item in items_removed:
                                label_list_remove = ttk.Label(self.frame_list_keys, font=self.font, anchor="w",
                                                              text=f"    Removed: {str(item)}")
                                label_list_remove.pack(anchor="w")

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
        iid = self.treeview.focus()
        row_dict = self.treeview.item(iid)
        self.create_split_edit_dialog(row_dict.get('values')[1], row_dict.get('values')[2])

    def splits_delete(self):
        iid = self.treeview.focus()
        self.treeview.delete(iid)
        self.reset_treeview_indices()
        self.treeview_select(None)

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
            self.treeview.insert('', tk.END, values=("x", split_event, split_value))
        else:
            # Replace the entry in the Treeview
            iid = self.treeview.focus()
            self.treeview.item(iid, values=("x", split_event, split_value))

        self.reset_treeview_indices()
        self.split_editor_window.destroy()

    def split_edit_cancel(self):
        self.split_editor_window.destroy()

    def treeview_select(self, _):
        # Enable the Edit/Delete buttons when a treeview row is selected, otherwise disable them
        if self.treeview.focus():
            self.button_splits_edit.state(["!disabled"])
            self.button_splits_delete.state(["!disabled"])
        else:
            self.button_splits_edit.state(["disabled"])
            self.button_splits_delete.state(["disabled"])

    def reset_treeview_indices(self):
        # Renumber the treeview indices
        for iid in self.treeview.get_children():
            index = self.treeview.index(iid)
            self.treeview.set(iid, 0, index + 1)