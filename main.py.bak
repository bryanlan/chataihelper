import sys
import os
import shutil
import pyperclip
import tiktoken
import re
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFileDialog, QListWidget, 
                             QListWidgetItem, QSplitter, QMessageBox)
from PyQt5.QtCore import Qt

####################################
# Token Counting with tiktoken
####################################
def count_tokens_openai(text, model_name="gpt-4"):
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))

####################################
# File Selection Widget
####################################
class FileSelectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.project_path_label = QLabel("Project Folder: None")
        self.choose_folder_btn = QPushButton("Choose Project Folder")
        self.choose_folder_btn.clicked.connect(self.choose_project_folder)
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.MultiSelection)
        self.file_list.itemSelectionChanged.connect(self.update_token_count)
        
        self.token_count_label = QLabel("Token Count: 0")
        
        layout.addWidget(self.project_path_label)
        layout.addWidget(self.choose_folder_btn)
        layout.addWidget(self.file_list)
        layout.addWidget(self.token_count_label)
        
        self.setLayout(layout)
        self.project_path = None
        self.all_files = []

    def choose_project_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.project_path = folder
            self.project_path_label.setText("Project Folder: " + folder)
            self.populate_file_list()

    def populate_file_list(self):
        self.file_list.clear()
        self.all_files = []
        if self.project_path:
            for root, dirs, files in os.walk(self.project_path):
                for f in files:
                    if f.startswith('.'):
                        pass
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, self.project_path)
                    item = QListWidgetItem(rel_path)
                    self.file_list.addItem(item)
                    self.all_files.append((rel_path, full_path))
    
    def get_selected_files(self):
        selected_items = self.file_list.selectedItems()
        selected_paths = []
        for i in selected_items:
            rel_path = i.text()
            for ap in self.all_files:
                if ap[0] == rel_path:
                    selected_paths.append(ap)
                    break
        return selected_paths
    
    def update_token_count(self):
        selected_files = self.get_selected_files()
        total_tokens = 0
        for _, fpath in selected_files:
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    total_tokens += count_tokens_openai(content, model_name="gpt-4")
            except:
                pass
        self.token_count_label.setText("Token Count: {}".format(total_tokens))

####################################
# Instructions Widget
####################################
class InstructionsWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        # Now the user only sees a single text box with the system-level instructions.
        # These instructions can be edited by the user if they wish, but the format instructions
        # will be appended automatically and remain hidden from the user.
        self.default_system_instructions = (
            "You are an expert software engineer. You are tasked with following my instructions. I will give you instructions for what code changes to make, followed by how to format your answer, and then the project files and their contents."
        )
        
        self.system_edit = QTextEdit()
        self.system_edit.setPlaceholderText("System prompt instructions...")
        self.system_edit.setText(self.default_system_instructions)
        
        layout.addWidget(QLabel("System Prompt Instructions (User Editable):"))
        layout.addWidget(self.system_edit)
        
        self.setLayout(layout)
    
    def get_system_instructions(self):
        return self.system_edit.toPlainText()

