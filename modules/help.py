from rich.table import Table
from rich.panel import Panel
from rich.align import Align

def get_help_table():
    help_text = {
        'organize': {
            'description': 'Organize files in the specified directory',
            'usage': 'organize [directory] [file_type]',
            'details': 'Sorts files into categorized folders based on their file types. Optionally specify a directory and/or file type.'
        },
        'list': {
            'description': 'List all files and directories in the current location',
            'usage': 'list',
            'details': 'Displays a table with names, types, and sizes of items in the current directory.'
        },
        'search': {
            'description': 'Search for files containing a specific query',
            'usage': 'search <query>',
            'details': 'Performs a case-insensitive search for files matching the given query in their names.'
        },
        'cd': {
            'description': 'Change the current working directory',
            'usage': 'cd <path>',
            'details': 'Navigates to the specified directory. Use ".." to move up one level.'
        },
        'pwd': {
            'description': 'Print the current working directory',
            'usage': 'pwd',
            'details': 'Displays the full path of the current working directory.'
        },
        'restore': {
            'description': 'Restore organized files to their original locations',
            'usage': 'restore',
            'details': 'Moves files back to their original locations after using the "organize" command.'
        },
        'blacklist': {
            'description': 'Modify the blacklist of files/directories to ignore during organization',
            'usage': 'blacklist add <filename/directory>\nblacklist remove <filename/directory>',
            'details': 'Add or remove filenames or directories from the blacklist. Blacklisted items are ignored during organization.'
        },
        'show_blacklist': {
            'description': 'Display the current blacklist',
            'usage': 'show_blacklist',
            'details': 'Shows a list of all files and directories currently in the blacklist.'
        },
        'stats': {
            'description': 'Show directory statistics',
            'usage': 'stats',
            'details': 'Displays the total number of files, directories, and the total size of the current directory.'
        },
        'exit': {
            'description': 'Exit the File Organizer',
            'usage': 'exit',
            'details': 'Closes the application.'
        },
        'help': {
            'description': 'Display this help information',
            'usage': 'help',
            'details': 'Shows a list of all available commands with their descriptions and usage.'
        }
    }

    help_table = Table(show_header=True, header_style="bold magenta", expand=True)
    help_table.add_column("Command", style="cyan", no_wrap=True)
    help_table.add_column("Description", style="green")
    help_table.add_column("Usage", style="yellow")
    help_table.add_column("Details", style="blue")

    for cmd, info in help_text.items():
        help_table.add_row(cmd, info['description'], info['usage'], info['details'])

    return Panel(Align.center(help_table), title="File Organizer - Command Reference", border_style="bold", padding=(1, 1), expand=False)

def show_command_help(command):
    help_text = {
        'organize': 'Organizes files in the specified directory into categorized folders based on their file types. You can optionally specify a directory and/or file type to organize.',
        'list': 'Displays a table showing all files and directories in the current location, including their names, types, and sizes.',
        'search': 'Performs a case-insensitive search for files containing the specified query in their names.',
        'cd': 'Changes the current working directory to the specified path. Use ".." to navigate up one level.',
        'pwd': 'Prints the full path of the current working directory.',
        'restore': 'Moves files back to their original locations after using the "organize" command.',
        'blacklist': 'Modifies the blacklist of files or directories to ignore during organization. Use "add" to add an item to the blacklist or "remove" to remove an item from the blacklist.',
        'show_blacklist': 'Displays a list of all files and directories currently in the blacklist.',
        'stats': 'Shows statistics for the current directory, including the total number of files, directories, and the total size.',
        'exit': 'Closes the File Organizer application.',
        'help': 'Displays help information for all available commands or for a specific command when followed by the command name.'
    }

    if command in help_text:
        return Panel(help_text[command], title=f"Help: {command}", border_style="bold", expand=False)
    else:
        return Panel(f"No help available for '{command}'. Type 'help' to see all available commands.", title="Command Not Found", border_style="bold", style="red", expand=False)