# 🗂️ File Organizer

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

> A versatile file organization tool with both CLI and GUI interfaces.

## ✨ Features

- 📁 Organize files based on their types
- 🚫 Blacklist specific files, directories, or file types
- 🔄 Restore organized files to their original locations
- 🔍 Search for files within a directory
- 📊 View directory statistics
- 💻 User-friendly command-line interface
- 🖥️ Optional graphical user interface

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/file-organizer.git
   cd file-organizer
   ```

2. Install the required dependencies:
   ```bash
   pip install rich prompt_toolkit
   ```

## 🎮 Usage

To start the File Organizer, run:
```bash
python main.py
```

You will be prompted to choose between the CLI and GUI versions.

### 🖥️ CLI Usage

The CLI provides an interactive prompt where you can enter commands.

### 🖱️ GUI Usage

The GUI provides buttons for common actions and a file tree view.

## 🛠️ Commands (CLI)

| Command | Description |
|---------|-------------|
| `organize [directory] [file_type]` | Organize files in the specified directory |
| `list` | List all files and directories in the current location |
| `search <query>` | Search for files containing a specific query |
| `cd <directory>` | Change the current working directory |
| `pwd` | Print the current working directory |
| `restore` | Restore organized files to their original locations |
| `blacklist add/remove <item>` | Modify the blacklist |
| `show_blacklist` | Display the current blacklist |
| `stats` | Show directory statistics |
| `clear` | Clear the terminal screen |
| `exit` | Exit the File Organizer |
| `help [command]` | Display help information |

## ⚙️ Configuration

The File Organizer uses a configuration file located at `config/config.json`. This file stores the blacklist settings. You can manually edit this file or use the `blacklist` command to modify it.

## 🐛 Error Handling

The application includes a robust error handling system that provides detailed error information and suggestions for fixing common issues.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

![Contributing](https://opensource.com/sites/default/files/styles/image-full-size/public/lead-images/github-universe.jpg?itok=lwRZddXA)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

For any questions or issues, please open an issue on the GitHub repository.

<p align="center">
  <a href="https://github.com/aaru111/file-organizer/issues">
    <img src="https://img.shields.io/github/issues/aaru111/file-organizer.svg" alt="GitHub issues">
  </a>
  <a href="https://github.com/aaru111/file-organizer/network">
    <img src="https://img.shields.io/github/forks/aaru111/file-organizer.svg" alt="GitHub forks">
  </a>
  <a href="https://github.com/aaru111/file-organizer/stargazers">
    <img src="https://img.shields.io/github/stars/aaru111/file-organizer.svg" alt="GitHub stars">
  </a>
</p>
