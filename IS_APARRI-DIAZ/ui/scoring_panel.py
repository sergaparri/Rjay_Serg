import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict

class ScoringSettingsPanel(ttk.LabelFrame):
    def __init__(self, parent, update_callback: Callable, *args, **kwargs):
        super().__init__(parent, text="Scoring Settings", *args, **kwargs)
        self.update_callback = update_callback
        self._setup_ui()

    def _setup_ui(self):
        self.scoring_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self,
            text="Enable Smart Scoring",
            variable=self.scoring_enabled,
            command=self._update_scoring
        ).pack(anchor=tk.W, pady=5)

        # Weight sliders
        self.weights = {
            'recency': tk.DoubleVar(value=0.3),
            'size': tk.DoubleVar(value=0.2),
            'location': tk.DoubleVar(value=0.2),
            'extension': tk.DoubleVar(value=0.1),
            'name': tk.DoubleVar(value=0.2)
        }

        ttk.Label(self, text="Score Weights:").pack(anchor=tk.W, pady=(5,0))
        
        for factor, var in self.weights.items():
            frame = ttk.Frame(self)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=factor.capitalize() + ":", width=10).pack(side=tk.LEFT)
            ttk.Scale(
                frame,
                from_=0,
                to=1,
                variable=var,
                command=lambda v, f=factor: self._update_weight(f, float(v))
            ).pack(side=tk.LEFT, expand=True, fill=tk.X)
            ttk.Label(frame, textvariable=var, width=4).pack(side=tk.LEFT)

    def _update_weight(self, factor: str, value: float):
        self.weights[factor].set(round(value, 2))
        self._update_scoring()

    def _update_scoring(self):
        weights = {k: v.get() for k, v in self.weights.items()}
        self.update_callback(self.scoring_enabled.get(), weights) 