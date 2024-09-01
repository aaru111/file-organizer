# File Organizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)

A powerful and user-friendly file organization tool with both CLI and GUI interfaces.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [CLI Usage](#cli-usage)
  - [GUI Usage](#gui-usage)
- [Commands](#commands)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features

- Organize files based on their types
- Blacklist specific files, directories, or file types
- Restore organized files to their original locations
- Search for files within a directory
- View directory statistics
- User-friendly command-line interface
- Optional graphical user interface

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/file-organizer.git
   cd file-organizer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### CLI Usage

To start the File Organizer in CLI mode, run:

```
python main.py
```

### GUI Usage

To start the File Organizer in GUI mode, run:

```
python main.py
```

When prompted, choose "Yes" to use the GUI version.

## Commands

Here's a quick overview of available commands in CLI mode:

- `organize [directory] [file_type]`: Organize files in the specified directory
- `list`: List all files and directories in the current location
- `search <query>`: Search for files containing a specific query
- `cd <path>`: Change the current working directory
- `pwd`: Print the current working directory
- `restore`: Restore organized files to their original locations
- `blacklist add/remove <item>`: Modify the blacklist
- `show_blacklist`: Display the current blacklist
- `stats`: Show directory statistics
- `clear`: Clear the terminal screen
- `exit`: Exit the File Organizer
- `help [command]`: Display help information

For detailed information on each command, use `help <command>` in the CLI.

## Configuration

The File Organizer uses a configuration file located at `config/config.json`. This file stores the blacklist settings. You can manually edit this file or use the `blacklist` command to modify it.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

For any questions or issues, please open an issue on the GitHub repository.
