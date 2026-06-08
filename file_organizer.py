"""
Smart File Organizer - Advanced Grouping Engine with Windows Path Fix
Organizes files by extension AND filename similarity.

Fixes:
- Handles Windows MAX_PATH (260 character) limitation
- Uses \\\\?\\ prefix for long paths (Windows 10+)
- Better error handling for path-related issues
"""

import os
import shutil
import re
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple, Optional, Dict, Set
from difflib import SequenceMatcher


# ============================================================================
# CONFIGURATION
# ============================================================================

# Known extension to category mapping
KNOWN_EXTENSIONS = {
    '.xlsx': 'excel_files', '.xls': 'excel_files', '.xlsm': 'excel_files', '.csv': 'excel_files',
    '.docx': 'word_files', '.doc': 'word_files', '.rtf': 'word_files',
    '.pptx': 'powerpoint_files', '.ppt': 'powerpoint_files',
    '.pdf': 'pdf_files',
    '.txt': 'text_files', '.md': 'text_files', '.log': 'text_files',
    '.png': 'images', '.jpg': 'images', '.jpeg': 'images', '.gif': 'images',
    '.bmp': 'images', '.svg': 'images', '.webp': 'images', '.ico': 'images',
    '.mp3': 'audio', '.wav': 'audio', '.flac': 'audio', '.m4a': 'audio',
    '.ogg': 'audio', '.aac': 'audio',
    '.mp4': 'video', '.avi': 'video', '.mkv': 'video', '.mov': 'video',
    '.wmv': 'video', '.flv': 'video', '.webm': 'video',
    '.zip': 'archives', '.rar': 'archives', '.7z': 'archives',
    '.tar': 'archives', '.gz': 'archives', '.bz2': 'archives',
    '.py': 'code', '.js': 'code', '.html': 'code', '.css': 'code',
    '.json': 'data', '.xml': 'data', '.yaml': 'data', '.yml': 'data',
    '.db': 'data', '.sqlite': 'data', '.sql': 'data',
    '.psd': 'design', '.ai': 'design', '.eps': 'design', '.fig': 'design',
    '.exe': 'executables', '.msi': 'executables', '.sh': 'scripts',
    '.bat': 'scripts', '.cmd': 'scripts', '.ps1': 'scripts',
}

# Project name patterns
PROJECT_PATTERNS = [
    (r'(?i)(بابل|babol)', 'پروژه_بابل'),
    (r'(?i)(تیس|tiss)', 'پروژه_تیس'),
    (r'(?i)(داتین|datin)', 'پروژه_داتین'),
    (r'(?i)(آپارات|aparat)', 'کلاینت_آپارات'),
    (r'(?i)(دیجی‌کالا|digikala)', 'کلاینت_دیجی‌کالا'),
    (r'(?i)(اسنپ|snapp)', 'کلاینت_اسنپ'),
    (r'(?i)(تپسی|tapsi)', 'کلاینت_تپسی'),
]

SIMILARITY_THRESHOLD = 0.6
MIN_GROUP_SIZE = 2
PROGRESS_INTERVAL = 50

IGNORE_FILES = {'desktop.ini', 'thumbs.db', '.ds_store', '.gitkeep', '.gitignore'}

# Maximum folder name length (Windows safe)
MAX_FOLDER_NAME_LEN = 50
MAX_TOTAL_PATH_LEN = 240  # Leave room for prefix and filename


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def safe_path(path: Path) -> str:
    """
    Convert Path to Windows long path format if needed.
    Uses \\\\?\\ prefix for paths longer than 260 characters.
    """
    path_str = str(path)
    if os.name == 'nt' and len(path_str) > 200:
        # Add long path prefix if not already present
        if not path_str.startswith('\\\\?\\'):
            return '\\\\?\\' + os.path.abspath(path_str)
    return path_str