####################################
# Prompt Creation and Results Widget
####################################
class PromptCreationWidget(QWidget):
    def __init__(self, file_selection_widget, instructions_widget):
        super().__init__()
        
        self.file_selection_widget = file_selection_widget
        self.instructions_widget = instructions_widget
        
        layout = QVBoxLayout()
        
        self.custom_commands_edit = QTextEdit()
        self.custom_commands_edit.setPlaceholderText("Enter custom (per-run) commands or instructions here...")
        
        create_prompt_btn = QPushButton("Create Prompt")
        create_prompt_btn.clicked.connect(self.create_prompt)
        
        self.results_edit = QTextEdit()
        self.results_edit.setPlaceholderText("Paste LLM's response here (SUMMARY + CHANGES format)...")
        
        apply_btn = QPushButton("Apply Results")
        apply_btn.clicked.connect(self.apply_results)
        
        layout.addWidget(QLabel("Custom Commands (Per-Run)"))
        layout.addWidget(self.custom_commands_edit)
        layout.addWidget(create_prompt_btn)
        layout.addWidget(QLabel("LLM Results (Paste here):"))
        layout.addWidget(self.results_edit)
        layout.addWidget(apply_btn)
        
        self.setLayout(layout)

    def create_prompt(self):
        # Get user-edited system instructions
        system_instructions = self.instructions_widget.get_system_instructions()
        custom_commands = self.custom_commands_edit.toPlainText()

        # Hardcoded hidden instructions that we append to ensure the format
        # and summarize instructions are known to the model
        hidden_instructions = (
            "\n\n"
            "You must produce:\n"
            "1) A SUMMARY section in Markdown.\n"
            "   - Provide a brief overall summary.\n"
            "   - Provide a short summary for each file changed and explain why.\n"
            "   - Provide a short summary for each file deleted and explain why.\n"
            "   - This entire summary section should be formatted using Markdown.\n\n"
            "2) A CHANGES section following the exact format below:\n\n"
            "SUMMARY:\n"
            "<Your markdown summary>\n"
            "CHANGES:\n"
            "For each file changed:\n"
            "FILE: <relative/path/to/file>\n"
            "FILENAME: <filename>\n"
            "OPERATION: <CREATE|MODIFY|REMOVE>\n"
            "FULL_CONTENT:\n"
            "<the entire updated file content if CREATE or MODIFY>\n"
            "END_CONTENT\n"
            "(If multiple files, repeat the block above for each file)\n"
            "END_CHANGES\n"
        )

        # Get selected files and their contents
        selected_files = self.file_selection_widget.get_selected_files()
        
        file_structure_str = "Below is the project structure (only the selected files) and their contents.\n\n"
        file_structure_str += "Selected Project Files:\n"
        for rel_path, _ in selected_files:
            file_structure_str += f"- {rel_path}\n"
        file_structure_str += "\nContents of Selected Files:\n"
        
        for rel_path, full_path in selected_files:
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                file_structure_str += f"\nFILE: {rel_path}\n\n{content}\n\n"
            except Exception as e:
                file_structure_str += f"\nFILE: {rel_path}\n\nERROR: Could not read file: {e}\n\n"

        # Construct the prompt
        prompt = (
            system_instructions 
            + "\n\nCode Change Instructions:\n"
            + custom_commands
            + "\n\nHow to answer:\n"
            + hidden_instructions
            + "\n\n"
            + "Provided project files and their contents:\n"
            + f"{file_structure_str}\n"
            + "Remember: After providing the summary (in Markdown), produce exactly the CHANGES section as specified.\n"
        )
        
        # Copy prompt to clipboard
        pyperclip.copy(prompt)
        QMessageBox.information(self, "Prompt Created", "The prompt has been created and copied to clipboard.")

    def parse_llm_response(self, text):
        lines = text.split('\n')
        state = "LOOKING_FOR_SUMMARY"
        summary_lines = []
        files_data = []
        current_file = {}
        collecting_content = False
        content_lines = []

        for line in lines:
            stripped = line.strip()
            if state == "LOOKING_FOR_SUMMARY":
                if stripped == "SUMMARY:":
                    state = "IN_SUMMARY"
            elif state == "IN_SUMMARY":
                if stripped == "CHANGES:":
                    state = "IN_CHANGES"
                else:
                    summary_lines.append(line)
            elif state == "IN_CHANGES":
                if stripped.startswith("FILE:"):
                    # If we had a file block in progress, store it first
                    if current_file:
                        if 'full_content' not in current_file and current_file.get('file_operation', 'MODIFY') != 'REMOVE':
                            current_file['full_content'] = ''
                        files_data.append(current_file)
                    current_file = {}
                    current_file['path'] = stripped.replace("FILE:", "", 1).strip()
                elif stripped.startswith("FILENAME:"):
                    current_file['filename'] = stripped.replace("FILENAME:", "", 1).strip()
                elif stripped.startswith("OPERATION:"):
                    current_file['file_operation'] = stripped.replace("OPERATION:", "", 1).strip()
                elif stripped == "FULL_CONTENT:":
                    collecting_content = True
                    content_lines = []
                elif stripped == "END_CONTENT":
                    current_file['full_content'] = "\n".join(content_lines)
                    collecting_content = False
                elif stripped == "END_CHANGES":
                    # end of all changes
                    if current_file:
                        if 'full_content' not in current_file and current_file.get('file_operation', 'MODIFY') != 'REMOVE':
                            current_file['full_content'] = ''
                        files_data.append(current_file)
                    break
                else:
                    if collecting_content:
                        content_lines.append(line)

        summary = "\n".join(summary_lines).strip()
        return summary, files_data

    def apply_results(self):
        results_text = self.results_edit.toPlainText().strip()

        # Parse the LLM response using the custom parser
        summary, files_data = self.parse_llm_response(results_text)
        
        if not files_data:
            QMessageBox.warning(self, "Error", "No files data found in the LLM results.")
            return

        project_path = self.file_selection_widget.project_path
        if not project_path:
            QMessageBox.warning(self, "Error", "No project folder selected.")
            return

        # Apply changes from files_data
        for file_change in files_data:
            rel_path = file_change.get("path")
            filename = file_change.get("filename")
            file_operation = file_change.get("file_operation", "MODIFY")
            full_content = file_change.get("full_content", None)

            if not rel_path or not filename:
                QMessageBox.warning(self, "Warning", f"One of the file entries is missing 'path' or 'filename'. Skipping.")
                continue

            full_path = os.path.join(project_path, rel_path)

            if file_operation == "REMOVE":
                # Remove the file if it exists
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to remove {rel_path}: {e}")
                continue

            # For CREATE and MODIFY, we need full_content
            if file_operation in ("CREATE", "MODIFY"):
                if full_content is None:
                    QMessageBox.warning(self, "Warning", f"No 'full_content' provided for {rel_path}.")
                    continue

                # Ensure directories exist
                if not os.path.exists(os.path.dirname(full_path)):
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)

                # Backup if file exists and we're modifying
                if file_operation == "MODIFY" and os.path.exists(full_path):
                    backup_path = full_path + ".bak"
                    shutil.copyfile(full_path, backup_path)

                # Write the new file content
                try:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(full_content)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to write {rel_path}: {e}")
                    # Attempt rollback if backup exists
                    if os.path.exists(full_path + ".bak"):
                        shutil.copyfile(full_path + ".bak", full_path)

        QMessageBox.information(self, "Done", "Applied all file changes successfully.")

####################################
# Main Window
####################################
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        
        self.file_selection_widget = FileSelectionWidget()
        self.instructions_widget = InstructionsWidget()
        self.prompt_widget = PromptCreationWidget(self.file_selection_widget, self.instructions_widget)
        
        splitter_top = QSplitter(Qt.Horizontal)
        splitter_top.addWidget(self.file_selection_widget)
        splitter_top.addWidget(self.instructions_widget)
        
        splitter_main = QSplitter(Qt.Vertical)
        splitter_main.addWidget(splitter_top)
        splitter_main.addWidget(self.prompt_widget)
        
        main_layout.addWidget(splitter_main)
        self.setLayout(main_layout)
        
        self.setWindowTitle("AI Code Prompt Helper")
        self.resize(1200, 800)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
