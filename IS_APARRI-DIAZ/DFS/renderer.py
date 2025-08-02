import tkinter as tk
import time

class MapRenderer:
    def __init__(self, canvas):
        self.canvas = canvas
    
    def draw_nodes(self, layout):
        for label, props in layout.items():
            x, y, w, h = props['x'], props['y'], props['w'], props['h']
            color = props['color']
            
            self.canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline="white")
            self.canvas.create_text(x + w / 2, y + h / 2, text=label, fill="black")
    
    def draw_path(self, path, layout, delay=0.3):
        for i in range(len(path) - 1):
            a = layout[path[i]]
            b = layout[path[i+1]]
            
            x1 = a['x'] + a['w'] // 2
            y1 = a['y'] + a['h'] // 2
            x2 = b['x'] + b['w'] // 2
            y2 = b['y'] + b['h'] // 2
            
            self.canvas.create_line(x1, y1, x2, y2, fill="yellow", width=3)
            
            self.canvas.update()
            time.sleep(delay)
    
    def clear_canvas(self):
        self.canvas.delete("all") 