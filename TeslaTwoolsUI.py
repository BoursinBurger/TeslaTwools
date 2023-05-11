#!/usr/bin/python3
import os
import sys
import csv
import itertools
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showwarning, askyesnocancel
from tkinter.filedialog import asksaveasfile, askopenfile
import Teslagrad2Data
from TeslaTwoolsStatus import States, SplitEdit, VERSION


class TeslaTwoolsUI:
    def __init__(self, master=None):
        # Save file metadata
        self.save_directory = None
        self.file_watcher = None
        self.save_file = None
        self.save_editor_map = None
        self.save_editor_scrolls = None
        self.save_editor_triggers = None
        self.save_editor_scene = None
        self.save_editor_coords = None
        # UI Elements - Main Window
        self.main_window = tk.Tk() if master is None else tk.Toplevel(master)
        self.main_window.configure(height=480, relief="flat", width=640)
        self.main_window.resizable(False, False)
        self.main_window.title(f"TeslaTwools v{VERSION}")
        self.font = "Arial 12"
        self.notebook = ttk.Notebook(self.main_window)
        self.notebook.configure(height=480, width=640)
        # UI Elements - File Watcher
        self.frame_filewatcher = ttk.Frame(self.notebook)
        self.frame_filewatcher.pack(side=tk.TOP)
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
        # UI Elements - Splits
        self.frame_splits = ttk.Frame(self.notebook)
        self.labelframe_editor = ttk.Labelframe(self.frame_splits)
        self.labelframe_editor.configure(height=200, text='Splits Editor', width=320)
        self.tv_editor = ttk.Treeview(self.labelframe_editor)
        self.tv_editor.configure(height=16, selectmode="extended", show="headings")
        self.tv_editor_cols = ['editor_id', 'editor_event', 'editor_value']
        self.tv_editor_dcols = ['editor_id', 'editor_event', 'editor_value']
        self.tv_editor.configure(columns=self.tv_editor_cols, displaycolumns=self.tv_editor_dcols)
        self.tv_editor.column("editor_id", anchor=tk.W, stretch=True, width=25, minwidth=20)
        self.tv_editor.column("editor_event", anchor=tk.W, stretch=True, width=140, minwidth=20)
        self.tv_editor.column("editor_value", anchor=tk.W, stretch=True, width=140, minwidth=20)
        self.tv_editor.heading("editor_id", anchor=tk.W, text='#')
        self.tv_editor.heading("editor_event", anchor=tk.W, text='Event')
        self.tv_editor.heading("editor_value", anchor=tk.W, text='Value')
        self.tv_editor.grid(column=0, columnspan=5, padx=5, pady=10, row=0)
        self.tv_editor.bind('<ButtonRelease-1>', self.tv_editor_select)
        self.button_splits_add = ttk.Button(self.labelframe_editor)
        self.button_splits_add.configure(default="disabled", text='Add')
        self.button_splits_add.grid(column=0, row=1)
        self.button_splits_add.configure(command=self.splits_add)
        self.button_splits_moveup = ttk.Button(self.labelframe_editor)
        self.button_splits_moveup.configure(default="disabled", state=tk.DISABLED, text='🡹', width=5)
        self.button_splits_moveup.grid(column=1, row=1)
        self.button_splits_moveup.configure(command=self.splits_moveup)
        self.button_splits_edit = ttk.Button(self.labelframe_editor)
        self.button_splits_edit.configure(default="disabled", state=tk.DISABLED, text='Edit')
        self.button_splits_edit.grid(column=2, row=1)
        self.button_splits_edit.configure(command=self.splits_edit)
        self.button_splits_movedown = ttk.Button(self.labelframe_editor)
        self.button_splits_movedown.configure(default="disabled", state=tk.DISABLED, text='🡻', width=5)
        self.button_splits_movedown.grid(column=3, row=1)
        self.button_splits_movedown.configure(command=self.splits_movedown)
        self.button_splits_delete = ttk.Button(self.labelframe_editor)
        self.button_splits_delete.configure(default="disabled", state=tk.DISABLED, text='Delete')
        self.button_splits_delete.grid(column=4, row=1)
        self.button_splits_delete.configure(command=self.splits_delete)
        self.button_splits_save = ttk.Button(self.labelframe_editor)
        self.button_splits_save.configure(default="disabled", text='Save Splits...')
        self.button_splits_save.grid(column=0, columnspan=2, pady=20, row=2)
        self.button_splits_save.configure(command=self.splits_save)
        self.button_splits_default = ttk.Button(self.labelframe_editor)
        self.button_splits_default.configure(default="disabled", text='Default Splits')
        self.button_splits_default.grid(column=2, row=2, pady=20)
        self.button_splits_default.configure(command=self.splits_default)
        self.button_splits_load = ttk.Button(self.labelframe_editor)
        self.button_splits_load.configure(default="disabled", text='Load Splits...')
        self.button_splits_load.grid(column=3, columnspan=2, pady=20, row=2)
        self.button_splits_load.configure(command=self.splits_load)
        self.labelframe_editor.pack(expand=False, fill=tk.Y, padx=5, pady=5, side=tk.LEFT)
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
        self.tv_tracker.column("tracker_id", anchor=tk.W, stretch=True, width=25, minwidth=20)
        self.tv_tracker.column("tracker_event", anchor=tk.W, stretch=True, width=160, minwidth=20)
        self.tv_tracker.column("tracker_time", anchor=tk.W, stretch=True, width=100, minwidth=20)
        self.tv_tracker.heading("tracker_id", anchor=tk.W, text='#')
        self.tv_tracker.heading("tracker_event", anchor=tk.W, text='Event')
        self.tv_tracker.heading("tracker_time", anchor=tk.W, text='Time')
        self.tv_tracker.grid(column=0, row=0, padx=5, pady=10)
        self.save_log = tk.IntVar()
        self.checkbutton_save_log = ttk.Checkbutton(self.labelframe_tracker)
        self.checkbutton_save_log.configure(text='Save File Watcher events to a log file', variable=self.save_log)
        self.checkbutton_save_log.grid(column=0, row=1, padx=10, sticky=tk.W)
        self.save_run = tk.IntVar()
        self.checkbutton_save_run = ttk.Checkbutton(self.labelframe_tracker)
        self.checkbutton_save_run.configure(text='Save logs of completed splits', variable=self.save_run)
        self.checkbutton_save_run.grid(column=0, row=2, padx=10, pady=5, sticky=tk.W)
        self.livesplit_enabled = tk.IntVar()
        self.checkbutton_livesplit = ttk.Checkbutton(self.labelframe_tracker)
        self.checkbutton_livesplit.configure(text='Interface with LiveSplit Server', variable=self.livesplit_enabled,
                                             command=self.livesplit_toggle)
        self.checkbutton_livesplit.grid(column=0, row=3, padx=10, sticky=tk.W)
        self.labelframe_tracker.pack(expand=False, fill=tk.Y, padx=5, pady=5, side=tk.RIGHT)
        self.labelframe_tracker.grid_propagate(False)

        # Dialog window elements - Split Editor
        self.split_editor_window = None
        self.label_split_event = None
        self.stringvar_split_event = None
        self.accb_split_event = None
        self.label_split_value = None
        self.stringvar_split_value = None
        self.accb_split_value = None
        self.button_split_ok = None
        self.button_split_cancel = None
        self.button_retry_filewatcher = None
        self.split_edit_type = None

        self.frame_splits.pack(side=tk.TOP)
        self.notebook.add(self.frame_splits, text='Splits')
        # UI Elements - Save Editor
        self.frame_editor = ttk.Frame(self.notebook)
        self.frame_editor.configure(height=200, width=200)
        # Save Editor - Save Slot
        self.labelframe_saveslot = ttk.Labelframe(self.frame_editor)
        self.labelframe_saveslot.configure(height=100, text='Save Slot', width=200)
        self.label_slot_editing = ttk.Label(self.labelframe_saveslot)
        self.label_slot_editing.configure(text='Currently Selected Save: None')
        self.label_slot_editing.grid(column=0, row=0)
        self.button_change_save = ttk.Button(self.labelframe_saveslot)
        self.button_change_save.configure(text='Select Save')
        self.button_change_save.grid(column=1, padx=10, pady=5, row=1)
        self.button_change_save.configure(command=self.select_save)
        self.button_new_save = ttk.Button(self.labelframe_saveslot)
        self.button_new_save.configure(text='Create New Save')
        self.button_new_save.grid(column=2, padx=10, pady=5, row=1)
        self.button_new_save.configure(command=self.new_save)
        self.button_update_save = ttk.Button(self.labelframe_saveslot)
        self.button_update_save.configure(state=tk.DISABLED, text='Update Save')
        self.button_update_save.grid(column=3, padx=10, pady=5, row=1)
        self.button_update_save.configure(command=self.update_save)
        self.labelframe_saveslot.pack(fill=tk.X, padx=5, side=tk.TOP)
        # Save Editor - Equipment
        self.labelframe_equipment = ttk.Labelframe(self.frame_editor)
        self.labelframe_equipment.configure(height=100, text='Equipment', width=200)
        self.eq_blink = tk.IntVar()
        self.checkbutton_eq_blink = ttk.Checkbutton(self.labelframe_equipment)
        self.checkbutton_eq_blink.configure(text='Blink', state=tk.DISABLED,
                                            variable=self.eq_blink, command=self.display_unsaved_changes)
        self.checkbutton_eq_blink.grid(column=0, padx=5, row=0)
        self.eq_cloak = tk.IntVar()
        self.checkbutton_eq_cloak = ttk.Checkbutton(self.labelframe_equipment)
        self.checkbutton_eq_cloak.configure(text='Cloak', state=tk.DISABLED,
                                            variable=self.eq_cloak, command=self.display_unsaved_changes)
        self.checkbutton_eq_cloak.grid(column=1, padx=5, row=0)
        self.eq_waterblink = tk.IntVar()
        self.checkbutton_eq_waterblink = ttk.Checkbutton(self.labelframe_equipment)
        self.checkbutton_eq_waterblink.configure(text='Water Blink', state=tk.DISABLED,
                                                 variable=self.eq_waterblink, command=self.display_unsaved_changes)
        self.checkbutton_eq_waterblink.grid(column=2, padx=5, row=0)
        self.eq_slide = tk.IntVar()
        self.checkbutton_eq_slide = ttk.Checkbutton(self.labelframe_equipment)
        self.checkbutton_eq_slide.configure(text='Power Slide', state=tk.DISABLED,
                                            variable=self.eq_slide, command=self.display_unsaved_changes)
        self.checkbutton_eq_slide.grid(column=3, padx=5, row=0)
        self.eq_mjolnir = tk.IntVar()
        self.checkbutton_eq_mjolnir = ttk.Checkbutton(self.labelframe_equipment)
        self.checkbutton_eq_mjolnir.configure(text='Mjölnir', state=tk.DISABLED,
                                              variable=self.eq_mjolnir, command=self.display_unsaved_changes)
        self.checkbutton_eq_mjolnir.grid(column=4, padx=5, row=0)
        self.eq_axe = tk.IntVar()
        self.checkbutton_eq_axe = ttk.Checkbutton(self.labelframe_equipment)
        self.checkbutton_eq_axe.configure(text='Axe', state=tk.DISABLED,
                                          variable=self.eq_axe, command=self.display_unsaved_changes)
        self.checkbutton_eq_axe.grid(column=5, padx=5, row=0)
        self.eq_map = tk.IntVar()
        self.checkbutton_eq_map = ttk.Checkbutton(self.labelframe_equipment)
        self.checkbutton_eq_map.configure(text='Map', state=tk.DISABLED,
                                          variable=self.eq_map, command=self.display_unsaved_changes)
        self.checkbutton_eq_map.grid(column=0, padx=5, row=1)
        self.eq_redcloak = tk.IntVar()
        self.checkbutton_eq_redcloak = ttk.Checkbutton(self.labelframe_equipment)
        self.checkbutton_eq_redcloak.configure(text='Red Cloak', state=tk.DISABLED,
                                               variable=self.eq_redcloak, command=self.display_unsaved_changes)
        self.checkbutton_eq_redcloak.grid(column=1, padx=5, pady=5, row=1)
        self.eq_omniblink = tk.IntVar()
        self.checkbutton_eq_omniblink = ttk.Checkbutton(self.labelframe_equipment)
        self.checkbutton_eq_omniblink.configure(text='Directional Blink', state=tk.DISABLED,
                                                variable=self.eq_omniblink, command=self.display_unsaved_changes)
        self.checkbutton_eq_omniblink.grid(column=2, padx=5, pady=5, row=1)
        self.eq_doublejump = tk.IntVar()
        self.checkbutton_eq_doublejump = ttk.Checkbutton(self.labelframe_equipment)
        self.checkbutton_eq_doublejump.configure(text='Double Jump', state=tk.DISABLED,
                                                 variable=self.eq_doublejump, command=self.display_unsaved_changes)
        self.checkbutton_eq_doublejump.grid(column=3, padx=5, pady=5, row=1)
        self.eq_blinkaxe = tk.IntVar()
        self.checkbutton_eq_blinkaxe = ttk.Checkbutton(self.labelframe_equipment)
        self.checkbutton_eq_blinkaxe.configure(text='Blink Wire Axe', state=tk.DISABLED,
                                               variable=self.eq_blinkaxe, command=self.display_unsaved_changes)
        self.checkbutton_eq_blinkaxe.grid(column=4, padx=5, pady=5, row=1)
        self.eq_secretmap = tk.IntVar()
        self.checkbutton_eq_secretsmap = ttk.Checkbutton(self.labelframe_equipment)
        self.checkbutton_eq_secretsmap.configure(text='Secrets Map', state=tk.DISABLED,
                                                 variable=self.eq_secretmap, command=self.display_unsaved_changes)
        self.checkbutton_eq_secretsmap.grid(column=5, padx=5, pady=5, row=1)
        self.labelframe_equipment.pack(fill=tk.X, padx=5, side=tk.TOP)
        self.labelframe_equipment.grid_anchor(tk.CENTER)
        # Save Editor - Bosses
        self.labelframe_bosses = ttk.Labelframe(self.frame_editor)
        self.labelframe_bosses.configure(height=100, text='Bosses', width=200)
        self.boss_huldr = tk.IntVar()
        self.checkbutton_boss_huldr = ttk.Checkbutton(self.labelframe_bosses)
        self.checkbutton_boss_huldr.configure(text='Huldr', state=tk.DISABLED,
                                              variable=self.boss_huldr, command=self.display_unsaved_changes)
        self.checkbutton_boss_huldr.grid(column=0, padx=5, pady=5, row=0)
        self.boss_moose = tk.IntVar()
        self.checkbutton_boss_moose = ttk.Checkbutton(self.labelframe_bosses)
        self.checkbutton_boss_moose.configure(text='The First Draug', state=tk.DISABLED,
                                              variable=self.boss_moose, command=self.display_unsaved_changes)
        self.checkbutton_boss_moose.grid(column=1, padx=5, pady=5, row=0)
        self.boss_fafnir = tk.IntVar()
        self.checkbutton_boss_fafnir = ttk.Checkbutton(self.labelframe_bosses)
        self.checkbutton_boss_fafnir.configure(text='Fafnir', state=tk.DISABLED,
                                               variable=self.boss_fafnir, command=self.display_unsaved_changes)
        self.checkbutton_boss_fafnir.grid(column=2, padx=5, pady=5, row=0)
        self.boss_halvtann = tk.IntVar()
        self.checkbutton_boss_halvtann = ttk.Checkbutton(self.labelframe_bosses)
        self.checkbutton_boss_halvtann.configure(text='Halvtann', state=tk.DISABLED,
                                                 variable=self.boss_halvtann, command=self.display_unsaved_changes)
        self.checkbutton_boss_halvtann.grid(column=3, padx=5, pady=5, row=0)
        self.boss_galvan = tk.IntVar()
        self.checkbutton_boss_galvan = ttk.Checkbutton(self.labelframe_bosses)
        self.checkbutton_boss_galvan.configure(text='Galvan', state=tk.DISABLED,
                                               variable=self.boss_galvan, command=self.display_unsaved_changes)
        self.checkbutton_boss_galvan.grid(column=4, padx=5, pady=5, row=0)
        self.boss_troll = tk.IntVar()
        self.checkbutton_boss_troll = ttk.Checkbutton(self.labelframe_bosses)
        self.checkbutton_boss_troll.configure(text='Troll', state=tk.DISABLED,
                                              variable=self.boss_troll, command=self.display_unsaved_changes)
        self.checkbutton_boss_troll.grid(column=5, padx=5, pady=5, row=0)
        self.labelframe_bosses.pack(fill=tk.X, padx=5, side=tk.TOP)
        self.labelframe_bosses.grid_anchor(tk.CENTER)
        # Save Editor - Map
        self.labelframe_map = ttk.Labelframe(self.frame_editor)
        self.labelframe_map.configure(height=100, text='Map', width=200)
        self.button_show_all_map = ttk.Button(self.labelframe_map)
        self.button_show_all_map.configure(text='Show All Map Sections', state=tk.DISABLED)
        self.button_show_all_map.grid(column=1, padx=10, pady=5, row=0)
        self.button_show_all_map.configure(command=self.show_all_map)
        self.button_hide_all_map = ttk.Button(self.labelframe_map)
        self.button_hide_all_map.configure(text='Hide All Map Sections', state=tk.DISABLED)
        self.button_hide_all_map.grid(column=2, padx=10, pady=5, row=0)
        self.button_hide_all_map.configure(command=self.hide_all_map)
        self.button_choose_map_sections = ttk.Button(self.labelframe_map)
        self.button_choose_map_sections.configure(text='Choose Map Sections', state=tk.DISABLED)
        self.button_choose_map_sections.grid(column=3, padx=10, pady=5, row=0)
        self.button_choose_map_sections.configure(command=self.choose_map_sections)
        self.label_map_seen = ttk.Label(self.labelframe_map)
        self.label_map_seen.configure(text='Seen: 0', state=tk.DISABLED)
        self.label_map_seen.grid(column=0, padx=10, row=0)
        self.labelframe_map.pack(fill=tk.X, padx=5, side=tk.TOP)
        self.labelframe_map.grid_anchor(tk.CENTER)
        # Save Editor - Scrolls
        self.labelframe_scrolls = ttk.Labelframe(self.frame_editor)
        self.labelframe_scrolls.configure(height=100, text='Scrolls', width=200)
        self.button_collect_all_scrolls = ttk.Button(self.labelframe_scrolls)
        self.button_collect_all_scrolls.configure(text='Collect All Scrolls', state=tk.DISABLED)
        self.button_collect_all_scrolls.grid(column=1, padx=10, pady=5, row=0)
        self.button_collect_all_scrolls.configure(command=self.collect_all_scrolls)
        self.button_collect_no_scrolls = ttk.Button(self.labelframe_scrolls)
        self.button_collect_no_scrolls.configure(text='Collect No Scrolls', state=tk.DISABLED)
        self.button_collect_no_scrolls.grid(column=2, padx=10, pady=5, row=0)
        self.button_collect_no_scrolls.configure(command=self.collect_no_scrolls)
        self.button_choose_scrolls = ttk.Button(self.labelframe_scrolls)
        self.button_choose_scrolls.configure(text='Choose Scrolls', state=tk.DISABLED)
        self.button_choose_scrolls.grid(column=3, padx=10, pady=5, row=0)
        self.button_choose_scrolls.configure(command=self.choose_scrolls)
        self.label_scrolls_collected = ttk.Label(self.labelframe_scrolls)
        self.label_scrolls_collected.configure(text='Collected: 0/81', state=tk.DISABLED)
        self.label_scrolls_collected.grid(column=0, padx=10, row=0)
        self.labelframe_scrolls.pack(fill=tk.X, padx=5, side=tk.TOP)
        self.labelframe_scrolls.grid_anchor(tk.CENTER)
        # Save Editor - Triggers
        self.labelframe_triggers = ttk.Labelframe(self.frame_editor)
        self.labelframe_triggers.configure(height=100, text='Triggers', width=200)
        self.button_set_all_triggers = ttk.Button(self.labelframe_triggers)
        self.button_set_all_triggers.configure(text='Set All Triggers', state=tk.DISABLED)
        self.button_set_all_triggers.grid(column=1, padx=10, pady=5, row=0)
        self.button_set_all_triggers.configure(command=self.set_all_triggers)
        self.button_set_no_triggers = ttk.Button(self.labelframe_triggers)
        self.button_set_no_triggers.configure(text='Set No Triggers', state=tk.DISABLED)
        self.button_set_no_triggers.grid(column=2, padx=10, pady=5, row=0)
        self.button_set_no_triggers.configure(command=self.set_no_triggers)
        self.button_choose_triggers = ttk.Button(self.labelframe_triggers)
        self.button_choose_triggers.configure(text='Choose Triggers', state=tk.DISABLED)
        self.button_choose_triggers.grid(column=3, padx=10, pady=5, row=0)
        self.button_choose_triggers.configure(command=self.choose_triggers)
        self.label_triggers_triggered = ttk.Label(self.labelframe_triggers)
        self.label_triggers_triggered.configure(text='Triggered: 0', state=tk.DISABLED)
        self.label_triggers_triggered.grid(column=0, padx=10, row=0)
        self.labelframe_triggers.pack(fill=tk.X, padx=5, side=tk.TOP)
        self.labelframe_triggers.grid_anchor(tk.CENTER)
        # Save Editor - Scene
        self.labelframe_scene = ttk.Labelframe(self.frame_editor)
        self.labelframe_scene.configure(height=100, text='Scene', width=200)
        self.label_chosen_scene = ttk.Label(self.labelframe_scene)
        self.label_chosen_scene.configure(text='Current Scene: None', state=tk.DISABLED)
        self.label_chosen_scene.grid(column=0, row=0)
        self.button_choose_scene = ttk.Button(self.labelframe_scene)
        self.button_choose_scene.configure(text='Choose Scene', state=tk.DISABLED)
        self.button_choose_scene.grid(column=0, pady=5, row=1)
        self.button_choose_scene.configure(command=self.change_scene)
        self.labelframe_scene.pack(fill=tk.X, padx=5, side=tk.TOP)
        self.labelframe_scene.grid_anchor(tk.CENTER)

        # Dialog window elements - Save selector
        self.save_select_window = None
        self.frame_confirm_slot = None
        self.frame_select_slot = None
        self.scrollbar_selectslot = None
        self.canvas_selectslot = None
        self.innerframe_selectslot = None
        self.intvar_saveslot = None
        self.button_scene_ok = None
        self.button_slot_cancel = None
        # Dialog window elements - Map selector
        self.map_selector_window = None
        self.frame_select_map = None
        self.listbox_map = None
        self.scrollbar_map = None
        self.frame_confirm_map = None
        self.button_map_ok = None
        self.button_map_cancel = None
        # Dialog window elements - Scroll selector
        self.scroll_selector_window = None
        self.frame_confirm_scrolls = None
        self.button_scroll_ok = None
        self.button_scroll_cancel = None
        self.background_image = None
        self.scroll_selection_widget = None
        # Dialog window elements - Trigger selector
        self.trigger_selector_window = None
        self.frame_select_triggers = None
        self.listbox_triggers = None
        self.scrollbar_trigger = None
        self.frame_confirm_triggers = None
        self.button_trigger_ok = None
        self.button_trigger_cancel = None
        # Dialog window elements - Scene selector
        self.scene_select_window = None
        self.frame_confirm_scene = None
        self.button_scene_ok = None
        self.button_scene_cancel = None
        self.frame_select_scene = None
        self.canvas_selectscene = None
        self.scrollbar_selectscene = None
        self.innerframe_selectscene = None
        self.stringvar_scene = None

        self.frame_editor.pack(side=tk.TOP)
        self.notebook.add(self.frame_editor, text='Save Editor')
        self.notebook.pack(side=tk.TOP)

        # Main widget
        self.mainwindow = self.main_window

    def run(self):
        self.mainwindow.mainloop()

    # UI Functions for File Watcher
    def clear_filewatcher_frame(self):
        for widgets in self.frame_filewatcher.winfo_children():
            widgets.destroy()
        self.filewatcher_elements_drawn = False

    def update(self, file_watcher):
        self.file_watcher = file_watcher
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
                self.button_retry_filewatcher = ttk.Button(self.frame_filewatcher)
                self.button_retry_filewatcher.configure(text='Retry')
                self.button_retry_filewatcher.pack(side=tk.TOP, expand=tk.YES)
                self.button_retry_filewatcher.configure(command=self.retry_filewatcher)
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
            case States.SAVE_FILE_EDITED:
                self.clear_filewatcher_frame()
                label_msg = ttk.Label(self.frame_filewatcher, font=self.font,
                                      text=f"The save file was modified by the Save Editor.")
                label_msg.pack(side=tk.TOP, expand=tk.YES)
            case States.SAVE_SLOT_UPDATED:
                if not self.filewatcher_elements_drawn:
                    # Initialize all game state frame elements
                    self.clear_filewatcher_frame()
                    self.frame_game_state = ttk.Frame(self.frame_filewatcher, height=320)
                    self.frame_game_state.pack_propagate(False)
                    self.label_name = ttk.Label(self.frame_game_state, font=self.font, anchor=tk.W)
                    self.label_scene = ttk.Label(self.frame_game_state, font=self.font, anchor=tk.W)
                    self.label_coords = ttk.Label(self.frame_game_state, font=self.font, anchor=tk.W)
                    self.label_playtime = ttk.Label(self.frame_game_state, font=self.font, anchor=tk.W)
                    self.label_realtime = ttk.Label(self.frame_game_state, font=self.font, anchor=tk.W)
                    self.label_next_split = ttk.Label(self.frame_game_state, font=self.font, anchor=tk.SE)
                    self.frame_non_list_keys = ttk.Frame(self.frame_game_state)
                    self.frame_list_keys = ttk.Frame(self.frame_game_state)
                    self.frame_activity_log = ttk.Frame(self.frame_filewatcher, height=200)

                    self.activity_textbox = tk.Text(self.frame_activity_log, height=9)
                    self.activity_textbox.bind("<1>", lambda event: self.activity_textbox.focus_set())
                    self.activity_scroll = ttk.Scrollbar(self.frame_activity_log, orient=tk.VERTICAL,
                                                         command=self.activity_textbox.yview)
                    self.activity_textbox['yscrollcommand'] = self.activity_scroll.set
                    self.label_name.pack(anchor=tk.W, padx=5)
                    self.label_scene.pack(anchor=tk.W, padx=5)
                    self.label_coords.pack(anchor=tk.W, padx=5)
                    self.label_playtime.pack(anchor=tk.W, padx=5)
                    self.label_realtime.pack(anchor=tk.W, padx=5)
                    self.frame_non_list_keys.pack(anchor=tk.W)
                    self.frame_list_keys.pack(anchor=tk.W)
                    self.label_next_split.pack(side=tk.BOTTOM, fill=tk.X, padx=5)
                    self.frame_game_state.pack(fill=tk.BOTH, anchor=tk.N, expand=True, side=tk.TOP)
                    self.activity_scroll.pack(side=tk.RIGHT, fill=tk.Y)
                    self.activity_textbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
                    self.frame_activity_log.pack(fill=tk.X, anchor=tk.S, expand=True, side=tk.BOTTOM)

                # Set the text of the static game state labels
                self.label_name.config(text=f"Name: {file_watcher.active_slot_data.name}")
                self.label_scene.config(text=f"Scene: {file_watcher.active_slot_data.respawnScene}")
                self.label_coords.config(text=f"Coords: ({file_watcher.active_slot_data.respawnPoint.get('x')}, "
                                              f"{file_watcher.active_slot_data.respawnPoint.get('y')})")
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

                ignored_keys = {"name", "respawnScene", "respawnPoint['x']", "respawnPoint['y']"}
                # Reset Non-List and List frames
                for widgets in self.frame_non_list_keys.winfo_children():
                    widgets.destroy()
                for widgets in self.frame_list_keys.winfo_children():
                    widgets.destroy()

                for event_dict in self.file_watcher.new_events:
                    for key, new_value in event_dict.items():

                        # Skip empty values
                        if len(new_value) == 0:
                            continue

                        # Skip ignored keys
                        if key in ignored_keys:
                            continue

                        # Set non-list keys into frame_non_list_keys
                        if type(new_value) is str:
                            label_non_list = ttk.Label(self.frame_non_list_keys, font=self.font, anchor=tk.W,
                                                       text=f"{key}: {new_value}")
                            label_non_list.pack(anchor=tk.W, padx=5)

                        # Set list keys into frame_list_keys
                        if type(new_value) is list:
                            # Display the list name underlined, then display the series of values
                            label_list = ttk.Label(self.frame_list_keys, font=f"{self.font} underline", anchor=tk.W,
                                                   text=f"{key}")
                            label_list.pack(anchor=tk.W, padx=5)
                            for item in new_value:
                                label_list_add = ttk.Label(self.frame_list_keys, font=self.font, anchor=tk.W,
                                                           text=f"    Added: {str(item)}")
                                label_list_add.pack(anchor=tk.W, padx=5)

                # Update the activity textbox
                self.activity_textbox.config(state=tk.NORMAL)
                self.activity_textbox.delete(1.0, tk.END)
                self.activity_textbox.insert(1.0, "\n".join(file_watcher.activity_log))
                self.activity_textbox.see(tk.END)
                self.activity_textbox.config(state=tk.DISABLED)

                # Done with updates
                self.filewatcher_elements_drawn = True

    def retry_filewatcher(self):
        self.file_watcher.filewatcher_active = True

    # UI Functions for Splits
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

        # Event AutocompleteCombobox
        self.stringvar_split_event = tk.StringVar(value=split_event)
        self.accb_split_event = AutocompleteCombobox(self.split_editor_window, width=50)
        self.accb_split_event.set_completion_list(
            ("version", "name", "respawnScene", "blinkUnlocked", "cloakUnlocked", "waterblinkUnlocked",
             "mjolnirUnlocked", "powerSlideUnlocked", "axeUnlocked", "blinkWireAxeUnlocked", "redCloakUnlocked",
             "omniBlinkUnlocked", "doubleJumpUnlocked", "secretsMapUnlocked", "mapUnlocked", "hasMetGalvan",
             "hulderBossfightBeaten", "mooseBossFightBeaten", "fafnirBossFightBeaten", "halvtannBossFightBeaten",
             "galvanBossFightBeaten", "trollMiniBossFightBeaten", "invasionSequenceDone", "vikingBlimpOnTheHunt",
             "vikingBlimpPosition", "HulderUnderworldChaseProgression", "hulder_PreBossDiscoverTraversed",
             "hulder_PreBossLevelChaseDone", "hulder_DarkRoomLevelChaseDone", "hulder_GrueEyesLevelChaseDone",
             "triggersSet", "mapShapesUnlocked", "activitiesUnlocked", "scrollsPickedUp", "scrollsSeenInCollection",
             "savedCharges", "savedResetInfos", "gameWasCompletedOnce"))
        self.accb_split_event.configure(textvariable=self.stringvar_split_event)
        self.accb_split_event.pack(anchor=tk.W, side=tk.TOP, padx=10, pady=5)

        # Value Label
        self.label_split_value = ttk.Label(self.split_editor_window, width=50, text="Select Split Value")
        self.label_split_value.pack(side=tk.TOP, pady=5)

        # Value AutocompleteCombobox
        self.stringvar_split_value = tk.StringVar(value=split_value)
        self.accb_split_value = AutocompleteCombobox(self.split_editor_window, width=50)
        self.accb_split_value.set_completion_list(list(itertools.chain(["True", "False"],
                                                                       list(Teslagrad2Data.map_shapes),
                                                                       [str(x) for x in Teslagrad2Data.scrolls],
                                                                       list(Teslagrad2Data.triggers),
                                                                       list(Teslagrad2Data.scenes.keys()))))
        self.accb_split_value.configure(textvariable=self.stringvar_split_value)
        self.accb_split_value.pack(anchor=tk.W, side=tk.TOP, padx=10, pady=5)

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
        csv_writer = csv.writer(file, delimiter='|', lineterminator='\n')
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
        csv_reader = csv.reader(file, delimiter='|')
        for row in csv_reader:
            self.tv_editor.insert('', tk.END, values=row)
        self.reset_splits_tracker()

    def split_edit_ok(self, _=None):
        # Read the entry attributes
        split_event = self.stringvar_split_event.get()
        split_value = self.stringvar_split_value.get()

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

    def livesplit_toggle(self):
        if self.livesplit_enabled.get() == 0:
            self.file_watcher.livesplit_disconnect()
        else:
            self.file_watcher.livesplit_connect()

    # UI Functions for Save Editor
    def toggle_save_editor_elements(self, enabled: bool):
        for element in (self.checkbutton_eq_blink, self.checkbutton_eq_cloak, self.checkbutton_eq_waterblink,
                        self.checkbutton_eq_slide, self.checkbutton_eq_mjolnir, self.checkbutton_eq_axe,
                        self.checkbutton_eq_map, self.checkbutton_eq_redcloak, self.checkbutton_eq_omniblink,
                        self.checkbutton_eq_doublejump, self.checkbutton_eq_blinkaxe, self.checkbutton_eq_secretsmap,
                        self.checkbutton_boss_huldr, self.checkbutton_boss_moose, self.checkbutton_boss_fafnir,
                        self.checkbutton_boss_halvtann, self.checkbutton_boss_galvan, self.checkbutton_boss_troll,
                        self.button_show_all_map, self.button_hide_all_map, self.button_choose_map_sections,
                        self.label_map_seen, self.button_collect_all_scrolls, self.button_collect_no_scrolls,
                        self.button_choose_scrolls, self.label_scrolls_collected, self.button_set_all_triggers,
                        self.button_set_no_triggers, self.button_choose_triggers, self.label_triggers_triggered,
                        self.button_update_save, self.label_chosen_scene, self.button_choose_scene):
            element.configure(state=tk.NORMAL if enabled else tk.DISABLED)

    def check_for_unsaved_changes(self) -> bool:
        """
        Compare save slot data with the save editor UI elements.
        :return: True if any elements changed, False otherwise.
        """

        # If this gets called when a save slot is not selected, proceed without checking.
        if self.save_file is None or self.intvar_saveslot.get() == -1:
            return False

        save_slot = self.save_file.saveDataSlots[self.intvar_saveslot.get()]
        # Equipment and Bosses
        for save_item, ui_item in ((bool(self.eq_blink.get()), save_slot.blinkUnlocked),
                                   (bool(self.eq_cloak.get()), save_slot.cloakUnlocked),
                                   (bool(self.eq_waterblink.get()), save_slot.waterblinkUnlocked),
                                   (bool(self.eq_slide.get()), save_slot.powerSlideUnlocked),
                                   (bool(self.eq_mjolnir.get()), save_slot.mjolnirUnlocked),
                                   (bool(self.eq_axe.get()), save_slot.axeUnlocked),
                                   (bool(self.eq_map.get()), save_slot.mapUnlocked),
                                   (bool(self.eq_redcloak.get()), save_slot.redCloakUnlocked),
                                   (bool(self.eq_omniblink.get()), save_slot.omniBlinkUnlocked),
                                   (bool(self.eq_doublejump.get()), save_slot.doubleJumpUnlocked),
                                   (bool(self.eq_blinkaxe.get()), save_slot.blinkWireAxeUnlocked),
                                   (bool(self.eq_secretmap.get()), save_slot.secretsMapUnlocked),
                                   (bool(self.boss_huldr.get()), save_slot.hulderBossfightBeaten),
                                   (bool(self.boss_moose.get()), save_slot.mooseBossFightBeaten),
                                   (bool(self.boss_fafnir.get()), save_slot.fafnirBossFightBeaten),
                                   (bool(self.boss_halvtann.get()), save_slot.halvtannBossFightBeaten),
                                   (bool(self.boss_galvan.get()), save_slot.galvanBossFightBeaten),
                                   (bool(self.boss_troll.get()), save_slot.trollMiniBossFightBeaten)):
            if save_item != ui_item:
                return True

        # Map
        if self.save_editor_map != save_slot.mapShapesUnlocked:
            return True
        # Scrolls
        if self.save_editor_scrolls != save_slot.scrollsPickedUp:
            return True
        # Triggers
        if self.save_editor_triggers != save_slot.triggersSet:
            return True
        # Scene
        if self.save_editor_scene != save_slot.respawnScene:
            return True
        if self.save_editor_coords != save_slot.respawnPoint:
            return True

        return False

    def verify_changes(self) -> bool:
        """
        Check for unsaved changes, then if any exist, display a Yes/No/Cancel dialog asking to save before proceeding.
        :return: True if ok to proceed, False if not ok because Cancel was clicked.
        """
        # Ask to continue if there are unsaved changes
        unsaved_changes = self.check_for_unsaved_changes()
        if not unsaved_changes:
            return True

        response = askyesnocancel(title="Save Changes?",
                                  message="This save slot has unsaved changes. Save changes before proceeding?")
        if response is True:
            self.update_save()
            return True
        elif response is False:
            return True
        else:
            return False

    def display_unsaved_changes(self):
        unsaved_changes = self.check_for_unsaved_changes()
        self.label_slot_editing.configure(text=f'Currently Selected Save: Slot #{self.intvar_saveslot.get() + 1} '
                                               f'{"(*)" if unsaved_changes else ""}')
        self.button_update_save.configure(state=tk.NORMAL if unsaved_changes else tk.DISABLED)

    def select_save(self):
        ok_to_proceed = self.verify_changes()
        if not ok_to_proceed:
            return

        # Dialog Window
        self.save_select_window = tk.Toplevel(self.main_window)
        x = self.main_window.winfo_x()
        y = self.main_window.winfo_y()
        self.save_select_window.geometry(f"800x200+{x + 320:d}+{y + 175:d}")
        self.save_select_window.title("Select Save Slot")

        # Define confirmation frame first
        self.frame_confirm_slot = ttk.Frame(self.save_select_window)
        self.button_scene_ok = ttk.Button(self.frame_confirm_slot)
        self.button_scene_ok.configure(text='OK')
        self.button_scene_ok.grid(column=0, padx=10, row=0)
        self.button_scene_ok.configure(command=self.slot_ok)
        self.button_slot_cancel = ttk.Button(self.frame_confirm_slot)
        self.button_slot_cancel.configure(text='Cancel')
        self.button_slot_cancel.grid(column=1, padx=10, row=0)
        self.button_slot_cancel.configure(command=self.slot_cancel)
        self.frame_confirm_slot.pack(side=tk.BOTTOM)

        # Define slot selection frame
        self.frame_select_slot = ttk.Frame(self.save_select_window)
        self.canvas_selectslot = tk.Canvas(self.frame_select_slot)
        self.scrollbar_selectslot = ttk.Scrollbar(self.frame_select_slot,
                                                  orient=tk.VERTICAL,
                                                  command=self.canvas_selectslot.yview)
        self.innerframe_selectslot = ttk.Frame(self.canvas_selectslot)
        self.innerframe_selectslot.bind("<Configure>",
                                        lambda e: self.canvas_selectslot.configure(
                                            scrollregion=self.canvas_selectslot.bbox("all")))
        self.canvas_selectslot.create_window(0, 0, window=self.innerframe_selectslot, anchor=tk.NW)
        self.canvas_selectslot.configure(yscrollcommand=self.scrollbar_selectslot.set)

        # Parse all saves and create a radio button for each
        self.intvar_saveslot = tk.IntVar(value=-1)
        self.save_file = Teslagrad2Data.SaveFile()
        self.save_file.read()
        for index, save_slot in enumerate(self.save_file.saveDataSlots):
            playtime = save_slot.timeSpent
            scene = save_slot.respawnScene
            equipment_count = save_slot.equipment_count()
            boss_count = save_slot.boss_count()
            map_section_count = len(save_slot.mapShapesUnlocked)
            scroll_count = len(save_slot.scrollsPickedUp)
            trigger_count = len(save_slot.triggersSet)
            radiobutton_saveslot = ttk.Radiobutton(self.innerframe_selectslot)
            radiobutton_saveslot.configure(text=f'Slot #{index + 1}:{scene}, '
                                                f'Playtime: {playtime}, '
                                                f'Equipment: {equipment_count}, Bosses: {boss_count}, '
                                                f'Scrolls: {scroll_count}, Map: {map_section_count}, '
                                                f'Triggers: {trigger_count}', variable=self.intvar_saveslot,
                                           value=index)
            radiobutton_saveslot.pack(anchor=tk.W, padx=10)

        self.scrollbar_selectslot.pack(fill=tk.Y, side=tk.RIGHT)
        self.canvas_selectslot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame_select_slot.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

        # Chain the dialog to its parent and prevent parent interaction until the dialog is closed
        self.save_select_window.transient(self.main_window)
        self.save_select_window.wait_visibility()
        self.save_select_window.focus_force()
        self.save_select_window.grab_set()
        self.save_select_window.wait_window()

    def save_slot_selected(self, save_file_obj=None):
        # Enable the save editor elements
        self.toggle_save_editor_elements(True)
        if not save_file_obj:
            save_file = Teslagrad2Data.SaveFile()
            save_file.read()
            selected_save = save_file.saveDataSlots[self.intvar_saveslot.get()]
        else:
            selected_save = save_file_obj.saveDataSlots[self.intvar_saveslot.get()]
        # Set the checkboxes
        self.eq_blink.set(selected_save.blinkUnlocked)
        self.eq_cloak.set(selected_save.cloakUnlocked)
        self.eq_waterblink.set(selected_save.waterblinkUnlocked)
        self.eq_slide.set(selected_save.powerSlideUnlocked)
        self.eq_mjolnir.set(selected_save.mjolnirUnlocked)
        self.eq_axe.set(selected_save.axeUnlocked)
        self.eq_map.set(selected_save.mapUnlocked)
        self.eq_redcloak.set(selected_save.redCloakUnlocked)
        self.eq_omniblink.set(selected_save.omniBlinkUnlocked)
        self.eq_doublejump.set(selected_save.doubleJumpUnlocked)
        self.eq_blinkaxe.set(selected_save.blinkWireAxeUnlocked)
        self.eq_secretmap.set(selected_save.secretsMapUnlocked)
        self.boss_huldr.set(selected_save.hulderBossfightBeaten)
        self.boss_moose.set(selected_save.mooseBossFightBeaten)
        self.boss_fafnir.set(selected_save.fafnirBossFightBeaten)
        self.boss_halvtann.set(selected_save.halvtannBossFightBeaten)
        self.boss_galvan.set(selected_save.galvanBossFightBeaten)
        self.boss_troll.set(selected_save.trollMiniBossFightBeaten)
        # Set the lists
        self.save_editor_map = selected_save.mapShapesUnlocked
        self.save_editor_scrolls = selected_save.scrollsPickedUp
        self.save_editor_triggers = selected_save.triggersSet
        self.save_editor_scene = selected_save.respawnScene
        self.save_editor_coords = selected_save.respawnPoint
        # Set the labels
        self.label_slot_editing.configure(text=f'Currently Selected Save: Slot #{self.intvar_saveslot.get() + 1}')
        self.label_map_seen.configure(text=f'Seen: {len(self.save_editor_map)}')
        self.label_scrolls_collected.configure(text=f'Collected: {len(self.save_editor_scrolls)}/81')
        self.label_triggers_triggered.configure(text=f'Triggered: {len(self.save_editor_triggers)}')
        self.display_unsaved_changes()

    def slot_ok(self):
        self.save_slot_selected()
        self.save_select_window.destroy()

    def slot_cancel(self):
        self.save_select_window.destroy()

    def new_save(self):
        ok_to_proceed = self.verify_changes()
        if not ok_to_proceed:
            return

        if self.save_file is None:
            self.save_file = Teslagrad2Data.SaveFile()
            self.save_file.read()
        self.save_file.saveDataSlots.append(Teslagrad2Data.SaveSlot())
        self.intvar_saveslot.set(len(self.save_file.saveDataSlots) - 1)
        self.save_slot_selected(self.save_file)

    def update_save(self):
        if self.save_file is None:
            return

        selected_save = self.save_file.saveDataSlots[self.intvar_saveslot.get()]
        # Set flags
        selected_save.blinkUnlocked = bool(self.eq_blink.get())
        selected_save.cloakUnlocked = bool(self.eq_cloak.get())
        selected_save.waterblinkUnlocked = bool(self.eq_waterblink.get())
        selected_save.powerSlideUnlocked = bool(self.eq_slide.get())
        selected_save.mjolnirUnlocked = bool(self.eq_mjolnir.get())
        selected_save.axeUnlocked = bool(self.eq_axe.get())
        selected_save.mapUnlocked = bool(self.eq_map.get())
        selected_save.redCloakUnlocked = bool(self.eq_redcloak.get())
        selected_save.omniBlinkUnlocked = bool(self.eq_omniblink.get())
        selected_save.doubleJumpUnlocked = bool(self.eq_doublejump.get())
        selected_save.blinkWireAxeUnlocked = bool(self.eq_blinkaxe.get())
        selected_save.secretsMapUnlocked = bool(self.eq_secretmap.get())
        selected_save.hulderBossfightBeaten = bool(self.boss_huldr.get())
        selected_save.mooseBossFightBeaten = bool(self.boss_moose.get())
        selected_save.fafnirBossFightBeaten = bool(self.boss_fafnir.get())
        selected_save.halvtannBossFightBeaten = bool(self.boss_halvtann.get())
        selected_save.galvanBossFightBeaten = bool(self.boss_galvan.get())
        selected_save.trollMiniBossFightBeaten = bool(self.boss_troll.get())

        # Export save editor lists to the save slot
        selected_save.mapShapesUnlocked = self.save_editor_map
        selected_save.scrollsPickedUp = self.save_editor_scrolls
        selected_save.triggersSet = self.save_editor_triggers
        selected_save.respawnScene = self.save_editor_scene
        selected_save.respawnPoint = self.save_editor_coords
        self.file_watcher.state = States.SAVE_FILE_EDITED
        self.save_file.write()
        # Reload the editor lists due to potential checksum action changing their contents
        self.save_editor_map = selected_save.mapShapesUnlocked
        self.save_editor_scrolls = selected_save.scrollsPickedUp
        self.save_editor_triggers = selected_save.triggersSet
        self.display_unsaved_changes()

    def show_all_map(self):
        self.save_editor_map = Teslagrad2Data.map_shapes
        self.label_map_seen.configure(text=f'Seen: {len(self.save_editor_map)}')
        self.display_unsaved_changes()

    def hide_all_map(self):
        self.save_editor_map = list()
        self.label_map_seen.configure(text=f'Seen: {len(self.save_editor_map)}')
        self.display_unsaved_changes()

    def choose_map_sections(self):
        self.map_selector_window = tk.Toplevel(self.main_window)
        x = self.main_window.winfo_x()
        y = self.main_window.winfo_y()
        self.map_selector_window.geometry(f"300x400+{x + 320:d}+{y + 175:d}")
        self.map_selector_window.title("Select Map Sections")
        self.frame_select_map = ttk.Frame(self.map_selector_window)
        self.frame_select_map.configure(height=200, width=200)
        self.listbox_map = tk.Listbox(self.frame_select_map)
        self.scrollbar_map = ttk.Scrollbar(self.frame_select_map, orient=tk.VERTICAL, command=self.listbox_map.yview)
        self.scrollbar_map.pack(fill=tk.Y, side=tk.RIGHT)
        self.listbox_map.configure(selectmode=tk.MULTIPLE)
        self.listbox_map.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.listbox_map['yscrollcommand'] = self.scrollbar_map.set
        for index, item in enumerate(Teslagrad2Data.map_shapes):
            self.listbox_map.insert(tk.END, item)
            if item in self.save_editor_map:
                self.listbox_map.selection_set(index)
        self.frame_select_map.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.frame_confirm_map = ttk.Frame(self.map_selector_window)
        self.frame_confirm_map.configure(height=200, width=200)
        self.button_map_ok = ttk.Button(self.frame_confirm_map)
        self.button_map_ok.configure(text='OK')
        self.button_map_ok.grid(column=0, padx=10, row=0)
        self.button_map_ok.configure(command=self.map_ok)
        self.button_map_cancel = ttk.Button(self.frame_confirm_map)
        self.button_map_cancel.configure(text='Cancel')
        self.button_map_cancel.grid(column=1, padx=10, row=0)
        self.button_map_cancel.configure(command=self.map_cancel)
        self.frame_confirm_map.pack(side=tk.BOTTOM)
        # Chain the dialog to its parent and prevent parent interaction until the dialog is closed
        self.map_selector_window.transient(self.main_window)
        self.map_selector_window.wait_visibility()
        self.map_selector_window.focus_force()
        self.map_selector_window.grab_set()
        self.map_selector_window.wait_window()

    def map_ok(self):
        self.save_editor_map = [Teslagrad2Data.map_shapes[index] for index in self.listbox_map.curselection()]
        self.label_map_seen.configure(text=f'Seen: {len(self.save_editor_map)}')
        self.display_unsaved_changes()
        self.map_selector_window.destroy()

    def map_cancel(self):
        self.map_selector_window.destroy()

    def collect_all_scrolls(self):
        self.save_editor_scrolls = Teslagrad2Data.scrolls
        self.label_scrolls_collected.configure(text=f'Collected: {len(self.save_editor_scrolls)}/81')
        self.display_unsaved_changes()

    def collect_no_scrolls(self):
        self.save_editor_scrolls = list()
        self.label_scrolls_collected.configure(text=f'Collected: {len(self.save_editor_scrolls)}/81')
        self.display_unsaved_changes()

    def choose_scrolls(self):
        self.scroll_selector_window = tk.Toplevel(self.main_window)
        x = self.main_window.winfo_x()
        y = self.main_window.winfo_y()
        self.scroll_selector_window.geometry(f"640x480+{x + 320:d}+{y + 175:d}")
        self.scroll_selector_window.minsize(640, 480)
        self.scroll_selector_window.title("Select Scrolls")
        # Define the confirmation frame first, since the reverse causes an overlap
        self.frame_confirm_scrolls = ttk.Frame(self.scroll_selector_window)
        self.button_scroll_ok = ttk.Button(self.frame_confirm_scrolls)
        self.button_scroll_ok.configure(text='OK')
        self.button_scroll_ok.grid(column=0, padx=10, row=0)
        self.button_scroll_ok.configure(command=self.scrolls_ok)
        self.button_scroll_cancel = ttk.Button(self.frame_confirm_scrolls)
        self.button_scroll_cancel.configure(text='Cancel')
        self.button_scroll_cancel.grid(column=1, padx=10, row=0)
        self.button_scroll_cancel.configure(command=self.scrolls_cancel)
        self.frame_confirm_scrolls.pack(side=tk.BOTTOM)
        # Define the scroll selection frame
        scroll_map_image = resource_path("Teslagrad_2_Scroll_map.png")
        self.background_image = tk.PhotoImage(file=scroll_map_image)
        self.scroll_selection_widget = ScrollSelector(self.scroll_selector_window,
                                                      image=self.background_image,
                                                      scrollbarwidth=15,
                                                      width=4980, height=3247)
        # Set the initial vertical scroll position to 75% so the beginning area of the map is visible
        self.scroll_selection_widget.cnvs.yview_moveto(0.75)
        self.scroll_selection_widget.pack(side=tk.TOP)
        # Set the checked state for the scrolls in scrollsPickedUp
        for scroll_number in self.save_editor_scrolls:
            self.scroll_selection_widget.scroll_intvars[scroll_number - 1].set(1)
        # Chain the dialog to its parent and prevent parent interaction until the dialog is closed
        self.scroll_selector_window.transient(self.main_window)
        self.scroll_selector_window.wait_visibility()
        self.scroll_selector_window.focus_force()
        self.scroll_selector_window.grab_set()
        self.scroll_selector_window.wait_window()

    def scrolls_ok(self):
        # Set save_editor_scrolls to the indices+1 of intvars whose values are 1 (checked)
        self.save_editor_scrolls = [index + 1 for index, obj in enumerate(self.scroll_selection_widget.scroll_intvars)
                                    if obj.get() == 1]
        self.label_scrolls_collected.configure(text=f'Collected: {len(self.save_editor_scrolls)}/81')
        self.display_unsaved_changes()
        self.scroll_selector_window.destroy()

    def scrolls_cancel(self):
        self.scroll_selector_window.destroy()

    def set_all_triggers(self):
        self.save_editor_triggers = Teslagrad2Data.triggers
        self.label_triggers_triggered.configure(text=f'Triggered: {len(self.save_editor_triggers)}')
        self.display_unsaved_changes()

    def set_no_triggers(self):
        self.save_editor_triggers = list()
        self.label_triggers_triggered.configure(text=f'Triggered: {len(self.save_editor_triggers)}')
        self.display_unsaved_changes()

    def choose_triggers(self):
        self.trigger_selector_window = tk.Toplevel(self.main_window)
        x = self.main_window.winfo_x()
        y = self.main_window.winfo_y()
        self.trigger_selector_window.geometry(f"400x400+{x + 320:d}+{y + 175:d}")
        self.trigger_selector_window.title("Select Triggers")
        self.frame_select_triggers = ttk.Frame(self.trigger_selector_window)
        self.frame_select_triggers.configure(height=200, width=200)
        self.listbox_triggers = tk.Listbox(self.frame_select_triggers)
        self.scrollbar_trigger = ttk.Scrollbar(self.frame_select_triggers, orient=tk.VERTICAL,
                                               command=self.listbox_triggers.yview)
        self.scrollbar_trigger.pack(fill=tk.Y, side=tk.RIGHT)
        self.listbox_triggers.configure(selectmode="multiple")
        self.listbox_triggers.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.listbox_triggers['yscrollcommand'] = self.scrollbar_trigger.set
        for index, item in enumerate(Teslagrad2Data.triggers):
            self.listbox_triggers.insert(tk.END, item)
            if item in self.save_editor_triggers:
                self.listbox_triggers.selection_set(index)
        self.frame_select_triggers.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.frame_confirm_triggers = ttk.Frame(self.trigger_selector_window)
        self.frame_confirm_triggers.configure(height=200, width=200)
        self.button_trigger_ok = ttk.Button(self.frame_confirm_triggers)
        self.button_trigger_ok.configure(text='OK')
        self.button_trigger_ok.grid(column=0, padx=10, row=0)
        self.button_trigger_ok.configure(command=self.trigger_ok)
        self.button_trigger_cancel = ttk.Button(self.frame_confirm_triggers)
        self.button_trigger_cancel.configure(text='Cancel')
        self.button_trigger_cancel.grid(column=1, padx=10, row=0)
        self.button_trigger_cancel.configure(command=self.trigger_cancel)
        self.frame_confirm_triggers.pack(side=tk.BOTTOM)
        # Chain the dialog to its parent and prevent parent interaction until the dialog is closed
        self.trigger_selector_window.transient(self.main_window)
        self.trigger_selector_window.wait_visibility()
        self.trigger_selector_window.focus_force()
        self.trigger_selector_window.grab_set()
        self.trigger_selector_window.wait_window()

    def trigger_ok(self):
        self.save_editor_triggers = [Teslagrad2Data.triggers[index] for index in self.listbox_triggers.curselection()]
        self.label_triggers_triggered.configure(text=f'Triggered: {len(self.save_editor_triggers)}')
        self.display_unsaved_changes()
        self.trigger_selector_window.destroy()

    def trigger_cancel(self):
        self.trigger_selector_window.destroy()

    def change_scene(self):
        # Dialog Window
        self.scene_select_window = tk.Toplevel(self.main_window)
        x = self.main_window.winfo_x()
        y = self.main_window.winfo_y()
        self.scene_select_window.geometry(f"200x400+{x + 320:d}+{y + 175:d}")
        self.scene_select_window.title("Select Scene")

        # Define confirmation frame first
        self.frame_confirm_scene = ttk.Frame(self.scene_select_window)
        self.button_scene_ok = ttk.Button(self.frame_confirm_scene)
        self.button_scene_ok.configure(text='OK')
        self.button_scene_ok.grid(column=0, padx=10, row=0)
        self.button_scene_ok.configure(command=self.scene_ok)
        self.button_scene_cancel = ttk.Button(self.frame_confirm_scene)
        self.button_scene_cancel.configure(text='Cancel')
        self.button_scene_cancel.grid(column=1, padx=10, row=0)
        self.button_scene_cancel.configure(command=self.scene_cancel)
        self.frame_confirm_scene.pack(side=tk.BOTTOM)

        # Define scene selection frame
        self.frame_select_scene = ttk.Frame(self.scene_select_window)
        self.canvas_selectscene = tk.Canvas(self.frame_select_scene)
        self.scrollbar_selectscene = ttk.Scrollbar(self.frame_select_scene,
                                                   orient=tk.VERTICAL,
                                                   command=self.canvas_selectscene.yview)
        self.innerframe_selectscene = ttk.Frame(self.canvas_selectscene)
        self.innerframe_selectscene.bind("<Configure>",
                                         lambda e: self.canvas_selectscene.configure(
                                             scrollregion=self.canvas_selectscene.bbox("all")))
        self.canvas_selectscene.create_window(0, 0, window=self.innerframe_selectscene, anchor=tk.NW)
        self.canvas_selectscene.configure(yscrollcommand=self.scrollbar_selectscene.set)

        # Create a radio button for each scene
        self.stringvar_scene = tk.StringVar(value="")
        for scene_key in Teslagrad2Data.scenes.keys():
            radiobutton_scene = ttk.Radiobutton(self.innerframe_selectscene)
            radiobutton_scene.configure(text=scene_key, variable=self.stringvar_scene, value=scene_key)
            radiobutton_scene.pack(anchor=tk.W, padx=10)

        self.scrollbar_selectscene.pack(fill=tk.Y, side=tk.RIGHT)
        self.canvas_selectscene.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame_select_scene.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)

        # Chain the dialog to its parent and prevent parent interaction until the dialog is closed
        self.scene_select_window.transient(self.main_window)
        self.scene_select_window.wait_visibility()
        self.scene_select_window.focus_force()
        self.scene_select_window.grab_set()
        self.scene_select_window.wait_window()

    def scene_ok(self):
        self.save_editor_scene = self.stringvar_scene.get()
        self.save_editor_coords = Teslagrad2Data.scenes.get(self.stringvar_scene.get())
        self.label_chosen_scene.configure(text=f'Current Scene: {self.save_editor_scene}')
        self.display_unsaved_changes()
        self.scene_select_window.destroy()

    def scene_cancel(self):
        self.scene_select_window.destroy()


