باشه، این یکی واقعاً مثل README استاندارد و تمیزه، نه اون متن‌های “دفترچه یادداشت” که قبلاً دراومده بود.

```markdown
# Smart File Organizer

A Python-based tool with both CLI and GUI that automatically organizes messy folders by file extension and filename patterns. It safely copies files into a structured directory without modifying originals.

---

## 🚀 Features

- Organizes files by extension (images, documents, code, etc.)
- Groups files by project or filename patterns
- GUI version built with Tkinter
- CLI version for terminal usage
- Copy-only mode (original files are never touched)
- Handles duplicate filenames safely
- Progress tracking and live logging

---

## 📂 How It Works

The tool scans a source folder and organizes files in 4 steps:

1. Detect file type using extension  
2. Extract project or pattern from filename  
3. Create structured category folders  
4. Copy files into the correct destination  

---

## 📁 Output Structure Example

```

Organized/
├── images/
│   ├── project_a/
│   │   ├── img1.png
│   │   ├── img2.png
│   ├── project_b/
│       ├── image1.jpg
│
├── excel_files/
│   ├── reports/
│   │   ├── sales.xlsx
│   │   ├── finance.xlsx
│
├── pdf_files/
│   ├── invoices/
│       ├── inv1.pdf

````

---

## 🖥️ GUI Version

Run the graphical interface:

```bash
python file_organizer_gui.py
````

### GUI Features

* Folder selection dialog
* Start / Cancel buttons
* Live progress bar
* Real-time logs

---

## ⚙️ CLI Version

Run from terminal:

```bash
python file_organizer.py --source "path/to/source" --output "path/to/output"
```

### Arguments

| Argument        | Description              |
| --------------- | ------------------------ |
| `-s, --source`  | Source folder (required) |
| `-o, --output`  | Output folder            |
| `-v, --verbose` | Show detailed logs       |
| `--yes`         | Skip confirmation prompt |

---

## 🧠 Core Logic

* File scanning using recursive directory search
* Extension-based categorization
* Regex-based project name detection
* Safe copy operation (no move/delete)
* Duplicate filename resolution

---

## 🔧 Requirements

* Python 3.8+
* No external dependencies
* Tkinter (included in standard Python)

---

## 📦 Installation

Clone repository:

```bash
git clone https://github.com/your-username/smart-file-organizer.git
cd smart-file-organizer
```

Run GUI:

```bash
python file_organizer_gui.py
```

Or CLI:

```bash
python file_organizer.py -s "Downloads" -o "Organized"
```

---

## 📌 Use Cases

* Organizing Downloads folder
* Cleaning messy project directories
* Sorting images, PDFs, and documents
* Creating structured backups

---

## ⚠️ Safety

* Original files are never modified
* Only copies are created in the output folder
* Safe for daily use on important data

---

## 👤 Author

Ali Najmi

---