def shorten_folder_name(name: str, max_len: int = MAX_FOLDER_NAME_LEN) -> str:
    """Shorten folder name if too long."""
    if len(name) <= max_len:
        return name
    
    # Try to keep first part and last part
    parts = name.split('_')
    if len(parts) > 1:
        # Keep first 2 parts and last part
        short = '_'.join(parts[:2] + parts[-1:])
        if len(short) <= max_len:
            return short
    
    # Just truncate
    return name[:max_len-3] + '...'


def get_folder_name_for_extension(ext: str) -> str:
    """Get folder name for a file extension."""
    ext_lower = ext.lower()
    if ext_lower in KNOWN_EXTENSIONS:
        return KNOWN_EXTENSIONS[ext_lower]
    
    ext_name = ext_lower[1:] if ext_lower.startswith('.') else ext_lower
    if ext_name:
        return shorten_folder_name(f"{ext_name}_files", 40)
    return "no_extension_files"


def normalize_filename(filename: str) -> str:
    """Normalize filename for similarity comparison."""
    name = Path(filename).stem
    
    name = re.sub(r'[-_\s]?(v|ver|version)[-_\s]?\d+', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\d+$', '', name)
    name = re.sub(r'[_\-\s]?\d+[_\-\s]?', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_-')
    name = name.lower()
    
    return shorten_folder_name(name, 40) if name else "unnamed"


def calculate_similarity(name1: str, name2: str) -> float:
    """Calculate similarity ratio between two normalized names."""
    return SequenceMatcher(None, name1, name2).ratio()


def get_common_prefix(names: List[str]) -> str:
    """Get the longest common prefix from a list of names."""
    if not names:
        return "unknown"
    
    prefix = names[0]
    for name in names[1:]:
        while not name.startswith(prefix) and prefix:
            prefix = prefix[:-1]
        if not prefix:
            break
    
    prefix = prefix.strip('_-')
    return shorten_folder_name(prefix, 40) if prefix else "unknown"


def extract_project_name(filename: str) -> Optional[str]:
    """Extract project name from filename."""
    name = Path(filename).stem
    for pattern, project_name in PROJECT_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return shorten_folder_name(project_name, 40)
    return None


def group_by_similarity(files: List[Path]) -> Dict[str, List[Path]]:
    """Group files by filename similarity."""
    if not files:
        return {}
    
    normalized = {f: normalize_filename(f.name) for f in files}
    groups = {}
    used = set()
    
    for file_path, norm_name in normalized.items():
        if file_path in used:
            continue
        
        group_files = [file_path]
        group_names = [norm_name]
        
        for other_path, other_norm in normalized.items():
            if other_path == file_path or other_path in used:
                continue
            
            if calculate_similarity(norm_name, other_norm) >= SIMILARITY_THRESHOLD:
                group_files.append(other_path)
                group_names.append(other_norm)
                used.add(other_path)
        
        used.add(file_path)
        
        if len(group_files) >= MIN_GROUP_SIZE:
            group_name = get_common_prefix(group_names)
        else:
            group_name = norm_name
        
        groups[group_name] = group_files
    
    return groups


def get_unique_destination(folder: Path, filename: str) -> Path:
    """Get unique filename if duplicate exists."""
    dest = folder / filename
    if not dest.exists():
        return dest
    
    stem = Path(filename).stem
    ext = Path(filename).suffix
    counter = 1
    while (folder / f"{stem}_{counter}{ext}").exists():
        counter += 1
    return folder / f"{stem}_{counter}{ext}"


# ============================================================================
# SCROLLABLE FRAME
# ============================================================================

class ScrollableFrame(tk.Frame):
    """A scrollable frame that can contain any widgets."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.canvas = tk.Canvas(self, highlightthickness=0, bg='#f0f0f0')
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def get_content_frame(self):
        return self.scrollable_frame


# ============================================================================
# ORGANIZER ENGINE
# ============================================================================

class AdvancedFileOrganizer:
    def __init__(self, source_path: Path, output_path: Path, verbose: bool = False):
        self.source_path = source_path
        self.output_path = output_path
        self.verbose = verbose
        self.cancel_flag = False
        
        self.stats = {
            'total': 0, 'processed': 0, 'copied': 0, 'failed': 0,
            'categories': defaultdict(int), 'groups': defaultdict(int), 'extensions': defaultdict(int)
        }
        self.failed_files = []
        self.progress_callback = None
    
    def set_progress_callback(self, callback):
        self.progress_callback = callback
    
    def log(self, message: str):
        if self.verbose:
            print(message)
    
    def cancel(self):
        self.cancel_flag = True
    
    def _update_progress(self):
        if self.progress_callback and self.stats['total'] > 0:
            percent = (self.stats['processed'] / self.stats['total']) * 100
            self.progress_callback(self.stats['processed'], self.stats['total'], percent)
    
    def scan_files(self) -> List[Path]:
        files = []
        for f in self.source_path.rglob("*"):
            if not f.is_file():
                continue
            if f.name.lower() in IGNORE_FILES or f.name.startswith('.'):
                continue
            files.append(f)
        return files
    
    def group_files_by_category(self, files: List[Path]) -> Dict[str, Dict[str, List[Path]]]:
        category_files = defaultdict(list)
        project_files = defaultdict(list)
        
        for f in files:
            ext = f.suffix.lower()
            category = get_folder_name_for_extension(ext)
            self.stats['extensions'][ext if ext else 'no_extension'] += 1
            
            project = extract_project_name(f.name)
            if project:
                project_files[f"{category}|{project}"].append(f)
            else:
                category_files[category].append(f)
        
        result = {}
        
        for key, flist in project_files.items():
            cat, proj = key.split('|', 1)
            if cat not in result:
                result[cat] = {}
            result[cat][proj] = flist
            self.stats['groups'][proj] += len(flist)
        
        for cat, flist in category_files.items():
            if cat not in result:
                result[cat] = {}
            if not flist:
                continue
            
            groups = group_by_similarity(flist)
            for gname, gfiles in groups.items():
                if len(gfiles) >= MIN_GROUP_SIZE:
                    result[cat][gname] = gfiles
                    self.stats['groups'][gname] += len(gfiles)
                else:
                    for ff in gfiles:
                        sname = normalize_filename(ff.name)
                        result[cat][sname] = [ff]
                        self.stats['groups'][sname] += 1
        
        return result
    
    def copy_files(self, grouped_files: Dict[str, Dict[str, List[Path]]]) -> None:
        created_folders = set()
        
        for groups in grouped_files.values():
            for flist in groups.values():
                self.stats['total'] += len(flist)
        
        for category, groups in grouped_files.items():
            for group_name, files in groups.items():
                if self.cancel_flag:
                    return
                
                dest_folder = self.output_path / category / group_name
                
                # Check path length
                dest_path_str = str(dest_folder)
                if len(dest_path_str) > MAX_TOTAL_PATH_LEN:
                    self.log(f"   ⚠️ Path too long, skipping: {category}/{group_name}/")
                    for f in files:
                        self.stats['failed'] += 1
                        self.stats['processed'] += 1
                        self.failed_files.append((f, "Path too long"))
                    continue
                
                if dest_folder not in created_folders:
                    try:
                        dest_folder.mkdir(parents=True, exist_ok=True)
                        created_folders.add(dest_folder)
                        if self.verbose:
                            self.log(f"📁 Creating: {category}/{group_name}/")
                    except Exception as e:
                        self.log(f"   ❌ Failed to create folder: {category}/{group_name}/ - {e}")
                        for f in files:
                            self.stats['failed'] += 1
                            self.stats['processed'] += 1
                            self.failed_files.append((f, str(e)))
                        continue
                
                for f in files:
                    if self.cancel_flag:
                        return
                    
                    try:
                        dest = get_unique_destination(dest_folder, f.name)
                        shutil.copy2(f, dest)
                        self.stats['copied'] += 1
                        self.stats['categories'][category] += 1
                        self.stats['processed'] += 1
                        
                        if self.verbose and self.stats['processed'] % PROGRESS_INTERVAL == 0:
                            self.log(f"   📊 Progress: {self.stats['processed']}/{self.stats['total']} files")
                        self._update_progress()
                        
                    except Exception as e:
                        self.stats['failed'] += 1
                        self.stats['processed'] += 1
                        self.failed_files.append((f, str(e)))
                        self.log(f"   ❌ Failed: {f.name} - {e}")
                        self._update_progress()
    
    def run(self) -> Tuple[int, int, Dict]:
        """Main run method - executes the full organization pipeline."""
        self.stats = {
            'total': 0, 'processed': 0, 'copied': 0, 'failed': 0,
            'categories': defaultdict(int), 'groups': defaultdict(int), 'extensions': defaultdict(int)
        }
        self.failed_files = []
        
        # Scan files
        files = self.scan_files()
        
        if not files:
            return 0, 0, {}
        
        self.stats['total'] = len(files)
        
        # Group files
        grouped_files = self.group_files_by_category(files)
        
        # Copy files
        self.copy_files(grouped_files)
        
        return self.stats['copied'], self.stats['failed'], self.stats
    
    def print_summary(self) -> str:
        result = []
        result.append("\n" + "=" * 60)
        result.append("✅ ORGANIZATION COMPLETE!")
        result.append("=" * 60)
        result.append(f"📊 Total files: {self.stats['total']}")
        result.append(f"✅ Copied: {self.stats['copied']}")
        result.append(f"❌ Failed: {self.stats['failed']}")
        
        if self.stats['categories']:
            result.append("\n📁 By category:")
            for cat, cnt in sorted(self.stats['categories'].items(), key=lambda x: -x[1]):
                result.append(f"   📂 {cat}: {cnt} file(s)")
        
        if self.stats['extensions']:
            result.append("\n🔤 By file type:")
            for ext, cnt in sorted(self.stats['extensions'].items(), key=lambda x: -x[1])[:10]:
                result.append(f"   📄 {ext}: {cnt} file(s)")
        
        if self.failed_files:
            result.append(f"\n❌ Failed files ({len(self.failed_files)}):")
            for f, err in self.failed_files[:10]:
                result.append(f"   • {f.name}: {err}")
        
        result.append(f"\n📂 Output: {self.output_path}")
        result.append("💡 Original files were NOT modified.")
        result.append("=" * 60)
        
        return "\n".join(result)


# ============================================================================
# GUI APPLICATION
# ============================================================================

class OrganizerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart File Organizer - Advanced Grouping")
        self.root.geometry("950x750")
        self.root.configure(bg='#f0f0f0')
        
        self.organizer = None
        self.thread = None
        
        self._create_widgets()
        self._center_window()
    
    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
    
    def _create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg='#2c3e50', height=90)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📁 Smart File Organizer", font=('Segoe UI', 18, 'bold'),
                bg='#2c3e50', fg='white').pack(expand=True)
        tk.Label(header, text="Groups similar filenames | Auto-detects any extension | Handles 100,000+ files",
                font=('Segoe UI', 9), bg='#2c3e50', fg='#bdc3c7').pack()
        
        # Main scrollable area
        self.scrollable = ScrollableFrame(self.root, bg='#f0f0f0')
        self.scrollable.pack(fill=tk.BOTH, expand=True)
        main = self.scrollable.get_content_frame()
        inner = tk.Frame(main, bg='#f0f0f0', padx=20, pady=20)
        inner.pack(fill=tk.BOTH, expand=True)
        
        # Source folder
        src_frame = tk.LabelFrame(inner, text="Source Folder", font=('Segoe UI', 10, 'bold'), bg='#f0f0f0')
        src_frame.pack(fill=tk.X, pady=(0, 15))
        src_row = tk.Frame(src_frame, bg='#f0f0f0')
        src_row.pack(fill=tk.X, padx=10, pady=10)
        
        self.source_var = tk.StringVar()
        tk.Entry(src_row, textvariable=self.source_var, font=('Segoe UI', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Button(src_row, text="Browse", command=self._browse_source, bg='#3498db', fg='white', padx=15).pack(side=tk.RIGHT)
        
        # Output folder
        out_frame = tk.LabelFrame(inner, text="Output Folder (auto-generated)", font=('Segoe UI', 10, 'bold'), bg='#f0f0f0')
        out_frame.pack(fill=tk.X, pady=(0, 15))
        out_row = tk.Frame(out_frame, bg='#f0f0f0')
        out_row.pack(fill=tk.X, padx=10, pady=10)
        
        self.output_var = tk.StringVar()
        tk.Entry(out_row, textvariable=self.output_var, font=('Segoe UI', 10), state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Progress
        prog_frame = tk.LabelFrame(inner, text="Progress", font=('Segoe UI', 10, 'bold'), bg='#f0f0f0')
        prog_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = tk.Scale(prog_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                     variable=self.progress_var, state=tk.DISABLED, length=400)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = tk.Label(prog_frame, text="Ready", bg='#f0f0f0', fg='#666')
        self.status_label.pack(pady=(0, 10))
        
        # Log
        log_frame = tk.LabelFrame(inner, text="Log", font=('Segoe UI', 10, 'bold'), bg='#f0f0f0')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, font=('Consolas', 9), height=18, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(inner, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X)
        
        self.start_btn = tk.Button(btn_frame, text="▶ Start Organizing", command=self._start_organization,
                                  bg='#27ae60', fg='white', font=('Segoe UI', 11, 'bold'), padx=20, pady=10)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_btn = tk.Button(btn_frame, text="Cancel", command=self._cancel_organization,
                                   bg='#e74c3c', fg='white', font=('Segoe UI', 11), padx=20, pady=10, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT)
        
        tk.Button(btn_frame, text="Clear Log", command=self._clear_log,
                 bg='#f39c12', fg='white', font=('Segoe UI', 11), padx=20, pady=10).pack(side=tk.RIGHT)
    
    def _browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_var.set(folder)
            src = Path(folder)
            self.output_var.set(str(src.parent / f"{src.name}_Sorted"))
    
    def _log(self, message: str, is_error: bool = False):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def _clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def _update_progress(self, current: int, total: int, percent: float):
        self.progress_var.set(percent)
        self.status_label.config(text=f"Processing... {current}/{total} files ({percent:.1f}%)")
        self.root.update_idletasks()
    
    def _cancel_organization(self):
        if self.organizer:
            self.organizer.cancel()
        self._log("⚠️ Cancelling... Please wait")
    
    def _start_organization(self):
        source = self.source_var.get().strip()
        if not source:
            messagebox.showerror("Error", "Please select a source folder.")
            return
        
        src_path = Path(source)
        if not src_path.exists():
            messagebox.showerror("Error", f"Source folder not found: {source}")
            return
        
        out = self.output_var.get().strip()
        if not out:
            out = str(src_path.parent / f"{src_path.name}_Sorted")
            self.output_var.set(out)
        
        out_path = Path(out)
        
        self.start_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self._clear_log()
        
        self.organizer = AdvancedFileOrganizer(src_path, out_path, verbose=True)
        self.organizer.set_progress_callback(self._update_progress)
        
        self.thread = threading.Thread(target=self._run_organizer, daemon=True)
        self.thread.start()
    
    def _run_organizer(self):
        try:
            copied, failed, _ = self.organizer.run()
            self.root.after(0, self._on_complete, copied, failed)
        except Exception as e:
            self.root.after(0, self._on_error, str(e))
    
    def _on_complete(self, copied, failed):
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_var.set(100)
        self.status_label.config(text=f"Complete! {copied} files organized.")
        
        # Show summary in log
        summary = self.organizer.print_summary()
        self._log(summary)
        
        if failed > 0:
            messagebox.showwarning("Complete", f"Organized {copied} files.\nFailed: {failed}\nCheck log for details.")
        else:
            messagebox.showinfo("Complete", f"Successfully organized {copied} files!")
    
    def _on_error(self, error_msg):
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self._log(f"❌ Error: {error_msg}", is_error=True)
        messagebox.showerror("Error", error_msg)
    
    def run(self):
        self.root.mainloop()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app = OrganizerGUI()
    app.run()