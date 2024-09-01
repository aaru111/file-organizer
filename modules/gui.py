# modules/gui.py

import os
import json
import shutil
from abc import ABC, abstractmethod
from tkinter import Tk, filedialog, messagebox, simpledialog
from tkinter.ttk import Frame, Button, Treeview, Scrollbar, Style
from modules.error_handler import error_handler
from modules.help import get_help_table
from rich.console import Console

console = Console()


class ConfigManager:
    CONFIG_DIR = "config"
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

    @staticmethod
    def load_config():
        if not os.path.exists(ConfigManager.CONFIG_DIR):
            os.makedirs(ConfigManager.CONFIG_DIR)
        if not os.path.exists(ConfigManager.CONFIG_FILE):
            default_config = {
                "blacklisted_files": [],
                "blacklisted_directories": [],
                "blacklisted_filetypes": []
            }
            with open(ConfigManager.CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
        with open(ConfigManager.CONFIG_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def save_config(config):
        with open(ConfigManager.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)


class FileOrganizer(ABC):

    def __init__(self, config):
        self.config = config

    @staticmethod
    def get_file_extension(file_path):
        return os.path.splitext(file_path)[1][1:].lower()

    @staticmethod
    def create_folder(directory, folder_name):
        folder_path = os.path.join(directory, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    @staticmethod
    def move_file(file_path, new_path):
        shutil.move(file_path, new_path)
        return file_path, new_path

    @abstractmethod
    def organize_files(self, directory, specific_type=None):
        pass

    def is_blacklisted(self, file_path, filename):
        """
        Check if a file or directory is blacklisted.
        """
        file_extension = self.get_file_extension(filename)
        is_blacklisted_file = filename in self.config['blacklisted_files']
        is_blacklisted_dir = any(
            os.path.commonpath([bl, file_path]) == bl
            for bl in self.config['blacklisted_directories'])
        is_blacklisted_type = file_extension in self.config[
            'blacklisted_filetypes']

        return is_blacklisted_file or is_blacklisted_dir or is_blacklisted_type


class SyncFileOrganizer(FileOrganizer):

    def __init__(self, config):
        super().__init__(config)

    def organize_files(self, directory, specific_type=None):
        organized_files = []
        file_categories = {
            'Documents': ['txt', 'doc', 'docx', 'pdf', 'rtf', 'odt'],
            'Images': ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
            'Audio': ['mp3', 'wav', 'ogg', 'flac'],
            'Videos': ['mp4', 'avi', 'mkv', 'mov']
        }

        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                if self.is_blacklisted(file_path, filename):
                    continue

                if os.path.isfile(file_path):
                    file_extension = self.get_file_extension(file_path)
                    if specific_type and file_extension != specific_type:
                        continue
                    category_folder = next(
                        (cat for cat, exts in file_categories.items()
                         if file_extension in exts), 'Others')

                    if category_folder == 'Documents':
                        category_folder = self.create_folder(
                            directory, category_folder)
                        extension_folder = self.create_folder(
                            category_folder, file_extension.upper())
                        new_path = os.path.join(extension_folder, filename)
                    else:
                        category_folder = self.create_folder(
                            directory, category_folder)
                        new_path = os.path.join(category_folder, filename)

                    organized_files.append(self.move_file(file_path, new_path))

        return organized_files


def delete_empty_folders(path):
    """
    Delete empty folders recursively from the given path.
    """
    if not os.path.isdir(path):
        return
    # Remove empty subdirectories
    for subdir in os.listdir(path):
        full_path = os.path.join(path, subdir)
        if os.path.isdir(full_path):
            delete_empty_folders(full_path)
    # Remove the directory itself if it's empty
    if not os.listdir(path):
        os.rmdir(path)


def restore_files(organized_files):
    for original_path, new_path in organized_files:
        if os.path.exists(new_path):
            shutil.move(new_path, original_path)
    delete_empty_folders(current_directory)
    messagebox.showinfo("File Organizer",
                        "Files restored to their original locations.")


def show_blacklist(config):
    blacklist_message = ""
    for key in [
            'blacklisted_files', 'blacklisted_directories',
            'blacklisted_filetypes'
    ]:
        if config[key]:
            blacklist_message += f"Blacklisted {key.split('_')[1].capitalize()}: " + ", ".join(
                config[key]) + "\n"
    if not blacklist_message:
        blacklist_message = "All blacklists are empty."
    messagebox.showinfo("Blacklist", blacklist_message)


def handle_blacklist(action, items, config):
    """
    Handles adding or removing items from the blacklist in batch.
    """
    items_list = items.split(",")  # Allow multiple items separated by commas
    for item in items_list:
        item = item.strip()  # Remove any extra spaces
        item_type = ('filetypes' if item.startswith('.') else
                     'directories' if os.path.isdir(item) else 'files')
        blacklist_key = f'blacklisted_{item_type}'

        if action == 'add':
            if item not in config[blacklist_key]:
                config[blacklist_key].append(item)
                messagebox.showinfo(
                    "Blacklist", f"Added '{item}' to blacklisted {item_type}.")
            else:
                messagebox.showwarning(
                    "Blacklist",
                    f"'{item}' is already in blacklisted {item_type}.")
        elif action == 'remove':
            if item in config[blacklist_key]:
                config[blacklist_key].remove(item)
                messagebox.showinfo(
                    "Blacklist",
                    f"Removed '{item}' from blacklisted {item_type}.")
            else:
                messagebox.showwarning(
                    "Blacklist",
                    f"'{item}' not found in blacklisted {item_type}.")

    ConfigManager.save_config(
        config)  # Save the updated config after processing all items


def get_directory_stats(directory):
    total_files = total_dirs = total_size = 0
    for root, dirs, files in os.walk(directory):
        total_dirs += len(dirs)
        total_files += len(files)
        total_size += sum(
            os.path.getsize(os.path.join(root, name)) for name in files)
    return total_files, total_dirs, total_size


def search_files(directory, query):
    results = []
    for root, _, files in os.walk(directory):
        results.extend(
            os.path.join(root, file) for file in files
            if query.lower() in file.lower())
    return results


def update_tree(tree, directory):
    for i in tree.get_children():
        tree.delete(i)

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            tree.insert('',
                        'end',
                        text=item,
                        values=("File", os.path.getsize(item_path)))
        else:
            tree.insert('', 'end', text=item, values=("Directory", ""))


def launch_gui():
    global current_directory

    root = Tk()
    root.title("File Organizer GUI")
    root.geometry("800x600")

    style = Style()
    style.configure("Treeview", rowheight=25)

    button_frame = Frame(root)
    button_frame.pack(fill='x')

    current_directory = os.getcwd()
    organized_files = []

    config = ConfigManager.load_config()
    organizer = SyncFileOrganizer(config)

    def open_directory():
        global current_directory
        directory = filedialog.askdirectory(initialdir=current_directory)
        if directory:
            current_directory = directory
            update_tree(tree, current_directory)

    def on_organize():
        filetype = simpledialog.askstring(
            "File Organizer",
            "Enter file type to organize (leave empty for all):")
        organized_files.extend(
            organizer.organize_files(current_directory, filetype))
        update_tree(tree, current_directory)
        messagebox.showinfo("File Organizer", "File organization completed.")

    def on_restore():
        if organized_files:
            restore_files(organized_files)
            update_tree(tree, current_directory)
        else:
            messagebox.showwarning(
                "Restore Files", "No files to restore. Use 'Organize' first.")

    def on_stats():
        files, dirs, size = get_directory_stats(current_directory)
        messagebox.showinfo(
            "Directory Stats",
            f"Files: {files}, Directories: {dirs}, Total size: {size:,} bytes")

    def on_search():
        query = simpledialog.askstring("Search Files", "Enter search query:")
        if query:
            results = search_files(current_directory, query)
            if results:
                messagebox.showinfo("Search Results", "\n".join(results))
            else:
                messagebox.showinfo("Search Results",
                                    "No files found matching the query.")

    def on_blacklist():
        action = simpledialog.askstring("Blacklist Action",
                                        "Enter action (add/remove):")
        if action in ['add', 'remove']:
            items = simpledialog.askstring(
                "Blacklist Items",
                "Enter filenames, directories, or filetypes to blacklist (comma-separated):"
            )
            if items:
                handle_blacklist(action, items, config)
        else:
            messagebox.showwarning("Blacklist",
                                   "Invalid action. Use 'add' or 'remove'.")

    def reset_to_default():
        global config
        default_config = {
            "blacklisted_files": [],
            "blacklisted_directories": [],
            "blacklisted_filetypes": []
        }
        ConfigManager.save_config(default_config)
        config = default_config
        messagebox.showinfo("Reset",
                            "Configuration has been reset to default.")

    def on_show_blacklist():
        show_blacklist(config)

    def on_exit():
        root.quit()

    Button(button_frame, text="Open Directory",
           command=open_directory).pack(side='left', padx=5, pady=5)
    Button(button_frame, text="Organize Files",
           command=on_organize).pack(side='left', padx=5, pady=5)
    Button(button_frame, text="Restore Files",
           command=on_restore).pack(side='left', padx=5, pady=5)
    Button(button_frame, text="Stats", command=on_stats).pack(side='left',
                                                              padx=5,
                                                              pady=5)
    Button(button_frame, text="Search", command=on_search).pack(side='left',
                                                                padx=5,
                                                                pady=5)
    Button(button_frame, text="Blacklist",
           command=on_blacklist).pack(side='left', padx=5, pady=5)
    Button(button_frame, text="Show Blacklist",
           command=on_show_blacklist).pack(side='left', padx=5, pady=5)
    Button(button_frame, text="Reset to Default",
           command=reset_to_default).pack(side='left', padx=5, pady=5)

    Button(button_frame, text="Exit", command=on_exit).pack(side='right',
                                                            padx=5,
                                                            pady=5)

    frame = Frame(root)
    frame.pack(fill='both', expand=True)

    tree = Treeview(frame, columns=('Type', 'Size'), show='tree')
    tree.heading('#0', text='Name')
    tree.heading('Type', text='Type')
    tree.heading('Size', text='Size')
    tree.pack(side='left', fill='both', expand=True)

    scrollbar = Scrollbar(frame, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

    update_tree(tree, current_directory)

    root.mainloop()
