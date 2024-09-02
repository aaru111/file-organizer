import os
import json
import shutil
import asyncio
from abc import ABC, abstractmethod
from tkinter import Tk, filedialog, messagebox, simpledialog, Toplevel, Text, Scrollbar, RIGHT, Y, END, Button as TkButton
from tkinter.ttk import Frame, Button, Treeview, Style
from treelib import Tree
from pathlib import Path
from typing import List, Tuple, Dict

# PyPI module 'appdirs' for standard config file directories
from appdirs import user_config_dir


class ConfigManager:
    """Handles loading and saving of configuration files."""

    CONFIG_DIR = user_config_dir("FileOrganizer", "YourCompany")
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

    @classmethod
    def load_config(cls) -> Dict[str, List[str]]:
        """Loads the configuration file, creating a default one if it doesn't exist."""
        os.makedirs(cls.CONFIG_DIR, exist_ok=True)
        if not os.path.exists(cls.CONFIG_FILE):
            return cls._create_default_config()
        with open(cls.CONFIG_FILE, 'r') as f:
            return json.load(f)

    @classmethod
    def _create_default_config(cls) -> Dict[str, List[str]]:
        """Creates and saves a default configuration file."""
        default_config = {
            "blacklisted_files": [],
            "blacklisted_directories": [],
            "blacklisted_filetypes": []
        }
        cls.save_config(default_config)
        return default_config

    @classmethod
    def save_config(cls, config: Dict[str, List[str]]) -> None:
        """Saves the given configuration to the config file."""
        with open(cls.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)


