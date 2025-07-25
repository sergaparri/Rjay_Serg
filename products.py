import os
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Callable
from pathlib import Path
from datetime import datetime, timedelta
import send2trash
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread, Timer
import time
import shutil
try:
    import win32file
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

# --- Models ---
@dataclass
class UserPreferences:
    keep_preference: str = 'newest'  # newest|oldest|largest|smallest
    deletion_method: str = 'recycle'  # recycle|permanent
    filters_enabled: bool = False
    extensions: Set[str] = field(default_factory=set)
    min_size: int = 0
    max_size: int = 0
    size_unit: str = 'KB'
    whitelist: List[str] = field(default_factory=list)
    blacklist: List[str] = field(default_factory=list)
    version_control: bool = False
    versioned_extensions: Set[str] = field(default_factory=lambda: {'.docx', '.pptx', '.xlsx', '.txt'})
    backup_dir: str = field(default_factory=lambda: os.path.join(os.path.expanduser('~'), '.filemonitor_backups'))
    backup_retention_days: int = 30

    def validate(self) -> bool:
        return (self.max_size == 0 or self.min_size <= self.max_size) and \
               self.keep_preference in ('newest', 'oldest', 'largest', 'smallest')

# --- Core Functionality ---
class FileAnalyzer:
    @staticmethod
    def calculate_hash(file_path: str, chunk_size: int = 8192) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (IOError, PermissionError) as e:
            raise RuntimeError(f"Failed to hash {file_path}: {str(e)}")

    @staticmethod
    def compare_files(file1: str, file2: str) -> bool:
        if os.path.islink(file1) or os.path.islink(file2):
            return os.path.realpath(file1) == os.path.realpath(file2)
        return FileAnalyzer.calculate_hash(file1) == FileAnalyzer.calculate_hash(file2)

    @staticmethod
    def find_duplicates(folder: str, filters: Dict) -> Dict[str, List[str]]:
        hashes = {}
        for root, _, files in os.walk(folder):
            for filename in files:
                file_path = os.path.join(root, filename)
                if FileAnalyzer._passes_filters(file_path, filters):
                    try:
                        file_hash = FileAnalyzer.calculate_hash(file_path)
                        hashes.setdefault(file_hash, []).append(file_path)
                    except RuntimeError:
                        continue
        return {h: files for h, files in hashes.items() if len(files) > 1}

    @staticmethod
    def _passes_filters(file_path: str, filters: Dict) -> bool:
        if not os.path.exists(file_path) or os.path.islink(file_path):
            return False
        if filters['extensions']:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in {e.lower() for e in filters['extensions']}:
                return False
        size = os.path.getsize(file_path)
        if filters['min_size'] and size < filters['min_size']:
            return False
        if filters['max_size'] and size > filters['max_size']:
            return False
        return True

    @staticmethod
    def get_available_extensions(folder: str) -> Set[str]:
        """Scan folder and return all unique file extensions"""
        extensions = set()
        for root, _, files in os.walk(folder):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext:  # Only add if extension exists
                    extensions.add(ext)
        return extensions

