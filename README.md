````markdown
# Smart File Organizer

## Overview

A Python-based file organization tool that automatically sorts and structures messy folders based on file extensions and filename patterns.

The system scans a directory, analyzes file types, detects project or pattern names from filenames, and copies files into a clean structured folder hierarchy without modifying the original data.

---

## Features

### File Organization
- Organizes files by extension (images, documents, code, etc.)
- Separates files into dedicated category folders
- Supports automatic grouping of similar filenames into subfolders

### Project Detection
- Detects project/client names from filenames using regex patterns
- Supports custom project naming rules
- Groups related files under the same project folder

### Safe Processing
- Copy-only mode (no deletion or movement of original files)
- Duplicate filename handling
- Safe directory creation

### User Interface
- CLI (Command Line Interface)
- GUI version using Tkinter
- Progress tracking and live logs

---

## Project Structure

```text
smart-file-organizer/
│
├── file_organizer.py
├── file_organizer_gui.py
├── README.md
├── requirements.txt
│
├── Organized/
│   ├── images/
│   │   ├── project_a/
│   │   ├── project_b/
│   │
│   ├── excel_files/
│   │   ├── reports/
│   │
│   ├── pdf_files/
│   │   ├── invoices/
│
└── logs/
````

---

## Technologies Used

* Python
* OS / Pathlib
* Shutil
* Regex
* Tkinter (GUI)

---

## Output Structure

Files are organized into the following hierarchy:

```text
Output/
│
├── {category}/
│   ├── {project_or_pattern}/
│   │   ├── file.ext
```

Examples of categories:

* images
* excel_files
* pdf_files
* audio
* video
* code

---

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/smart-file-organizer.git
cd smart-file-organizer
```

No external dependencies required (standard Python only).

---

## Usage

### CLI Version

```bash
python file_organizer.py --source "path/to/source" --output "path/to/output"
```

Options:

* `-s, --source` → Source directory
* `-o, --output` → Output directory
* `-v, --verbose` → Detailed logs
* `--yes` → Skip confirmation

---

### GUI Version

```bash
python file_organizer_gui.py
```

---

## Workflow

```text
Source Folder
     │
     ▼
File Scanning
     │
     ▼
Extension Detection
     │
     ▼
Project/Pattern Extraction
     │
     ▼
Folder Structure Creation
     │
     ▼
Safe File Copy
     │
     ▼
Organized Output
```

---

## Safety

* Original files are never modified
* Only copies are created in the output directory
* Safe for production and personal use

---

## Future Improvements

* File tagging system
* Advanced AI-based filename classification
* Configurable rules via JSON/YAML
* Cloud storage integration
* Duplicate content detection (hash-based)

---

## Author

Ali Najmi

```
```