class FileOrganizer(ABC):
    """Abstract base class for organizing files."""

    def __init__(self, config: Dict[str, List[str]]):
        self.config = config

    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """Returns the file extension of the given file path."""
        return Path(file_path).suffix[1:].lower()

    @staticmethod
    def create_folder(directory: str, folder_name: str) -> str:
        """Creates a folder with the given name in the specified directory."""
        folder_path = os.path.join(directory, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    @staticmethod
    def move_file(file_path: str, new_path: str) -> Tuple[str, str]:
        """Moves a file to a new path."""
        shutil.move(file_path, new_path)
        return file_path, new_path

    def is_blacklisted(self, file_path: str, filename: str) -> bool:
        """Checks if a file is blacklisted based on the configuration."""
        file_extension = self.get_file_extension(filename)
        is_blacklisted_file = filename in self.config['blacklisted_files']
        is_blacklisted_dir = any(
            os.path.commonpath([bl, file_path]) == bl
            for bl in self.config['blacklisted_directories'])
        is_blacklisted_type = file_extension in self.config[
            'blacklisted_filetypes']
        return is_blacklisted_file or is_blacklisted_dir or is_blacklisted_type

    @abstractmethod
    async def organize_files(
            self,
            directory: str,
            specific_type: str = None) -> List[Tuple[str, str]]:
        """Abstract method for organizing files."""
        pass


class AsyncFileOrganizer(FileOrganizer):
    """Asynchronous file organizer implementation."""

    async def organize_files(
            self,
            directory: str,
            specific_type: str = None) -> List[Tuple[str, str]]:
        """Organizes files asynchronously based on file types."""
        organized_files = []
        file_categories = self._file_categories()

        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                if self.is_blacklisted(file_path, filename):
                    continue

                if os.path.isfile(file_path):
                    file_extension = self.get_file_extension(file_path)
                    if specific_type and file_extension != specific_type:
                        continue
                    new_path = self._get_new_path(directory, filename,
                                                  file_extension,
                                                  file_categories)
                    organized_files.append(self.move_file(file_path, new_path))

        return organized_files

    @staticmethod
    def _file_categories() -> Dict[str, List[str]]:
        """Returns a dictionary mapping categories to file extensions."""
        return {
            'Documents': ['txt', 'doc', 'docx', 'pdf', 'rtf', 'odt'],
            'Images': ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
            'Audio': ['mp3', 'wav', 'ogg', 'flac'],
            'Videos': ['mp4', 'avi', 'mkv', 'mov']
        }

    def _get_new_path(self, directory: str, filename: str, file_extension: str,
                      file_categories: Dict[str, List[str]]) -> str:
        """Determines the new path for a file based on its extension."""
        category_folder = next((cat for cat, exts in file_categories.items()
                                if file_extension in exts), 'Others')
        category_folder_path = self.create_folder(directory, category_folder)

        if category_folder == 'Documents':
            extension_folder = self.create_folder(category_folder_path,
                                                  file_extension.upper())
            return os.path.join(extension_folder, filename)
        else:
            return os.path.join(category_folder_path, filename)


async def delete_empty_folders(path: str) -> None:
    """Recursively deletes empty folders."""
    if not os.path.isdir(path):
        return
    for subdir in os.listdir(path):
        full_path = os.path.join(path, subdir)
        if os.path.isdir(full_path):
            await delete_empty_folders(full_path)
    if not os.listdir(path):
        os.rmdir(path)


async def restore_files(organized_files: List[Tuple[str, str]]) -> None:
    """Restores files to their original locations."""
    for original_path, new_path in organized_files:
        if os.path.exists(new_path):
            shutil.move(new_path, original_path)
    await delete_empty_folders(current_directory)
    messagebox.showinfo("File Organizer",
                        "Files restored to their original locations.")


def update_tree(tree: Treeview, directory: str) -> None:
    """Updates the file tree display with the contents of the specified directory."""
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


class BlacklistHandler:
    """Handles the blacklisting of files, directories, and file types."""

    def __init__(self, config: Dict[str, List[str]]):
        self.config = config

    def handle_blacklist(self, action: str, items: str) -> None:
        """Handles adding or removing items from the blacklist."""
        items_list = [item.strip() for item in items.split(",")]
        for item in items_list:
            item_type = self._determine_item_type(item)
            blacklist_key = f'blacklisted_{item_type}'

            if action == 'add':
                self._add_to_blacklist(item, blacklist_key, item_type)
            elif action == 'remove':
                self._remove_from_blacklist(item, blacklist_key, item_type)

        ConfigManager.save_config(self.config)

    def _determine_item_type(self, item: str) -> str:
        """Determines if an item is a file, directory, or filetype."""
        return ('filetypes' if item.startswith('.') else
                'directories' if os.path.isdir(item) else 'files')

    def _add_to_blacklist(self, item: str, blacklist_key: str,
                          item_type: str) -> None:
        """Adds an item to the blacklist if not already present."""
        if item not in self.config[blacklist_key]:
            self.config[blacklist_key].append(item)
            messagebox.showinfo("Blacklist",
                                f"Added '{item}' to blacklisted {item_type}.")
        else:
            messagebox.showwarning(
                "Blacklist",
                f"'{item}' is already in blacklisted {item_type}.")

    def _remove_from_blacklist(self, item: str, blacklist_key: str,
                               item_type: str) -> None:
        """Removes an item from the blacklist if present."""
        if item in self.config[blacklist_key]:
            self.config[blacklist_key].remove(item)
            messagebox.showinfo(
                "Blacklist", f"Removed '{item}' from blacklisted {item_type}.")
        else:
            messagebox.showwarning(
                "Blacklist", f"'{item}' not found in blacklisted {item_type}.")

    def show_blacklist(self) -> None:
        """Displays the current blacklist."""
        blacklist_message = self._format_blacklist_message()
        messagebox.showinfo("Blacklist", blacklist_message)

    def _format_blacklist_message(self) -> str:
        """Formats the blacklist message to be displayed."""
        return "\n".join(f"Blacklisted {key.split('_')[1].capitalize()}: " +
                         ", ".join(self.config[key]) for key in [
                             'blacklisted_files', 'blacklisted_directories',
                             'blacklisted_filetypes'
                         ] if self.config[key]) or "All blacklists are empty."

    @classmethod
    def reset_to_default(cls) -> Dict[str, List[str]]:
        """Resets the configuration to its default state."""
        return ConfigManager._create_default_config()


def get_directory_stats(directory: str) -> Tuple[int, int, int]:
    """Returns the total number of files, directories, and size of a directory."""
    total_files = total_dirs = total_size = 0
    for root, dirs, files in os.walk(directory):
        total_dirs += len(dirs)
        total_files += len(files)
        total_size += sum(
            os.path.getsize(os.path.join(root, name)) for name in files)
    return total_files, total_dirs, total_size


def search_files(directory: str, query: str) -> List[str]:
    """Searches for files containing the query in their names."""
    return [
        os.path.join(root, file) for root, _, files in os.walk(directory)
        for file in files if query.lower() in file.lower()
    ]


def get_directory_structure(directory: str) -> Tree:
    """Generates a tree structure for the given directory."""
    tree = Tree()
    tree.create_node(os.path.basename(directory),
                     directory)  # Add the root node

    # Stack to keep track of nodes to add (ensures parent nodes exist first)
    stack = [(directory, directory)]

    while stack:
        parent, parent_id = stack.pop()

        for item in os.listdir(parent):
            item_path = os.path.join(parent, item)
            item_id = os.path.join(parent_id, item)

            if os.path.isdir(item_path):
                tree.create_node(item, item_id, parent=parent_id)
                stack.append((item_path, item_id))
            else:
                tree.create_node(item, item_id, parent=parent_id)

    return tree


def show_directory_structure(directory: str) -> None:
    """Displays the directory structure in a new window."""
    tree = get_directory_structure(directory)
    structure = tree.show(stdout=False)

    # Create a new top-level window for displaying and copying the structure
    struct_win = Toplevel()
    struct_win.title("Directory Structure")
    struct_win.geometry("600x400")

    text_box = Text(struct_win, wrap='none')
    text_box.insert(END, structure)
    text_box.config(state='disabled')

    scrollbar = Scrollbar(struct_win, command=text_box.yview)
    text_box.config(yscrollcommand=scrollbar.set)

    text_box.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    def copy_to_clipboard():
        struct_win.clipboard_clear()
        struct_win.clipboard_append(structure)
        struct_win.update(
        )  # now it stays on the clipboard after the window is closed
        messagebox.showinfo("Copied",
                            "Directory structure copied to clipboard!")

    TkButton(struct_win, text="Copy to Clipboard",
             command=copy_to_clipboard).pack(pady=10)


async def launch_gui() -> None:
    """Launches the GUI for the File Organizer application."""
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
    organizer = AsyncFileOrganizer(config)
    blacklist_handler = BlacklistHandler(config)

    def open_directory():
        """Opens a directory dialog for the user to select a directory."""
        global current_directory
        directory = filedialog.askdirectory(initialdir=current_directory)
        if directory:
            current_directory = directory
            update_tree(tree, current_directory)

    async def on_organize():
        """Organizes files based on user input for specific type."""
        filetype = simpledialog.askstring(
            "File Organizer",
            "Enter file type to organize (leave empty for all):")
        organized_files.extend(await organizer.organize_files(
            current_directory, filetype))
        update_tree(tree, current_directory)
        messagebox.showinfo("File Organizer", "File organization completed.")

    async def on_restore():
        """Restores files to their original locations if any have been organized."""
        if organized_files:
            await restore_files(organized_files)
            update_tree(tree, current_directory)
        else:
            messagebox.showwarning(
                "Restore Files", "No files to restore. Use 'Organize' first.")

    def on_stats():
        """Displays statistics about the current directory."""
        files, dirs, size = get_directory_stats(current_directory)
        messagebox.showinfo(
            "Directory Stats",
            f"Files: {files}, Directories: {dirs}, Total size: {size:,} bytes")

    def on_search():
        """Searches for files in the current directory based on a user query."""
        query = simpledialog.askstring("Search Files", "Enter search query:")
        if query:
            results = search_files(current_directory, query)
            if results:
                messagebox.showinfo("Search Results", "\n".join(results))
            else:
                messagebox.showinfo("Search Results",
                                    "No files found matching the query.")

    def on_blacklist():
        """Handles blacklist operations for adding or removing items."""
        action = simpledialog.askstring("Blacklist Action",
                                        "Enter action (add/remove):")
        if action in ['add', 'remove']:
            items = simpledialog.askstring(
                "Blacklist Items",
                "Enter filenames, directories, or filetypes to blacklist (comma-separated):"
            )
            if items:
                blacklist_handler.handle_blacklist(action, items)
        else:
            messagebox.showwarning("Blacklist",
                                   "Invalid action. Use 'add' or 'remove'.")

    def reset_to_default():
        """Resets the configuration to the default settings."""
        global config
        config = blacklist_handler.reset_to_default()
        messagebox.showinfo("Reset",
                            "Configuration has been reset to default.")

    def on_show_blacklist():
        """Displays the current blacklist."""
        blacklist_handler.show_blacklist()

    def on_show_structure():
        """Shows the directory structure of the current directory."""
        show_directory_structure(current_directory)

    def on_exit():
        """Exits the application."""
        root.quit()

    # GUI Buttons setup
    Button(button_frame, text="Open Directory",
           command=open_directory).pack(side='left', padx=5, pady=5)
    Button(button_frame,
           text="Organize Files",
           command=lambda: asyncio.create_task(on_organize())).pack(
               side='left', padx=5, pady=5)
    Button(button_frame,
           text="Restore Files",
           command=lambda: asyncio.create_task(on_restore())).pack(side='left',
                                                                   padx=5,
                                                                   pady=5)
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
    Button(button_frame, text="Show Structure",
           command=on_show_structure).pack(side='left', padx=5, pady=5)
    Button(button_frame, text="Reset to Default",
           command=reset_to_default).pack(side='left', padx=5, pady=5)
    Button(button_frame, text="Exit", command=on_exit).pack(side='right',
                                                            padx=5,
                                                            pady=5)

    frame = Frame(root)
    frame.pack(fill='both', expand=True)

    # Treeview setup for displaying directory contents
    tree = Treeview(frame, columns=('Type', 'Size'), show='tree')
    tree.heading('#0', text='Name')
    tree.heading('Type', text='Type')
    tree.heading('Size', text='Size')
    tree.pack(side='left', fill='both', expand=True)

    scrollbar = Scrollbar(frame, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    update_tree(tree, current_directory)
    root.mainloop()


if __name__ == "__main__":
    asyncio.run(launch_gui())