class FileOperations:
    @staticmethod
    def is_onedrive_file_synced(file_path: str) -> bool:
        """Check if OneDrive file is fully synced and unlocked"""
        try:
            if "OneDrive" in file_path:
                sync_marker = file_path + ".tmp"
                if os.path.exists(sync_marker):
                    return False
            return True
        except:
            return False

    @staticmethod
    def resolve_duplicates(files: List[str], keep_pref: str, deletion_method: str) -> Tuple[List[str], List[str]]:
        if len(files) <= 1:
            return files, []
        
        # Group by file extension first
        ext_groups = {}
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            ext_groups.setdefault(ext, []).append(file)
        
        # Process each extension group separately
        all_to_keep = []
        all_to_delete = []
        
        for ext, ext_files in ext_groups.items():
            # Sort within each extension group
            ext_files.sort(key=lambda x: os.path.basename(x))
            if keep_pref == 'newest':
                ext_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            elif keep_pref == 'oldest':
                ext_files.sort(key=lambda x: os.path.getmtime(x))
            elif keep_pref == 'largest':
                ext_files.sort(key=lambda x: os.path.getsize(x), reverse=True)
            elif keep_pref == 'smallest':
                ext_files.sort(key=lambda x: os.path.getsize(x))
            
            all_to_keep.append(ext_files[0])
            all_to_delete.extend(ext_files[1:])
        
        return all_to_keep, all_to_delete

    @staticmethod
    def safe_delete(file_path: str, method: str, max_retries: int = 5) -> bool:
        """Improved deletion with OneDrive support"""
        for attempt in range(max_retries):
            try:
                # Normalize path first
                file_path = os.path.abspath(file_path)
                
                # Check for long paths
                if len(file_path) > 240:  # Leave room for recycle bin ops
                    file_path = "\\\\?\\" + file_path
                
                # Check if file exists
                if not os.path.exists(file_path):
                    return True
                    
                # Wait for OneDrive sync if needed
                if "OneDrive" in file_path:
                    if not FileOperations.is_onedrive_file_synced(file_path):
                        time.sleep(2)
                        if not FileOperations.is_onedrive_file_synced(file_path):
                            return False
                
                # Unlock file attributes
                if not os.access(file_path, os.W_OK):
                    os.chmod(file_path, 0o777)
                
                # Force close any handles (if pywin32 available)
                if HAS_WIN32:
                    try:
                        handle = win32file.CreateFile(
                            file_path,
                            win32file.GENERIC_WRITE,
                            win32file.FILE_SHARE_DELETE,
                            None,
                            win32file.OPEN_EXISTING,
                            win32file.FILE_FLAG_DELETE_ON_CLOSE,
                            None
                        )
                        win32file.CloseHandle(handle)
                    except Exception:
                        pass
                        
                # Perform deletion
                if method == 'recycle':
                    send2trash.send2trash(file_path)
                else:
                    os.remove(file_path)
                    
                return True
                
            except Exception as e:
                time.sleep(1 + attempt)  # Exponential backoff
                continue
                
        return False

    @staticmethod
    def backup_file(file_path: str, backup_dir: str) -> bool:
        """Create a versioned backup of the file"""
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
            
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}")
            
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            return False

    @staticmethod
    def cleanup_old_backups(backup_dir: str, retention_days: int) -> None:
        """Delete backup files older than retention_days"""
        try:
            if not os.path.exists(backup_dir):
                return
                
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            
            for filename in os.listdir(backup_dir):
                file_path = os.path.join(backup_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_time:
                        os.remove(file_path)
        except Exception:
            pass

class FolderMonitor:
    def __init__(self):
        self.observer = None
        self._running = False
        self._file_hashes = {}  # Track file hashes for version control

    def start(self, path: str, event_handler: FileSystemEventHandler) -> bool:
        if self._running:
            return False
        self.observer = Observer()
        self.observer.schedule(event_handler, path, recursive=True)
        self.observer.start()
        self._running = True
        
        # Initialize file hashes for version control
        self._file_hashes = {}
        for root, _, files in os.walk(path):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    self._file_hashes[file_path] = FileAnalyzer.calculate_hash(file_path)
                except:
                    continue
                    
        return True

    def stop(self) -> None:
        if self.observer and self._running:
            self.observer.stop()
            self.observer.join()
            self._running = False
            self._file_hashes.clear()

    def is_running(self) -> bool:
        return self._running

    def check_file_changed(self, file_path: str) -> bool:
        """Check if file contents have changed since last check"""
        if file_path not in self._file_hashes:
            return False
            
        try:
            current_hash = FileAnalyzer.calculate_hash(file_path)
            if current_hash != self._file_hashes[file_path]:
                self._file_hashes[file_path] = current_hash
                return True
            return False
        except:
            return False

class VersionControlEventHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable, version_callback: Callable, debounce_sec: float = 0.5):
        self.callback = callback
        self.version_callback = version_callback
        self.debounce_sec = debounce_sec
        self._timer: Optional[Timer] = None
        self._pending_events = set()
        self._modified_files = set()

    def _trigger(self):
        self._timer = None
        if self._pending_events:
            self.callback(list(self._pending_events))
            self._pending_events.clear()
        if self._modified_files:
            self.version_callback(list(self._modified_files))
            self._modified_files.clear()

    def on_any_event(self, event):
        if not event.is_directory:
            if self._timer:
                self._timer.cancel()
            
            if event.event_type == 'modified':
                self._modified_files.add(event.src_path)
            elif event.event_type in ['created', 'deleted']:
                self._pending_events.add(event.src_path)
            
            self._timer = Timer(self.debounce_sec, self._trigger)
            self._timer.start()

