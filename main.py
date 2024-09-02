import os
import json
import shutil
import asyncio
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTreeWidget, QTreeWidgetItem, QFileDialog, QMessageBox, QInputDialog,
    QGridLayout, QSplitter, QLineEdit, QLabel, QListWidget, QGroupBox,
    QFormLayout, QTabWidget, QHBoxLayout, QComboBox, QDialog, QPlainTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QTextCursor
from PyQt5.QtGui import QPixmap



class ConfigManager:
    CONFIG_DIR = "config"
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, List[str]]:
        if not os.path.exists(self.CONFIG_DIR):
            os.makedirs(self.CONFIG_DIR)
        if not os.path.exists(self.CONFIG_FILE):
            default_config = {
                "blacklisted_files": [],
                "blacklisted_directories": [],
                "blacklisted_filetypes": [],
                "file_categories": {
                    'Documents': ['txt', 'doc', 'docx', 'pdf', 'rtf', 'odt'],
                    'Images': ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
                    'Audio': ['mp3', 'wav', 'ogg', 'flac'],
                    'Videos': ['mp4', 'avi', 'mkv', 'mov'],
                    'Python': ['py'],
                    'JavaScript': ['js'],
                    'HTML': ['html', 'htm']
                }
            }
            self.save_config(default_config)
            return default_config
        with open(self.CONFIG_FILE, 'r') as f:
            return json.load(f)

    def save_config(self, config: Optional[Dict[str, List[str]]] = None) -> None:
        config = config if config else self.config
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)


