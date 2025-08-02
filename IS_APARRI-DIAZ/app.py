import tkinter as tk
from core.models import UserPreferences
from core.file_analyzer import FileAnalyzer
from core.file_operations import FileOperations
from core.monitor import FolderMonitor, DebouncedEventHandler
from ui.log_panel import LogPanel
from ui.filter_panel import FilterPanel
from ui.scoring_panel import ScoringSettingsPanel
from ui.tray import SystemTrayIcon
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont
from pathlib import Path
from threading import Thread
from typing import Dict, List
import os

class SmartFolderMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Folder Monitor ✨")
        self.geometry("1000x700")
        self.minsize(800, 600)
        self.configure(bg="#f7f7fa")
        # Set default font for ttk widgets
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=11, family="Segoe UI")
        self.option_add("*Font", default_font)
        self.heading_font = tkfont.Font(family="Comic Sans MS", size=18, weight="bold")
        self.status_fun = False  # For easter egg
        
        # Models
        self.preferences = UserPreferences()
        self.file_filters = {'enabled': False, 'extensions': set(), 'min_size': 0, 'max_size': 0}
        self.monitor = FolderMonitor()
        self._processing = False
        self._pending_files = set()
        self.tray_icon = None

        # UI Variables
        self.keep_pref = tk.StringVar(value=self.preferences.keep_preference)
        self.del_method = tk.StringVar(value=self.preferences.deletion_method)
        self.size_unit_var = tk.StringVar(value=self.preferences.size_unit)

        # UI
        self._setup_ui()
        self._bind_preferences()
        self._setup_system_tray()

    def _setup_system_tray(self):
        self.tray_icon = SystemTrayIcon(self, self)
        self.tray_icon.run()
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        main_frame = ttk.Frame(self, padding="16 12 16 12", style="Main.TFrame")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(5, weight=1)
        # Title/logo area
        title_frame = ttk.Frame(main_frame, style="Title.TFrame")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        title_frame.grid_columnconfigure(1, weight=1)
        # Playful emoji logo
        logo_label = ttk.Label(title_frame, text="🗂️✨", font=("Segoe UI Emoji", 32))
        logo_label.grid(row=0, column=0, sticky="w", padx=(0, 8))
        logo_label.bind("<Button-1>", self._easter_egg)
        ttk.Label(title_frame, text="Smart Folder Monitor", font=self.heading_font, foreground="#4a90e2").grid(row=0, column=1, sticky="w")
        # Folder selection
        folder_frame = ttk.Frame(main_frame, style="Panel.TFrame")
        folder_frame.grid(row=1, column=0, sticky="ew", pady=5)
        folder_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(folder_frame, text="Monitor Folder:", font=("Segoe UI", 11, "bold"), background="#e3f2fd").grid(row=0, column=0, sticky="w")
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path)
        self.folder_entry.grid(row=0, column=1, sticky="ew", padx=5)
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self._browse_folder, style="Accent.TButton")
        browse_btn.grid(row=0, column=2, sticky="e")
        self._add_tooltip(browse_btn, "Select a folder to monitor for duplicates.")
        self._add_hover(browse_btn)
        # Settings notebook
        settings_notebook = ttk.Notebook(main_frame, style="Fun.TNotebook")
        settings_notebook.grid(row=2, column=0, sticky="ew", pady=10)
        # Filter tab
        filter_tab = ttk.Frame(settings_notebook, style="Panel.TFrame")
        self.filter_panel = FilterPanel(filter_tab, self._update_filters)
        self.filter_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        settings_notebook.add(filter_tab, text="🔍 Filters")
        # Preferences tab
        pref_tab = ttk.Frame(settings_notebook, style="Panel.TFrame")
        self._setup_preferences_ui(pref_tab)                                                                                                                                                     
        settings_notebook.add(pref_tab, text="⚙️ Preferences")
        # Scoring tab
        score_tab = ttk.Frame(settings_notebook, style="Panel.TFrame")
        self.scoring_panel = ScoringSettingsPanel(
            score_tab,
            self._update_scoring_settings
        )
        self.scoring_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        settings_notebook.add(score_tab, text="🏆 Scoring")
        # Log panel (visually distinct)
        log_panel_frame = ttk.Frame(main_frame, style="LogPanel.TFrame")
        log_panel_frame.grid(row=5, column=0, sticky="nsew", pady=(10, 0))
        log_panel_frame.grid_rowconfigure(0, weight=1)
        log_panel_frame.grid_columnconfigure(0, weight=1)
        self.log_panel = LogPanel(log_panel_frame)
        self.log_panel.grid(row=0, column=0, sticky="nsew")
        # Control buttons
        control_frame = ttk.Frame(main_frame, style="Panel.TFrame")
        control_frame.grid(row=6, column=0, sticky="ew", pady=10)
        control_frame.grid_columnconfigure(0, weight=1)
        self.start_btn = ttk.Button(
            control_frame, 
            text="🚦 Start Monitoring", 
            command=self._start_monitoring,
            style="Accent.TButton"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self._add_tooltip(self.start_btn, "Begin monitoring the selected folder.")
        self._add_hover(self.start_btn)
        self.stop_btn = ttk.Button(
            control_frame, 
            text="🛑 Stop Monitoring", 
            command=self._stop_monitoring,
            state=tk.DISABLED,
            style="Accent.TButton"
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self._add_tooltip(self.stop_btn, "Stop monitoring the folder.")
        self._add_hover(self.stop_btn)
        self.minimize_btn = ttk.Button(
            control_frame,
            text="🧺 Minimize to Tray",
            command=self.hide_window,
            style="Accent.TButton"
        )
        self.minimize_btn.pack(side=tk.RIGHT, padx=5)
        self._add_tooltip(self.minimize_btn, "Minimize the app to the system tray.")
        self._add_hover(self.minimize_btn)
        # Progress bar for monitoring
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate", style="Fun.Horizontal.TProgressbar")
        self.progress.grid(row=7, column=0, sticky="ew", pady=(0, 5))
        self.progress.grid_remove()
        # Status bar (fun and visually distinct)
        self.status_var = tk.StringVar(value="Ready 🚀")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding=(8, 4), font=("Segoe UI", 11, "italic"), background="#fffde7", foreground="#4a90e2")
        status_bar.grid(row=8, column=0, sticky="ew", pady=(5, 0))
        # Styles
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Main.TFrame", background="#f7f7fa")
        style.configure("Title.TFrame", background="#e3f2fd")
        style.configure("Panel.TFrame", background="#fce4ec", borderwidth=0)
        style.configure("LogPanel.TFrame", background="#f4f8fb", borderwidth=2, relief="ridge")
        style.configure("Accent.TButton", background="#4a90e2", foreground="#fff", borderwidth=0, focusthickness=3, focuscolor="#fce4ec", font=("Segoe UI", 11, "bold"), padding=6)
        style.map("Accent.TButton",
            background=[("active", "#1976d2"), ("disabled", "#b0bec5")],
            foreground=[("active", "#fff")]
        )
        style.configure("Fun.TNotebook", background="#e3f2fd", tabmargins=[2, 5, 2, 0])
        style.configure("Fun.Horizontal.TProgressbar", troughcolor="#e3f2fd", background="#4a90e2", bordercolor="#fce4ec", lightcolor="#81d4fa", darkcolor="#1976d2", thickness=12)

    def _setup_preferences_ui(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        
        ttk.Label(parent, text="When duplicates are found:").grid(row=0, column=0, sticky="w", pady=(5,0))
        
        keep_frame = ttk.Frame(parent)
        keep_frame.grid(row=1, column=0, sticky="ew", padx=10)
        
        ttk.Radiobutton(
            keep_frame, 
            text="Keep Newest", 
            variable=self.keep_pref, 
            value="newest"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            keep_frame, 
            text="Keep Oldest", 
            variable=self.keep_pref, 
            value="oldest"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            keep_frame, 
            text="Keep Largest", 
            variable=self.keep_pref, 
            value="largest"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            keep_frame, 
            text="Keep Smallest", 
            variable=self.keep_pref, 
            value="smallest"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(parent, text="Deletion Method:").grid(row=2, column=0, sticky="w", pady=(10,0))
        
        del_frame = ttk.Frame(parent)
        del_frame.grid(row=3, column=0, sticky="ew", padx=10)
        
        ttk.Radiobutton(
            del_frame, 
            text="Move to Recycle Bin", 
            variable=self.del_method, 
            value="recycle"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            del_frame, 
            text="Permanent Delete", 
            variable=self.del_method, 
            value="permanent"
        ).pack(side=tk.LEFT, padx=5)

        # Size unit dropdown
        size_frame = ttk.Frame(parent)
        size_frame.grid(row=4, column=0, sticky="w", pady=(10,0))
        ttk.Label(size_frame, text="Size Unit:").pack(side=tk.LEFT)
        self.size_unit = ttk.Combobox(size_frame, values=['KB', 'MB', 'GB'], width=5, textvariable=self.size_unit_var)
        self.size_unit.pack(side=tk.LEFT)

    def _bind_preferences(self):
        self.keep_pref.trace_add('write', lambda *_: setattr(
            self.preferences, 'keep_preference', self.keep_pref.get()))
        
        self.del_method.trace_add('write', lambda *_: setattr(
            self.preferences, 'deletion_method', self.del_method.get()))
        
        self.size_unit_var.trace_add('write', lambda *_: setattr(
            self.preferences, 'size_unit', self.size_unit_var.get()))

    def _update_scoring_settings(self, enabled: bool, weights: Dict[str, float]):
        self.preferences.scoring_enabled = enabled
        self.preferences.score_weights = weights
        self.log_panel.log("Scoring settings updated", 'info')

    def _browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.log_panel.log(f"Selected folder: {folder}", 'info')
            self.status_var.set(f"Monitoring folder: {folder}")

    def _update_filters(self, filter_settings: Dict):
        self.file_filters = {
            'enabled': filter_settings['enabled'],
            'extensions': set(filter_settings['extensions']),
            'min_size': filter_settings['min_size'] * (1024 ** {'KB': 1, 'MB': 2, 'GB': 3}[filter_settings['unit']]),
            'max_size': filter_settings['max_size'] * (1024 ** {'KB': 1, 'MB': 2, 'GB': 3}[filter_settings['unit']])
        }
        self.log_panel.log(f"Filters updated - Extensions: {filter_settings['extensions']}, Size: {filter_settings['min_size']}-{filter_settings['max_size']} {filter_settings['unit']}", 'info')

    def _start_monitoring(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first 😅")
            return
            
        if not Path(folder).exists():
            messagebox.showerror("Error", "Selected folder does not exist 😢")
            return
            
        if not self._processing:
            self._processing = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.folder_entry.config(state='disabled')
            self.log_panel.clear()
            
            # Scan for available extensions
            try:
                extensions = FileAnalyzer.get_available_extensions(folder)
                self.filter_panel.update_extensions(list(extensions))
                self.filter_panel.enable_filters()
                self.log_panel.log(f"🔎 Found {len(extensions)} file extensions in folder", 'info')
            except Exception as e:
                self.log_panel.log(f"❌ Error scanning for extensions: {str(e)}", 'error')
            
            # Start file system monitoring
            handler = DebouncedEventHandler(self._handle_file_events)
            if not self.monitor.start(folder, handler):
                self.log_panel.log("⚠️ Monitoring is already running", 'warning')
                return
                
            self.log_panel.log(f"✅ Started monitoring: {folder}", 'success')
            self.status_var.set(f"Monitoring: {folder} 👀")
            self.progress.grid()
            self.progress.start(10)
            
            # Perform initial duplicate check
            Thread(target=self._initial_duplicate_check, daemon=True).start()

    def _initial_duplicate_check(self):
        """Perform immediate duplicate check when monitoring starts"""
        folder = self.folder_path.get()
        try:
            self.log_panel.log("🕵️ Performing initial duplicate scan...", 'info')
            duplicates = FileAnalyzer.find_duplicates(folder, self.file_filters)
            if duplicates:
                self.log_panel.log(f"🎯 Found {len(duplicates)} duplicate groups in initial scan", 'info')
                self._resolve_duplicates(duplicates)
            else:
                self.log_panel.log("🎉 No duplicates found in initial scan", 'info')
        except Exception as e:
            self.log_panel.log(f"💥 Error during initial scan: {str(e)}", 'error')
        finally:
            self._processing = False
            self.progress.stop()
            self.progress.grid_remove()

    def _handle_file_events(self, file_paths: List[str]):
        """Handle batch file events"""
        if not file_paths:
            return
            
        self.log_panel.log(f"🔔 Detected changes in {len(file_paths)} files", 'info')
        
        # Group by parent directory
        dir_groups = {}

        
        for path in file_paths:
            if not Path(path).exists():
                continue
                
            if self.file_filters['enabled'] and not FileAnalyzer._passes_filters(path, self.file_filters):
                self.log_panel.log(f"Ignored {os.path.basename(path)} (didn't pass filters)", 'debug')
                continue
            parent_dir = str(Path(path).parent)
            dir_groups.setdefault(parent_dir, []).append(path)
        
        # Process each directory group
        for parent_dir, files in dir_groups.items():
            try:
                duplicates = FileAnalyzer.find_duplicates(parent_dir, self.file_filters)
                if duplicates:
                    self.log_panel.log(f"Found {len(duplicates)} duplicate groups in {parent_dir}", 'info')
                    self._resolve_duplicates(duplicates)
                else:
                    self.log_panel.log(f"No duplicates found in {parent_dir}", 'debug')
            except Exception as e:
                self.log_panel.log(f"Error processing {parent_dir}: {str(e)}", 'error')

    def _resolve_duplicates(self, duplicates: Dict[str, List[str]]):
        """Handle duplicate resolution for multiple file types"""
        total_deleted = 0
        total_groups = len(duplicates)
        
        for file_hash, files in duplicates.items():
            try:
                if len(files) <= 1:
                    continue
                    
                self.log_panel.log(f"🤹 Processing {len(files)} duplicates for hash {file_hash[:8]}...", 'info')
                
                to_keep, to_delete = FileOperations.resolve_duplicates(
                    files,
                    self.preferences.keep_preference,
                    self.preferences.deletion_method,
                    self.preferences.scoring_enabled,
                    self.preferences.score_weights
                )
                
                self.log_panel.log(f"💾 Keeping: {os.path.basename(to_keep[0])}", 'success')
                
                for file in to_delete:
                    # Skip if file no longer exists
                    if not Path(file).exists():
                        continue
                        
                    # Special handling for OneDrive files
                    if "OneDrive" in file:
                        self.log_panel.log(f"☁️ Attempting to delete OneDrive file: {os.path.basename(file)}", 'warning')
                        
                    if FileOperations.safe_delete(file, self.preferences.deletion_method):
                        self.log_panel.log(f"🗑️ Deleted: {os.path.basename(file)}", 'info')
                        total_deleted += 1
                    else:
                        self.log_panel.log(f"🔒 Failed to delete: {os.path.basename(file)} (file may be locked)", 'error')
                        
            except Exception as e:
                self.log_panel.log(f"💥 Error processing duplicates: {str(e)}", 'error')
        
        self.log_panel.log(f"🏁 Duplicate resolution complete. Processed {total_groups} groups, deleted {total_deleted} files", 'info')

    def _stop_monitoring(self):
        if self.monitor.is_running():
            self.monitor.stop()
            self.log_panel.log("🛑 Monitoring stopped", 'info')
        if self._processing:
            self._processing = False
            self.log_panel.log("🧹 Scan stopped by user", 'info')
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.folder_entry.config(state='normal')
        self.status_var.set("Ready 🚀")
        self.progress.stop()
        self.progress.grid_remove()

    def hide_window(self):
        """Minimize to system tray"""
        self.withdraw()
        # Optionally notify via tray icon if supported

    def show_window(self):
        """Restore from system tray"""
        self.deiconify()
        self.lift()
        self.focus_force()

    def _on_close(self):
        self._stop_monitoring()
        if self.tray_icon:
            self.tray_icon.icon.stop()
        self.destroy()

    def _add_tooltip(self, widget, text):
        # Simple tooltip implementation
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, padding=(4,2))
        label.pack()
        def enter(event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()
        def leave(event):
            tooltip.withdraw()
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def _add_hover(self, widget):
        def on_enter(e):
            widget.configure(cursor="hand2")
        def on_leave(e):
            widget.configure(cursor="")
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _easter_egg(self, event):
        if not self.status_fun:
            self.status_var.set("You found the hidden folder fairy! 🧚‍♂️✨")
            self.status_fun = True
        else:
            self.status_var.set("Ready 🚀")
            self.status_fun = False

if __name__ == "__main__":
    app = SmartFolderMonitor()
    app.mainloop() 