# --- UI Components ---
class LogPanel(ttk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, text="Activity Log", *args, **kwargs)
        self.log_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, width=80, height=20, state='disabled'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)

class FilterPanel(ttk.LabelFrame):
    def __init__(self, parent, update_callback: Callable, *args, **kwargs):
        super().__init__(parent, text="File Filters", *args, **kwargs)
        self.update_callback = update_callback
        self.extension_options = []
        self._setup_ui()
        self._disable_filters()

    def _setup_ui(self):
        self.filter_enabled = tk.BooleanVar(value=False)
        self.filter_check = ttk.Checkbutton(
            self, 
            text="Enable Filters", 
            variable=self.filter_enabled,
            command=self._on_filter_toggle
        )
        self.filter_check.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5)

        ttk.Label(self, text="File Extensions:").grid(row=1, column=0, sticky=tk.W)
        self.extensions_var = tk.StringVar()
        self.extensions_dropdown = ttk.Combobox(
            self,
            textvariable=self.extensions_var,
            values=self.extension_options,
            state="readonly"
        )
        self.extensions_dropdown.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=5)

        ttk.Label(self, text="Min Size:").grid(row=2, column=0, sticky=tk.W)
        self.min_size_entry = ttk.Entry(self, width=8)
        self.min_size_entry.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(self, text="Max Size:").grid(row=3, column=0, sticky=tk.W)
        self.max_size_entry = ttk.Entry(self, width=8)
        self.max_size_entry.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        self.size_unit = ttk.Combobox(self, values=['KB', 'MB', 'GB'], width=4)
        self.size_unit.current(0)
        self.size_unit.grid(row=2, column=2, rowspan=2, sticky=tk.W, padx=5)

        self.apply_btn = ttk.Button(
            self, 
            text="Apply Filters", 
            command=self._apply_filters
        )
        self.apply_btn.grid(row=4, column=0, columnspan=3, pady=5)

    def _on_filter_toggle(self):
        state = 'normal' if self.filter_enabled.get() else 'disabled'
        for child in [self.extensions_dropdown, self.min_size_entry, self.max_size_entry, self.size_unit, self.apply_btn]:
            child.configure(state=state)

    def _apply_filters(self):
        selected_exts = [ext.strip() for ext in self.extensions_var.get().split(',') if ext.strip()]
        self.update_callback({
            'enabled': self.filter_enabled.get(),
            'extensions': selected_exts,
            'min_size': int(self.min_size_entry.get() or 0),
            'max_size': int(self.max_size_entry.get() or 0),
            'unit': self.size_unit.get()
        })

    def update_extensions(self, extensions: List[str]):
        """Update available extensions in the dropdown"""
        self.extension_options = sorted(ext for ext in extensions if ext)
        self.extensions_dropdown['values'] = self.extension_options
        if self.extension_options:
            self.extensions_var.set(", ".join(self.extension_options[:3]))  # Pre-select first few

    def _disable_filters(self):
        """Disable all filter controls"""
        self.filter_enabled.set(False)
        self.filter_check.config(state='disabled')
        for child in [self.extensions_dropdown, self.min_size_entry, self.max_size_entry, self.size_unit, self.apply_btn]:
            child.config(state='disabled')

    def enable_filters(self):
        """Enable filter controls"""
        self.filter_check.config(state='normal')
        self._on_filter_toggle()

