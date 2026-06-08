```text
Smart File Organizer

A Python-based desktop and CLI tool that automatically organizes files by extension and filename patterns. It includes a GUI (Tkinter) and a safe copy-only mode to ensure original files remain untouched.

------------------------------------------------------------

FEATURES

- Organizes files by extension (images, documents, code, etc.)
- Groups files by similar filename patterns
- GUI version using Tkinter
- CLI version for terminal usage
- Safe copy-only mode (no deletion or movement)
- Handles duplicate filenames automatically
- Progress tracking and live logging

------------------------------------------------------------

HOW IT WORKS

The tool scans a source directory and:

1. Detects file type by extension  
2. Extracts meaningful patterns from filenames  
3. Creates categorized folders  
4. Copies files into structured directories  

------------------------------------------------------------

EXAMPLE OUTPUT STRUCTURE

Organized/
├── images/
│   ├── cat/
│   │   ├── cat1.png
│   │   ├── cat2.png
│   ├── nature/
│   │   ├── nature1.jpg
│
├── excel_files/
│   ├── report/
│   │   ├── report.xlsx
│   │   ├── report_final.xlsx
│
├── pdf_files/
│   ├── invoice/
│   │   ├── invoice1.pdf

------------------------------------------------------------

GUI VERSION

Run:
python file_organizer_gui.py

Features:
- Folder selection
- Progress bar
- Live logs
- Cancel button

------------------------------------------------------------

CLI VERSION

Run:
python file_organizer.py --source "path/to/source" --output "path/to/output"

Options:
- -s, --source  : Source folder (required)
- -o, --output  : Output folder
- -v, --verbose : Detailed logs
- --yes         : Skip confirmation

------------------------------------------------------------

LOGIC OVERVIEW

- Step 1: Group files by extension
- Step 2: Extract base filename patterns
- Step 3: Group similar names into folders
- Step 4: Copy files safely (no modification of originals)

------------------------------------------------------------

REQUIREMENTS

- Python 3.8+
- No external libraries required
- Tkinter (included in standard Python installation)

------------------------------------------------------------

INSTALLATION

git clone https://github.com/your-username/smart-file-organizer.git
cd smart-file-organizer

Run:
python file_organizer_gui.py

------------------------------------------------------------

USE CASES

- Organizing Downloads folder
- Cleaning messy project directories
- Sorting images, documents, and code
- Backup structuring

------------------------------------------------------------

IMPORTANT NOTES

- This tool does NOT delete or move original files
- Only creates copies in the output directory
- Safe for everyday file organization

------------------------------------------------------------

AUTHOR

Ali Najmi

------------------------------------------------------------

LICENSE

MIT License
```
