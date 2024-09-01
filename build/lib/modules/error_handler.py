import sys
import traceback
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from difflib import get_close_matches

console = Console()

class ErrorHandler:
    def __init__(self):
        self.error_count = {}
        self.commands = set()  # Store available commands

    def set_commands(self, commands):
        """Set the available commands for the application."""
        self.commands = set(commands)

    def handle_error(self, error, context=None):
        error_type = type(error).__name__
        error_message = str(error)

        # Increment error count
        self.error_count[error_type] = self.error_count.get(error_type, 0) + 1

        # Get traceback information
        tb = traceback.extract_tb(sys.exc_info()[2])
        file_name, line_number, func_name, text = tb[-1]

        # Create error details table
        error_details = Table(show_header=False, box=None)
        error_details.add_row("Error Type:", f"[bold red]{error_type}[/bold red]")
        error_details.add_row("Error Message:", f"[yellow]{error_message}[/yellow]")
        error_details.add_row("File:", file_name)
        error_details.add_row("Line:", str(line_number))
        error_details.add_row("Function:", func_name)

        if context:
            error_details.add_row("Context:", context)

        # Create code snippet
        if text:
            code_snippet = Syntax(text, "python", theme="monokai", line_numbers=True, start_line=max(1, line_number - 2))
        else:
            code_snippet = "[dim]No code snippet available[/dim]"

        # Determine panel color and title based on error type
        title, border_style, message = self._get_error_display_info(error_type, error_message)

        # Create and print the error panel
        error_panel = Panel(
            f"{message}\n\n{error_details}\n\n{code_snippet}",
            title=f"{title} (Occurrence: {self.error_count[error_type]})",
            border_style=border_style,
            expand=False
        )
        console.print(error_panel)

        # Provide helpful suggestions
        self._provide_suggestions(error_type, error_message, context)

    def _get_error_display_info(self, error_type, error_message):
        if error_type == "IndexError" and "list index out of range" in error_message:
            return "Input Error", "yellow", "[yellow]No command entered. Please type a command or 'help' for assistance.[/yellow]"
        elif error_type == "FileNotFoundError":
            return "File Error", "red", "[red]The specified file or directory was not found.[/red]"
        elif error_type == "PermissionError":
            return "Permission Error", "red", "[red]You don't have permission to access this file or directory.[/red]"
        else:
            return "Unexpected Error", "red", f"[red]An unexpected error occurred:[/red]"

    def _provide_suggestions(self, error_type, error_message, context):
        suggestions = {
            "IndexError": [
                "Make sure you're not trying to access an index that doesn't exist in a list.",
                "Check if the list is empty before trying to access its elements.",
                "Verify that you're using the correct indexing (remember, Python uses 0-based indexing)."
            ],
            "FileNotFoundError": [
                "Double-check the file path and make sure it's correct.",
                "Verify that the file exists in the specified location.",
                "Ensure you have the necessary permissions to access the file."
            ],
            "PermissionError": [
                "Check if you have the required permissions to access the file or directory.",
                "Try running the program with elevated privileges (but be cautious when doing so).",
                "Verify the file or directory ownership and permissions."
            ],
            "KeyError": [
                "Make sure the key you're trying to access exists in the dictionary.",
                "Use the .get() method with a default value to avoid KeyErrors.",
                "Check for typos in the key name."
            ],
            "ValueError": [
                "Ensure that the input values are of the correct type and format.",
                "Add input validation to check for valid values before processing.",
                "Use try-except blocks to handle potential value errors gracefully."
            ],
            "TypeError": [
                "Check that you're using the correct data types for your operations.",
                "Verify that all required arguments are provided to functions.",
                "Ensure that you're not mixing incompatible types in operations."
            ]
        }

        if error_type in suggestions:
            console.print("\n[bold cyan]Suggestions to fix this error:[/bold cyan]")
            for suggestion in suggestions[error_type]:
                console.print(f"• [green]{suggestion}[/green]")
        else:
            console.print("\n[bold cyan]General troubleshooting steps:[/bold cyan]")
            console.print("• [green]Review the error message and traceback carefully.[/green]")
            console.print("• [green]Check the documentation for the functions or methods involved.[/green]")
            console.print("• [green]Use print statements or a debugger to inspect variable values.[/green]")

        # Check for possible command typos
        if context and context.startswith("Command:"):
            possible_command = context.split(":")[1].strip().split()[0]
            self._suggest_command(possible_command)

        console.print("\n[dim]Type 'help' for assistance or 'exit' to quit the program.[/dim]")

    def _suggest_command(self, possible_command):
        close_matches = get_close_matches(possible_command, self.commands, n=1, cutoff=0.6)
        if close_matches:
            console.print(f"\n[bold yellow]Did you mean '[green]{close_matches[0]}[/green]'?[/bold yellow]")
            console.print(f"[dim]If so, please try running the command again with the correct spelling.[/dim]")

error_handler = ErrorHandler()