import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime

class LogPanel(ttk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, text="Activity Log", *args, **kwargs)
        self.log_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, width=80, height=10, state='disabled',
            font=('Consolas', 10), padx=5, pady=5
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure tags for different log levels
        self.log_text.tag_config('info', foreground='black')
        self.log_text.tag_config('warning', foreground='orange')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('debug', foreground='gray')

    def log(self, message: str, level: str = 'info') -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] ", 'debug')
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)
        
        # Auto-scroll if at bottom
        self.log_text.see(tk.END)

    def clear(self):
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled') 