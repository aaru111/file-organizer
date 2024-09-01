# gui.py

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class FileOrganizerGUI:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.current_directory = os.getcwd()
        self.organized_files = []

        self.root.title("File Organizer")
        self.root.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        # Create buttons
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.dir_label = ttk.Label(self.frame, text="Current Directory:")
        self.dir_label.pack(anchor="nw", padx=10, pady=5)

        self.dir_entry = ttk.Entry(self.frame, width=50)
        self.dir_entry.insert(0, self.current_directory)
        self.dir_entry.pack(anchor="nw", padx=10, pady=5)

        self.browse_button = ttk.Button(self.frame, text="Browse", command=self.browse_directory)
        self.browse_button.pack(anchor="nw", padx=10, pady=5)

        self.list_button = ttk.Button(self.frame, text="List Files", command=self.list_files)
        self.list_button.pack(anchor="nw", padx=10, pady=5)

        self.organize_button = ttk.Button(self.frame, text="Organize Files", command=self.organize_files)
        self.organize_button.pack(anchor="nw", padx=10, pady=5)

        self.restore_button = ttk.Button(self.frame, text="Restore Files", command=self.restore_files)
        self.restore_button.pack(anchor="nw", padx=10, pady=5)

        self.blacklist_button = ttk.Button(self.frame, text="Manage Blacklist", command=self.manage_blacklist)
        self.blacklist_button.pack(anchor="nw", padx=10, pady=5)

        self.clear_button = ttk.Button(self.frame, text="Clear Screen", command=self.clear_screen)
        self.clear_button.pack(anchor="nw", padx=10, pady=5)

        self.tree = ttk.Treeview(self.frame, columns=("Name", "Type", "Size"), show='headings')
        self.tree.heading("Name", text="Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Size", text="Size")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.current_directory = directory
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def list_files(self):
        self.clear_tree()
        for item in os.listdir(self.current_directory):
            item_path = os.path.join(self.current_directory, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                self.tree.insert("", "end", values=(item, "File", f"{size:,} bytes"))
            elif os.path.isdir(item_path):
                self.tree.insert("", "end", values=(item, "Directory", ""))

    def organize_files(self):
        # Code to organize files
        pass

    def restore_files(self):
        # Code to restore files
        pass

    def manage_blacklist(self):
        # Code to manage blacklist
        pass

    def clear_screen(self):
        self.clear_tree()

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