class AutocompleteCombobox(ttk.Combobox):

    def __init__(self, master=None, **kw):
        super(AutocompleteCombobox, self).__init__(master=master, **kw)
        self._completion_list = None
        self._hits = None
        self._hit_index = None
        self.position = None

    def set_completion_list(self, completion_list):
        """Use our completion list as our dropdown selection menu, arrows move through menu."""
        self._completion_list = sorted(completion_list, key=str.lower)  # Work with a sorted list
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list  # Setup our popup menu

    def autocomplete(self, delta=0):
        """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
        if delta:  # need to delete selection otherwise we would fix the current position
            self.delete(self.position, tk.END)
        else:  # set position to end so selection starts where textentry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):  # Match case insensitively
                _hits.append(element)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the autocompletion
        if self._hits:
            self.delete(0, tk.END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, tk.END)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "BackSpace":
            self.delete(self.index(tk.INSERT), tk.END)
            self.position = self.index(tk.END)
        if event.keysym == "Left":
            if self.position < self.index(tk.END):  # delete the selection
                self.delete(self.position, tk.END)
            else:
                self.position = self.position - 1  # delete one character
                self.delete(self.position, tk.END)
        if event.keysym == "Right":
            self.position = self.index(tk.END)  # go to end (no selection)
        if len(event.keysym) == 1:
            self.autocomplete()
        # No need for up/down, we'll jump to the popup
        # list at the position of the autocompletion


class ScrollSelector(ttk.Frame):

    def __init__(self, master=None, **kw):
        # Arrays for the 81 scrolls' checkbox values, frames, and checkboxes
        self.scroll_intvars = list()
        self.scroll_frames = list()
        self.scroll_checkbuttons = list()

        # Grab image and scrollbarwidth parameters out of **kwargs before calling super
        self.image = kw.pop('image', None)
        sw = kw.pop('scrollbarwidth', 10)
        # Initialize the super, setting the class object as a ttk Frame
        super(ScrollSelector, self).__init__(master=master, **kw)
        # A Canvas in the frame will hold the image in one layer and the scroll checkboxes in 81 separate frame layers
        self.cnvs = tk.Canvas(self, highlightthickness=0, **kw)
        # Add image to the canvas
        self.cnvs.create_image(0, 0, anchor='nw', image=self.image)
        # Add intvars, checkbox frames and checkboxes for the 81 scrolls to the canvas
        for i in range(81):
            self.scroll_intvars.append(tk.IntVar())
            self.scroll_frames.append(tk.Frame(self.cnvs))
            x_coord, y_coord = Teslagrad2Data.scroll_image_coordinates[i]
            self.cnvs.create_window(x_coord, y_coord, height=20, width=18, window=self.scroll_frames[i], anchor=tk.NW)
            self.scroll_checkbuttons.append(ttk.Checkbutton(self.scroll_frames[i], variable=self.scroll_intvars[i]))
            self.scroll_checkbuttons[i].place(x=0, y=0)
        # Vertical and Horizontal scrollbars
        self.v_scroll = tk.Scrollbar(self, orient=tk.VERTICAL, width=sw)
        self.h_scroll = tk.Scrollbar(self, orient=tk.HORIZONTAL, width=sw)
        self.sizegrip = ttk.Sizegrip(self)
        # Grid and configure weight.
        self.cnvs.grid(row=0, column=0, sticky='nsew')
        self.h_scroll.grid(row=1, column=0, sticky='ew')
        self.v_scroll.grid(row=0, column=1, sticky='ns')
        self.sizegrip.grid(row=1, column=1, sticky='se')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # Set the scrollbars to the canvas
        self.cnvs.config(xscrollcommand=self.h_scroll.set,
                         yscrollcommand=self.v_scroll.set)
        # Set canvas view to the scrollbars
        self.v_scroll.config(command=self.cnvs.yview)
        self.h_scroll.config(command=self.cnvs.xview)
        # Assign the region to be scrolled
        self.cnvs.config(scrollregion=self.cnvs.bbox('all'))
        self.cnvs.bind_class(self.cnvs, "<MouseWheel>", self.mouse_scroll)

    def mouse_scroll(self, evt):
        if evt.state == 0:
            self.cnvs.yview_scroll(int(-1 * (evt.delta / 120)), 'units')
        if evt.state == 1:
            self.cnvs.xview_scroll(int(-1 * (evt.delta / 120)), 'units')


# Helper function to fetch the map image when the program is packaged as an EXE
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
