# main.py

import os
import json
import shutil
import asyncio
from abc import ABC, abstractmethod
from tkinter import Tk, messagebox
from modules.gui import launch_gui
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.align import Align
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, PathCompleter
from prompt_toolkit.styles import Style
from modules.help import get_help_table, show_command_help
from modules.error_handler import error_handler

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
    async def organize_files(self, directory, specific_type=None):
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


class AsyncFileOrganizer(FileOrganizer):

    def __init__(self, config):
        super().__init__(config)

    async def organize_files(self, directory, specific_type=None):
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


async def list_files(directory):
    table = Table(show_header=True, header_style="bold magenta", expand=False)
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Size", justify="right", style="yellow")

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            table.add_row(item, "File", f"{size:,} bytes")
        elif os.path.isdir(item_path):
            table.add_row(item, "Directory", "")

    console.print(table)


async def search_files(directory, query):
    results = []
    for root, _, files in os.walk(directory):
        results.extend(
            os.path.join(root, file) for file in files
            if query.lower() in file.lower())
    return results


async def restore_files(organized_files):
    for original_path, new_path in organized_files:
        if os.path.exists(new_path):
            shutil.move(new_path, original_path)
    console.print(
        "[green]✓ Files restored to their original locations.[/green]")


async def show_home_screen():
    layout = Layout()
    layout.split_column(Layout(name="header", size=3), Layout(name="body"),
                        Layout(name="footer", size=1))

    layout["header"].update(
        Panel(Align.center("[bold]File Organizer[/bold]"),
              style="cyan",
              border_style="bold",
              padding=(0, 1)))
    help_table = get_help_table()
    layout["body"].update(help_table)
    layout["footer"].update(
        Align.center(
            "[dim italic]Type a command to begin or 'help <command>' for more information[/dim italic]"
        ))

    console.print(layout)


async def get_directory_stats(directory):
    total_files = total_dirs = total_size = 0
    for root, dirs, files in os.walk(directory):
        total_dirs += len(dirs)
        total_files += len(files)
        total_size += sum(
            os.path.getsize(os.path.join(root, name)) for name in files)
    return total_files, total_dirs, total_size


class BlacklistHandler:

    def __init__(self, config):
        self.config = config

    async def handle_blacklist(self, command):
        """
        Handles adding or removing items from the blacklist in batch.
        """
        if len(command) < 3:
            console.print(
                "[red]Usage: blacklist [add/remove] [filename, directory, or filetype (comma-separated)][/red]"
            )
            return

        action, items = command[1], command[2]
        items_list = items.split(
            ",")  # Allow multiple items separated by commas

        for item in items_list:
            item = item.strip()  # Remove any extra spaces
            item_type = ('filetypes' if item.startswith('.') else
                         'directories' if os.path.isdir(item) else 'files')
            blacklist_key = f'blacklisted_{item_type}'

            if action == 'add':
                if item not in self.config[blacklist_key]:
                    self.config[blacklist_key].append(item)
                    console.print(
                        f"[green]✓ Added '{item}' to blacklisted {item_type}.[/green]"
                    )
                else:
                    console.print(
                        f"[yellow]'{item}' is already in blacklisted {item_type}.[/yellow]"
                    )
            elif action == 'remove':
                if item in self.config[blacklist_key]:
                    self.config[blacklist_key].remove(item)
                    console.print(
                        f"[green]✓ Removed '{item}' from blacklisted {item_type}.[/green]"
                    )
                else:
                    console.print(
                        f"[yellow]'{item}' not found in blacklisted {item_type}.[/yellow]"
                    )
            else:
                console.print(
                    "[red]Invalid action. Use 'add' or 'remove'.[/red]")

        ConfigManager.save_config(
            self.config)  # Save the updated config after processing all items

    async def show_blacklist(self):
        if any(self.config[key] for key in [
                'blacklisted_files', 'blacklisted_directories',
                'blacklisted_filetypes'
        ]):
            for key in [
                    'blacklisted_files', 'blacklisted_directories',
                    'blacklisted_filetypes'
            ]:
                if self.config[key]:
                    console.print(
                        Panel(", ".join(self.config[key]),
                              title=
                              f"Blacklisted {key.split('_')[1].capitalize()}",
                              border_style="bold",
                              expand=False))
        else:
            console.print("[yellow]All blacklists are empty.[/yellow]")

    @staticmethod
    def reset_to_default():
        """
        Resets the configuration to its default state.
        """
        default_config = {
            "blacklisted_files": [],
            "blacklisted_directories": [],
            "blacklisted_filetypes": []
        }
        ConfigManager.save_config(default_config)
        console.print(
            "[green]Configuration has been reset to default.[/green]")


