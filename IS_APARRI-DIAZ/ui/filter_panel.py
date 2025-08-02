import tkinter as tk
from tkinter import ttk
from typing import Callable, List

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