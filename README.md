```markdown
# 🗂️ File Organizer

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

> A versatile file organization tool with a user-friendly graphical interface.

## ✨ Features

- 📁 **Organize Files**: Automatically categorize files based on their types into predefined folders.
- 🚫 **Blacklist Management**: Add or remove files, directories, or file types from the blacklist to exclude them from organization.
- 🔄 **File Restoration**: Restore files to their original locations after organization.
- 🔍 **File Search**: Search for files within the selected directory.
- 📊 **Directory Statistics**: View statistics about the number of files, directories, and total size of the selected directory.
- 💻 **Graphical User Interface (GUI)**: Intuitive interface for easy interaction with the file organizer.

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/file-organizer.git
   cd file-organizer
   ```

2. Install the required dependencies:
   ```bash
   pip install PyQt6
   ```

## 🎮 Usage

To start the File Organizer GUI, run:
```bash
python main.py
```

You will see a graphical interface with the following components:

### 🖥️ Main Window

- **File Tree View**: Displays the files and directories in the selected directory.
- **Buttons Panel**: Includes buttons for various actions such as opening a directory, organizing files, restoring files, viewing statistics, and more.
- **Settings Panel**: Allows you to manage file categories and rename folders.

### 🔧 Functionality

- **Open Directory**: Choose a directory to view and organize.
- **Organize Files**: Sort files based on their types and predefined categories.
- **Restore Files**: Move organized files back to their original locations.
- **View Stats**: Display statistics about the current directory.
- **Search Files**: Find files based on a search query.
- **Blacklist Management**: Add or remove items from the blacklist and view the current blacklist.
- **Reset to Default**: Reset configurations and file categories to default settings.

## ⚙️ Configuration

The application uses a configuration file located at `config/config.json`. This file contains:

- **Blacklisted Files**: Files that are excluded from the organization process.
- **Blacklisted Directories**: Directories that are excluded from the organization process.
- **Blacklisted Filetypes**: File types that are excluded from the organization process.
- **File Categories**: Categories and their associated file extensions.

You can modify this file manually or use the settings panel within the GUI to update categories.

## 🐛 Error Handling

The application provides detailed error messages and suggestions for fixing common issues. If something goes wrong, check the error messages for guidance.

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
```