class FileOrganizer(ABC):
    def __init__(self, config: Dict[str, List[str]]):
        self._config = config

    @staticmethod
    def get_file_extension(file_path: str) -> str:
        return os.path.splitext(file_path)[1][1:].lower()

    @staticmethod
    def create_folder(directory: str, folder_name: str) -> str:
        folder_path = os.path.join(directory, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    @staticmethod
    def move_file(file_path: str, new_path: str) -> Tuple[str, str]:
        shutil.move(file_path, new_path)
        return file_path, new_path

    def is_blacklisted(self, file_path: str, filename: str) -> bool:
        file_extension = self.get_file_extension(filename)
        is_blacklisted_file = filename in self._config['blacklisted_files']
        is_blacklisted_dir = any(
            os.path.commonpath([bl, file_path]) == bl
            for bl in self._config['blacklisted_directories']
        )
        is_blacklisted_type = file_extension in self._config['blacklisted_filetypes']
        return is_blacklisted_file or is_blacklisted_dir or is_blacklisted_type

    @abstractmethod
    async def organize_files(self, directory: str, specific_type: Optional[str] = None) -> List[Tuple[str, str]]:
        pass


class SyncFileOrganizer(FileOrganizer):
    async def organize_files(self, directory: str, specific_type: Optional[str] = None) -> List[Tuple[str, str]]:
        organized_files = []
        file_categories = self._config.get("file_categories", {})

        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                if self.is_blacklisted(file_path, filename):
                    continue

                file_extension = self.get_file_extension(file_path)
                if specific_type and file_extension != specific_type:
                    continue

                category_folder = next(
                    (cat for cat, exts in file_categories.items() if file_extension in exts), 'Others'
                )

                base_folder = self.create_folder(directory, category_folder)
                new_path = os.path.join(base_folder, filename)
                if category_folder in file_categories and file_extension in file_categories[category_folder]:
                    extension_folder = self.create_folder(base_folder, file_extension.upper())
                    new_path = os.path.join(extension_folder, filename)

                organized_files.append(self.move_file(file_path, new_path))

        return organized_files


async def delete_empty_folders(path: str) -> None:
    if not os.path.isdir(path):
        return
    for subdir in os.listdir(path):
        full_path = os.path.join(path, subdir)
        if os.path.isdir(full_path):
            await delete_empty_folders(full_path)
    if not os.listdir(path):
        os.rmdir(path)


async def restore_files(organized_files: List[Tuple[str, str]], current_directory: str) -> None:
    for original_path, new_path in organized_files:
        if os.path.exists(new_path):
            shutil.move(new_path, original_path)
    await delete_empty_folders(current_directory)
    QMessageBox.information(None, "File Organizer", "Files restored to their original locations.")


def update_tree(tree: QTreeWidget, directory: str) -> None:
    tree.clear()
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        size = os.path.getsize(item_path) if os.path.isfile(item_path) else ""
        item_type = "File" if os.path.isfile(item_path) else "Directory"
        item_widget = QTreeWidgetItem(tree, [item, item_type, f"{size} bytes"])
        item_widget.setData(0, Qt.ItemDataRole.UserRole, item_path)


class BlacklistHandler:
    def __init__(self, config: Dict[str, List[str]], config_manager: ConfigManager):
        self._config = config
        self.config_manager = config_manager

    def handle_blacklist(self, action: str, items: str) -> None:
        items_list = [item.strip() for item in items.split(",")]
        for item in items_list:
            item_type = (
                'filetypes' if item.startswith('.') else
                'directories' if os.path.isdir(item) else 'files'
            )
            blacklist_key = f'blacklisted_{item_type}'

            if action == 'add':
                if item not in self._config[blacklist_key]:
                    self._config[blacklist_key].append(item)
                    QMessageBox.information(None, "Blacklist", f"Added '{item}' to blacklisted {item_type}.")
                else:
                    QMessageBox.warning(None, "Blacklist", f"'{item}' is already in blacklisted {item_type}.")
            elif action == 'remove':
                if item in self._config[blacklist_key]:
                    self._config[blacklist_key].remove(item)
                    QMessageBox.information(None, "Blacklist", f"Removed '{item}' from blacklisted {item_type}.")
                else:
                    QMessageBox.warning(None, "Blacklist", f"'{item}' not found in blacklisted {item_type}.")
        self.config_manager.save_config()

    def show_blacklist(self) -> None:
        blacklist_message = ""
        for key in ['blacklisted_files', 'blacklisted_directories', 'blacklisted_filetypes']:
            if self._config[key]:
                blacklist_message += f"Blacklisted {key.split('_')[1].capitalize()}: " + ", ".join(self._config[key]) + "\n"
        if not blacklist_message:
            blacklist_message = "All blacklists are empty."
        QMessageBox.information(None, "Blacklist", blacklist_message)

    def reset_to_default(self) -> None:
        self._config = ConfigManager().config
        self.config_manager.save_config(self._config)


def get_directory_stats(directory: str) -> Tuple[int, int, int]:
    total_files, total_dirs, total_size = 0, 0, 0
    for root, dirs, files in os.walk(directory):
        total_dirs += len(dirs)
        total_files += len(files)
        total_size += sum(os.path.getsize(os.path.join(root, name)) for name in files)
    return total_files, total_dirs, total_size


def search_files(directory: str, query: str) -> List[str]:
    return [
        os.path.join(root, file)
        for root, _, files in os.walk(directory)
        for file in files if query.lower() in file.lower()
    ]


class SettingsPanel(QWidget):
    def __init__(self, config: Dict[str, List[str]], config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config
        self.config_manager = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # File Categories Section
        categories_group = QGroupBox("File Categories")
        categories_layout = QVBoxLayout()
        self.categories_list = QListWidget()
        self.categories_list.addItems(self.config.get('file_categories', {}).keys())
        categories_layout.addWidget(self.categories_list)

        category_form = QFormLayout()
        self.category_name_input = QLineEdit()
        self.category_ext_input = QLineEdit()
        category_form.addRow(QLabel("Category Name:"), self.category_name_input)
        category_form.addRow(QLabel("Extensions (comma-separated):"), self.category_ext_input)

        categories_layout.addLayout(category_form)
        self.add_category_button = QPushButton("Add/Update Category")
        self.add_category_button.clicked.connect(self.add_update_category)
        self.rename_folder_button = QPushButton("Rename Folder")
        self.rename_folder_button.clicked.connect(self.rename_folder)
        categories_layout.addWidget(self.add_category_button)
        categories_layout.addWidget(self.rename_folder_button)

        categories_group.setLayout(categories_layout)
        layout.addWidget(categories_group)

    def add_update_category(self):
        category_name = self.category_name_input.text().strip()
        extensions = [ext.strip() for ext in self.category_ext_input.text().split(',') if ext.strip()]

        if category_name and extensions:
            existing_extensions = {ext for exts in self.config['file_categories'].values() for ext in exts}
            duplicate_extensions = [ext for ext in extensions if ext in existing_extensions]

            if duplicate_extensions:
                QMessageBox.warning(self, "Settings", f"Extensions already exist: {', '.join(duplicate_extensions)}.")
                return

            self.config['file_categories'][category_name] = extensions
            self.config_manager.save_config(self.config)
            self.categories_list.clear()
            self.categories_list.addItems(self.config['file_categories'].keys())
            QMessageBox.information(self, "Settings", f"Category '{category_name}' updated with extensions: {', '.join(extensions)}.")
        else:
            QMessageBox.warning(self, "Settings", "Both category name and extensions are required.")

    def rename_folder(self):
        selected_category = self.categories_list.currentItem()
        if selected_category:
            current_name = selected_category.text()
            new_name, ok = QInputDialog.getText(self, "Rename Folder", f"Enter new name for '{current_name}':")
            if ok and new_name:
                if new_name in self.config['file_categories']:
                    QMessageBox.warning(self, "Rename Folder", "A folder with this name already exists.")
                else:
                    self.config['file_categories'][new_name] = self.config['file_categories'].pop(current_name)
                    self.config_manager.save_config(self.config)
                    self.categories_list.clear()
                    self.categories_list.addItems(self.config['file_categories'].keys())
                    QMessageBox.information(self, "Rename Folder", f"Folder renamed to '{new_name}'.")


class FileContentDialog(QDialog):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Contents of {os.path.basename(path)}")
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.load_content(path)

    def load_content(self, path):
        if os.path.isdir(path):
            contents = "\n".join(os.listdir(path))
        else:
            with open(path, 'r', errors='ignore') as f:
                contents = f.read()
        self.text_edit.setPlainText(contents)
        
class BuyCoffeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buy Me A Coffee")
        self.resize(400, 400) 

   
        layout = QVBoxLayout(self)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
 
        coffee_image_path = "coffee_image.webp" 
        self.image_label.setPixmap(QPixmap(coffee_image_path).scaledToWidth(350, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(self.image_label)


class FileOrganizerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_directory = os.getcwd()
        self.organized_files = []

        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        self.organizer = SyncFileOrganizer(self.config)
        self.blacklist_handler = BlacklistHandler(self.config, self.config_manager)

        self.init_ui()
        update_tree(self.tree, self.current_directory)

    def init_ui(self):
        self.setWindowTitle("File Organizer GUI")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setWindowIcon(QIcon('icon.png'))  # Add a custom icon if available

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Main layout with splitter
        self.main_layout = QHBoxLayout(self.central_widget)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Tree and Actions Panel
        self.tree_and_actions = QWidget()
        self.tree_and_actions_layout = QVBoxLayout(self.tree_and_actions)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type", "Size"])
        self.tree.setColumnWidth(0, 250)  # Adjust the first column width
        self.tree.itemDoubleClicked.connect(self.view_item_content)
        self.tree_and_actions_layout.addWidget(self.tree)

        self.add_buttons_panel()
        self.splitter.addWidget(self.tree_and_actions)

        # Settings Panel with retractable feature
        self.settings_panel = SettingsPanel(self.config, self.config_manager)
        self.settings_widget = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_widget)
        self.settings_toggle_button = QPushButton("Toggle Settings Panel")
        self.settings_toggle_button.clicked.connect(self.toggle_settings_panel)
        self.settings_layout.addWidget(self.settings_toggle_button)
        self.settings_layout.addWidget(self.settings_panel)
        self.splitter.addWidget(self.settings_widget)
        

        # Set initial sizes for splitter panels
        self.splitter.setSizes([900, 300])
        self.main_layout.addWidget(self.splitter)

    def add_buttons_panel(self):
        self.buttons_widget = QWidget()
        self.buttons_layout = QGridLayout(self.buttons_widget)
        self.add_button("Buy Me A Coffee", self.buttons_layout, 0, 0, self.on_buy_me_a_coffee, colspan=2)
        self.add_button("Open Directory", self.buttons_layout, 1, 0, lambda: asyncio.run(self.open_directory()))
        self.add_button("Organize Files", self.buttons_layout, 1, 1, lambda: asyncio.run(self.on_organize()))
        self.add_button("Restore Files", self.buttons_layout, 2, 0, lambda: asyncio.run(self.on_restore()))
        self.add_button("Stats", self.buttons_layout, 2, 1, self.on_stats)
        self.add_button("Search", self.buttons_layout, 3, 0, self.on_search)
        self.add_button("Blacklist", self.buttons_layout, 3, 1, self.on_blacklist)
        self.add_button("Show Blacklist", self.buttons_layout, 4, 0, self.on_show_blacklist)
        self.add_button("Reset to Default", self.buttons_layout, 4, 1, self.reset_to_default)
        self.add_button("Exit", self.buttons_layout, 5, 0, self.close, colspan=2)
    
        self.tree_and_actions_layout.addWidget(self.buttons_widget)


    def on_buy_me_a_coffee(self) -> None:
        QMessageBox.information(self, "Buy Me A Coffee", "UPI ID: aarav-000@fam")
    
        coffee_dialog = BuyCoffeeDialog(self)
        coffee_dialog.exec()


    def add_button(self, text, layout, row, col, callback, colspan=1):
        button = QPushButton(text)
        layout.addWidget(button, row, col, 1, colspan)
        button.clicked.connect(callback)

    def toggle_settings_panel(self):
        if self.settings_panel.isVisible():
            self.settings_panel.hide()
        else:
            self.settings_panel.show()

    async def open_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", self.current_directory)
        if directory:
            self.current_directory = directory
            update_tree(self.tree, self.current_directory)

    async def on_organize(self) -> None:
        filetype, ok = QInputDialog.getText(self, "File Organizer", "Enter file type to organize (leave empty for all):")
        if ok:
            self.organized_files.extend(await self.organizer.organize_files(self.current_directory, filetype))
            update_tree(self.tree, self.current_directory)
            QMessageBox.information(self, "File Organizer", "File organization completed.")

    async def on_restore(self) -> None:
        if self.organized_files:
            await restore_files(self.organized_files, self.current_directory)
            update_tree(self.tree, self.current_directory)
        else:
            QMessageBox.warning(self, "Restore Files", "No files to restore. Use 'Organize' first.")

    def on_stats(self) -> None:
        files, dirs, size = get_directory_stats(self.current_directory)
        QMessageBox.information(self, "Directory Stats", f"Files: {files}, Directories: {dirs}, Total size: {size:,} bytes")

    def on_search(self) -> None:
        query, ok = QInputDialog.getText(self, "Search Files", "Enter search query:")
        if ok:
            results = search_files(self.current_directory, query)
            if results:
                QMessageBox.information(self, "Search Results", "\n".join(results))
            else:
                QMessageBox.information(self, "Search Results", "No files found matching the query.")

    def on_blacklist(self) -> None:
        action, ok = QInputDialog.getText(self, "Blacklist Action", "Enter action (add/remove):")
        if ok and action in ['add', 'remove']:
            items, ok_items = QInputDialog.getText(self, "Blacklist Items", "Enter filenames, directories, or filetypes to blacklist (comma-separated):")
            if ok_items:
                self.blacklist_handler.handle_blacklist(action, items)
        else:
            QMessageBox.warning(self, "Blacklist", "Invalid action. Use 'add' or 'remove'.")

    def reset_to_default(self) -> None:
        self.blacklist_handler.reset_to_default()
        self.config['file_categories'] = {
            'Documents': ['txt', 'doc', 'docx', 'pdf', 'rtf', 'odt'],
            'Images': ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
            'Audio': ['mp3', 'wav', 'ogg', 'flac'],
            'Videos': ['mp4', 'avi', 'mkv', 'mov'],
            'Python': ['py']
        }
        self.config_manager.save_config(self.config)
        QMessageBox.information(self, "Reset", "Configuration has been reset to default.")
        self.settings_panel.categories_list.clear()
        self.settings_panel.categories_list.addItems(self.config['file_categories'].keys())

    def on_show_blacklist(self) -> None:
        self.blacklist_handler.show_blacklist()

    def view_item_content(self, item: QTreeWidgetItem, column: int):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            dialog = FileContentDialog(path, self)
            dialog.exec()


def main():
    app = QApplication([])
    gui = FileOrganizerGUI()
    gui.show()
    app.exec()


if __name__ == "__main__":
    main()