async def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


async def main():
    current_directory = os.getcwd()
    organized_files = []

    session = PromptSession()
    file_completer = PathCompleter(only_directories=False, expanduser=True)
    dir_completer = PathCompleter(only_directories=True, expanduser=True)

    available_commands = [
        'organize', 'list', 'search', 'cd', 'pwd', 'restore', 'blacklist',
        'show_blacklist', 'stats', 'exit', 'help', 'clear'
    ]
    error_handler.set_commands(available_commands)

    config = ConfigManager.load_config()
    organizer = AsyncFileOrganizer(config)
    blacklist_handler = BlacklistHandler(config)

    def get_completer(command):
        if command in ['cd', 'organize']:
            return dir_completer
        elif command in ['blacklist']:
            return file_completer
        else:
            return WordCompleter(available_commands)

    prompt_style = Style.from_dict({'prompt': 'cyan'})

    await clear_screen()
    await show_home_screen()

    while True:
        try:
            user_input = await session.prompt_async(
                "\n❯ ",  # Removed rich style and added plain text prompt
                style=prompt_style,  # Apply the defined style to the prompt
                completer=get_completer(
                    user_input.split()[0] if 'user_input' in locals() else ''))
            command = user_input.split()

            if not command:
                continue

            if command[0] == 'organize':
                if len(command) == 3:
                    organized_files = await organizer.organize_files(
                        command[1], command[2])
                elif len(command) == 2:
                    organized_files = await organizer.organize_files(command[1]
                                                                     )
                else:
                    organized_files = await organizer.organize_files(
                        current_directory)
                console.print("[green]✓ File organization completed.[/green]")
            elif command[0] == 'list':
                await list_files(current_directory)
            elif command[0] == 'stats':
                files, dirs, size = await get_directory_stats(current_directory
                                                              )
                console.print(
                    f"[green]Files: {files}, Directories: {dirs}, Total size: {size:,} bytes[/green]"
                )
            elif command[0] == 'search' and len(command) > 1:
                results = await search_files(current_directory, command[1])
                if results:
                    console.print(
                        Panel(Align.left("\n".join(results)),
                              title="Search Results",
                              border_style="bold",
                              expand=False))
                else:
                    console.print(
                        "[yellow]No files found matching the query.[/yellow]")
            elif command[0] == 'cd' and len(command) > 1:
                new_dir = os.path.abspath(
                    os.path.join(current_directory, command[1]))
                if os.path.isdir(new_dir):
                    current_directory = new_dir
                    os.chdir(current_directory)
                    console.print(
                        f"[green]✓ Changed directory to: {current_directory}[/green]"
                    )
                else:
                    console.print("[red]Invalid directory.[/red]")
            elif command[0] == 'pwd':
                console.print(
                    f"[yellow]Current directory: {current_directory}[/yellow]")
            elif command[0] == 'restore':
                if organized_files:
                    await restore_files(organized_files)
                    organized_files = []
                else:
                    console.print(
                        "[yellow]No files to restore. Use 'organize' first.[/yellow]"
                    )
            elif command[0] == 'blacklist':
                await blacklist_handler.handle_blacklist(command)

            elif command[0] == 'reset':
                BlacklistHandler.reset_to_default()

            elif command[0] == 'show_blacklist':
                await blacklist_handler.show_blacklist()
            elif command[0] == 'clear':
                await clear_screen()
            elif command[0] == 'exit':
                console.print(
                    "[cyan]Thank you for using the File Organizer. Goodbye![/cyan]"
                )
                break
            elif command[0] == 'help':
                if len(command) > 1:
                    console.print(show_command_help(command[1]))
                else:
                    await show_home_screen()
            else:
                raise ValueError(f"Invalid command: {command[0]}")

        except KeyboardInterrupt:
            console.print(
                "\n[yellow]Operation cancelled by user. Type 'exit' to quit.[/yellow]"
            )
            continue
        except EOFError:
            console.print("\n[cyan]Exiting File Organizer. Goodbye![/cyan]")
            break
        except Exception as e:
            error_handler.handle_error(e, context=f"Command: {user_input}")


if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    response = messagebox.askyesno("File Organizer",
                                   "Do you want to use the GUI version?")
    root.destroy()

    if response:
        try:
            launch_gui()
        except Exception as e:
            error_handler.handle_error(e, context="Launching GUI")
    else:
        try:
            asyncio.run(main())
        except Exception as e:
            error_handler.handle_error(e, context="Main program execution")
