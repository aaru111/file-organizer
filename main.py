import os
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich import print
from rich.layout import Layout
from rich.align import Align
from rich.padding import Padding
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, PathCompleter
from help import get_help_table, show_command_help

console = Console()

def get_file_extension(file_path):
    return os.path.splitext(file_path)[1][1:].lower()

def create_folder(directory, folder_name):
    folder_path = os.path.join(directory, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def move_file(file_path, new_path):
    shutil.move(file_path, new_path)
    return file_path, new_path

def organize_files(directory, blacklist, specific_type=None):
    organized_files = []
    file_categories = {
        'Documents': ['txt', 'doc', 'docx', 'pdf', 'rtf', 'odt'],
        'Images': ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
        'Audio': ['mp3', 'wav', 'ogg', 'flac'],
        'Videos': ['mp4', 'avi', 'mkv', 'mov']
    }

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename in blacklist or any(bl in root for bl in blacklist if bl.endswith('/')):
                continue
            file_path = os.path.join(root, filename)

            if os.path.isfile(file_path):
                file_extension = get_file_extension(file_path)
                if specific_type and file_extension != specific_type:
                    continue
                category_folder = next((cat for cat, exts in file_categories.items() if file_extension in exts), 'Others')

                if category_folder == 'Documents':
                    category_folder = create_folder(directory, category_folder)
                    extension_folder = create_folder(category_folder, file_extension.upper())
                    new_path = os.path.join(extension_folder, filename)
                else:
                    category_folder = create_folder(directory, category_folder)
                    new_path = os.path.join(category_folder, filename)

                organized_files.append(move_file(file_path, new_path))

    return organized_files

def list_files(directory):
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

def search_files(directory, query):
    results = []
    for root, _, files in os.walk(directory):
        results.extend(os.path.join(root, file) for file in files if query.lower() in file.lower())
    return results

def restore_files(organized_files):
    for original_path, new_path in organized_files:
        if os.path.exists(new_path):
            shutil.move(new_path, original_path)
    console.print("[green]✓ Files restored to their original locations.[/green]")

def show_home_screen():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=1)
    )

    layout["header"].update(Panel(Align.center("[bold]File Organizer[/bold]"), style="cyan", border_style="bold", padding=(0, 1)))
    help_table = get_help_table()
    layout["body"].update(help_table)
    layout["footer"].update(Align.center("[dim italic]Type a command to begin or 'help <command>' for more information[/dim italic]"))

    console.print(layout)

def get_directory_stats(directory):
    total_files = total_dirs = total_size = 0
    for root, dirs, files in os.walk(directory):
        total_dirs += len(dirs)
        total_files += len(files)
        total_size += sum(os.path.getsize(os.path.join(root, name)) for name in files)
    return total_files, total_dirs, total_size

def main():
    current_directory = os.getcwd()
    organized_files = []
    blacklist = set()

    session = PromptSession()
    file_completer = PathCompleter(only_directories=False, expanduser=True)
    dir_completer = PathCompleter(only_directories=True, expanduser=True)

    def get_completer(command):
        if command in ['cd', 'organize']:
            return dir_completer
        elif command in ['blacklist']:
            return file_completer
        else:
            return WordCompleter(['organize', 'list', 'search', 'cd', 'pwd', 'restore', 'blacklist', 'show_blacklist', 'stats', 'exit', 'help'])

    console.clear()
    show_home_screen()

    user_input = ''  # Initialize user_input before the loop

    while True:
        try:
            user_input = session.prompt("\n[cyan]❯ [/cyan]", completer=get_completer(user_input.split()[0] if user_input else ''))
            command = user_input.split()

            if not command:
                continue

            if command[0] == 'organize':
                if len(command) == 3:
                    organized_files = organize_files(command[1], blacklist, command[2])
                elif len(command) == 2:
                    organized_files = organize_files(command[1], blacklist)
                else:
                    organized_files = organize_files(current_directory, blacklist)
                console.print("[green]✓ File organization completed.[/green]")
            elif command[0] == 'list':
                list_files(current_directory)
            elif command[0] == 'stats':
                files, dirs, size = get_directory_stats(current_directory)
                console.print(f"[green]Files: {files}, Directories: {dirs}, Total size: {size:,} bytes[/green]")
            elif command[0] == 'search' and len(command) > 1:
                results = search_files(current_directory, command[1])
                if results:
                    console.print(Panel(Align.left("\n".join(results)), title="Search Results", border_style="bold", expand=False))
                else:
                    console.print("[yellow]No files found matching the query.[/yellow]")
            elif command[0] == 'cd' and len(command) > 1:
                new_dir = os.path.abspath(os.path.join(current_directory, command[1]))
                if os.path.isdir(new_dir):
                    current_directory = new_dir
                    os.chdir(current_directory)
                    console.print(f"[green]✓ Changed directory to: {current_directory}[/green]")
                else:
                    console.print("[red]Invalid directory.[/red]")
            elif command[0] == 'pwd':
                console.print(f"[yellow]Current directory: {current_directory}[/yellow]")
            elif command[0] == 'restore':
                if organized_files:
                    restore_files(organized_files)
                    organized_files = []
                else:
                    console.print("[yellow]No files to restore. Use 'organize' first.[/yellow]")
            elif command[0] == 'blacklist':
                if len(command) < 3:
                    console.print("[red]Usage: blacklist [add/remove] [filename/directory][/red]")
                else:
                    action, item = command[1], command[2]
                    if action == 'add':
                        blacklist.add(item)
                        console.print(f"[green]✓ Added '{item}' to blacklist.[/green]")
                    elif action == 'remove':
                        if item in blacklist:
                            blacklist.remove(item)
                            console.print(f"[green]✓ Removed '{item}' from blacklist.[/green]")
                        else:
                            console.print(f"[yellow]'{item}' not found in blacklist.[/yellow]")
                    else:
                        console.print("[red]Invalid action. Use 'add' or 'remove'.[/red]")
            elif command[0] == 'show_blacklist':
                if blacklist:
                    console.print(Panel(", ".join(blacklist), title="Blacklisted Files/Directories", border_style="bold", expand=False))
                else:
                    console.print("[yellow]Blacklist is empty.[/yellow]")
            elif command[0] == 'exit':
                console.print("[cyan]Thank you for using the File Organizer. Goodbye![/cyan]")
                break
            elif command[0] == 'help':
                if len(command) > 1:
                    console.print(show_command_help(command[1]))
                else:
                    show_home_screen()
            else:
                console.print("[red]Invalid command. Type 'help' to see available commands.[/red]")

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()