# --- Main Application ---
class SmartFolderMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Folder Monitor")
        self.geometry("1000x700")
        
        # Models
        self.preferences = UserPreferences()
        self.file_filters = {'enabled': False, 'extensions': set(), 'min_size': 0, 'max_size': 0}
        self.monitor = FolderMonitor()
        self._processing = False
        self._pending_files = set()

        # UI Variables
        self.keep_pref = tk.StringVar(value=self.preferences.keep_preference)
        self.del_method = tk.StringVar(value=self.preferences.deletion_method)
        self.version_control = tk.BooleanVar(value=self.preferences.version_control)
        self.backup_dir = tk.StringVar(value=self.preferences.backup_dir)
        self.retention_days = tk.IntVar(value=self.preferences.backup_retention_days)

        # UI
        self._setup_ui()
        self._bind_preferences()

    def _setup_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Folder selection
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(folder_frame, text="Monitor Folder:").pack(side=tk.LEFT)
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        self.folder_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="Browse", command=self._browse_folder).pack(side=tk.LEFT)

        # Settings notebook
        settings_notebook = ttk.Notebook(main_frame)
        settings_notebook.pack(fill=tk.X, pady=10)
        
        # Filter tab
        filter_tab = ttk.Frame(settings_notebook)
        self.filter_panel = FilterPanel(filter_tab, self._update_filters)
        self.filter_panel.pack(fill=tk.X, padx=5, pady=5)
        settings_notebook.add(filter_tab, text="Filters")
        
        # Preferences tab
        pref_tab = ttk.Frame(settings_notebook)
        self._setup_preferences_ui(pref_tab)
        settings_notebook.add(pref_tab, text="Preferences")

        # Log panel
        self.log_panel = LogPanel(main_frame)
        self.log_panel.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(
            control_frame, 
            text="Start Monitoring", 
            command=self._start_monitoring
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            control_frame, 
            text="Stop Monitoring", 
            command=self._stop_monitoring,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

    def _setup_preferences_ui(self, parent):
        # Duplicate handling
        ttk.Label(parent, text="When duplicates are found:").pack(anchor=tk.W, pady=(5,0))
        
        keep_frame = ttk.Frame(parent)
        keep_frame.pack(fill=tk.X, padx=10)
        
        ttk.Radiobutton(
            keep_frame, 
            text="Keep Newest", 
            variable=self.keep_pref, 
            value="newest"
        ).pack(side=tk.LEFT)
        
        ttk.Radiobutton(
            keep_frame, 
            text="Keep Oldest", 
            variable=self.keep_pref, 
            value="oldest"
        ).pack(side=tk.LEFT)
        
        ttk.Radiobutton(
            keep_frame, 
            text="Keep Largest", 
            variable=self.keep_pref, 
            value="largest"
        ).pack(side=tk.LEFT)
        
        ttk.Radiobutton(
            keep_frame, 
            text="Keep Smallest", 
            variable=self.keep_pref, 
            value="smallest"
        ).pack(side=tk.LEFT)

        # Deletion method
        ttk.Label(parent, text="Deletion Method:").pack(anchor=tk.W, pady=(10,0))
        
        del_frame = ttk.Frame(parent)
        del_frame.pack(fill=tk.X, padx=10)
        
        ttk.Radiobutton(
            del_frame, 
            text="Move to Recycle Bin", 
            variable=self.del_method, 
            value="recycle"
        ).pack(side=tk.LEFT)
        
        ttk.Radiobutton(
            del_frame, 
            text="Permanent Delete", 
            variable=self.del_method, 
            value="permanent"
        ).pack(side=tk.LEFT)

        # Size unit
        size_frame = ttk.Frame(parent)
        size_frame.pack(fill=tk.X, pady=(10,0))
        ttk.Label(size_frame, text="Size Unit:").pack(side=tk.LEFT)
        self.size_unit = ttk.Combobox(size_frame, values=['KB', 'MB', 'GB'], width=5)
        self.size_unit.set(self.preferences.size_unit)
        self.size_unit.pack(side=tk.LEFT)

        # Version control settings
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)
        
        version_frame = ttk.Frame(parent)
        version_frame.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(
            version_frame,
            text="Enable Version Control",
            variable=self.version_control
        ).pack(side=tk.LEFT)
        
        ttk.Label(version_frame, text="For:").pack(side=tk.LEFT, padx=5)
        self.version_exts = tk.StringVar(value=", ".join(self.preferences.versioned_extensions))
        ttk.Entry(
            version_frame,
            textvariable=self.version_exts,
            width=20
        ).pack(side=tk.LEFT)
        
        # Backup directory
        backup_frame = ttk.Frame(parent)
        backup_frame.pack(fill=tk.X, pady=5)
        ttk.Label(backup_frame, text="Backup Directory:").pack(side=tk.LEFT)
        ttk.Entry(backup_frame, textvariable=self.backup_dir, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            backup_frame,
            text="Browse",
            command=self._browse_backup_dir
        ).pack(side=tk.LEFT)
        
        # Retention days
        retention_frame = ttk.Frame(parent)
        retention_frame.pack(fill=tk.X, pady=5)
        ttk.Label(retention_frame, text="Keep backups for:").pack(side=tk.LEFT)
        ttk.Entry(retention_frame, textvariable=self.retention_days, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(retention_frame, text="days").pack(side=tk.LEFT)

    def _bind_preferences(self):
        self.keep_pref.trace_add('write', lambda *_: setattr(
            self.preferences, 'keep_preference', self.keep_pref.get()))
        
        self.del_method.trace_add('write', lambda *_: setattr(
            self.preferences, 'deletion_method', self.del_method.get()))
        
        self.size_unit.bind("<<ComboboxSelected>>", lambda e: setattr(
            self.preferences, 'size_unit', self.size_unit.get()))
            
        self.version_control.trace_add('write', lambda *_: setattr(
            self.preferences, 'version_control', self.version_control.get()))
            
        self.backup_dir.trace_add('write', lambda *_: setattr(
            self.preferences, 'backup_dir', self.backup_dir.get()))
            
        self.retention_days.trace_add('write', lambda *_: setattr(
            self.preferences, 'backup_retention_days', self.retention_days.get()))
            
        self.version_exts.trace_add('write', lambda *_: setattr(
            self.preferences, 'versioned_extensions', 
            {ext.strip() for ext in self.version_exts.get().split(',') if ext.strip()}))

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.log_panel.log(f"Selected folder: {folder}")

    def _browse_backup_dir(self):
        folder = filedialog.askdirectory()
        if folder:
            self.backup_dir.set(folder)

    def _update_filters(self, filter_settings: Dict):
        self.file_filters = {
            'enabled': filter_settings['enabled'],
            'extensions': set(filter_settings['extensions']),
            'min_size': filter_settings['min_size'] * (1024 ** {'KB': 0, 'MB': 1, 'GB': 2}[filter_settings['unit']]),
            'max_size': filter_settings['max_size'] * (1024 ** {'KB': 0, 'MB': 1, 'GB': 2}[filter_settings['unit']])
        }
        self.log_panel.log("Filters updated")

    def _start_monitoring(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first")
            return
            
        if not self._processing:
            self._processing = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.folder_entry.config(state='disabled')
            
            # Create backup directory if it doesn't exist
            if self.preferences.version_control:
                os.makedirs(self.preferences.backup_dir, exist_ok=True)
                self.log_panel.log(f"Backup directory: {self.preferences.backup_dir}")
            
            # Scan for available extensions
            try:
                extensions = FileAnalyzer.get_available_extensions(folder)
                self.filter_panel.update_extensions(extensions)
                self.filter_panel.enable_filters()
                self.log_panel.log(f"Found {len(extensions)} file extensions in folder")
            except Exception as e:
                self.log_panel.log(f"Error scanning for extensions: {str(e)}")
            
            # Start file system monitoring
            handler = VersionControlEventHandler(
                self._handle_file_events,
                self._handle_modified_files
            )
            if not self.monitor.start(folder, handler):
                self.log_panel.log("Monitoring is already running")
                return
                
            self.log_panel.log(f"Started monitoring: {folder}")
            
            # Perform initial duplicate check
            Thread(target=self._initial_duplicate_check, daemon=True).start()

    def _handle_modified_files(self, file_paths: List[str]):
        """Handle modified files for version control"""
        if not self.preferences.version_control:
            return
            
        for file_path in file_paths:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in self.preferences.versioned_extensions:
                if self.monitor.check_file_changed(file_path):
                    try:
                        if FileOperations.backup_file(file_path, self.preferences.backup_dir):
                            self.log_panel.log(f"Created backup for modified file: {file_path}")
                        else:
                            self.log_panel.log(f"Failed to backup modified file: {file_path}")
                    except Exception as e:
                        self.log_panel.log(f"Error backing up file: {str(e)}")
                
                # Cleanup old backups
                FileOperations.cleanup_old_backups(
                    self.preferences.backup_dir,
                    self.preferences.backup_retention_days
                )

    def _initial_duplicate_check(self):
        """Perform immediate duplicate check when monitoring starts"""
        folder = self.folder_path.get()
        try:
            self.log_panel.log("Performing initial duplicate scan...")
            duplicates = FileAnalyzer.find_duplicates(folder, self.file_filters)
            if duplicates:
                self.log_panel.log(f"Found {len(duplicates)} duplicate groups")
                self._resolve_duplicates(duplicates)
            else:
                self.log_panel.log("No duplicates found in initial scan")
        except Exception as e:
            self.log_panel.log(f"Error during initial scan: {str(e)}")
        finally:
            self._processing = False

    def _handle_file_events(self, file_paths: List[str]):
        """Handle batch file events"""
        if not file_paths:
            return
            
        self.log_panel.log(f"Processing {len(file_paths)} changed files...")
        
        # Group by parent directory
        dir_groups = {}
        for path in file_paths:
            if not Path(path).exists():
                continue
                
            if self.file_filters['enabled'] and not FileAnalyzer._passes_filters(path, self.file_filters):
                self.log_panel.log(f"Ignored {path} (didn't pass filters)")
                continue
                
            parent_dir = str(Path(path).parent)
            dir_groups.setdefault(parent_dir, []).append(path)
        
        # Process each directory group
        for parent_dir, files in dir_groups.items():
            try:
                duplicates = FileAnalyzer.find_duplicates(parent_dir, self.file_filters)
                if duplicates:
                    self._resolve_duplicates(duplicates)
            except Exception as e:
                self.log_panel.log(f"Error processing {parent_dir}: {str(e)}")

    def _resolve_duplicates(self, duplicates: Dict[str, List[str]]):
        """Handle duplicate resolution for multiple file types"""
        total_deleted = 0
        total_groups = len(duplicates)
        
        for file_hash, files in duplicates.items():
            try:
                to_keep, to_delete = FileOperations.resolve_duplicates(
                    files,
                    self.preferences.keep_preference,
                    self.preferences.deletion_method
                )
                
                for file in to_delete:
                    # Skip if file no longer exists
                    if not os.path.exists(file):
                        continue
                        
                    # Special handling for OneDrive files
                    if "OneDrive" in file:
                        self.log_panel.log(f"Attempting to delete OneDrive file: {file}")
                        
                    if FileOperations.safe_delete(file, self.preferences.deletion_method):
                        self.log_panel.log(f"Successfully deleted: {file}")
                        total_deleted += 1
                    else:
                        self.log_panel.log(f"Permanent failure deleting: {file}. " +
                                         "File may be locked by OneDrive sync.")
                        
            except Exception as e:
                self.log_panel.log(f"Error processing duplicates: {str(e)}")
        
        self.log_panel.log(f"Duplicate resolution complete. Processed {total_groups} groups, deleted {total_deleted} files")

    def _stop_monitoring(self):
        if self.monitor.is_running():
            self.monitor.stop()
            self.log_panel.log("Monitoring stopped")
        if self._processing:
            self._processing = False
            self.log_panel.log("Scan stopped by user")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.folder_entry.config(state='normal')

    def _on_close(self):
        self._stop_monitoring()
        self.destroy()

if __name__ == "__main__":
    app = SmartFolderMonitor()
    app.protocol("WM_DELETE_WINDOW", app._on_close)
    app.mainloop()
