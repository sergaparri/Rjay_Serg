import tkinter as tk
from renderer import MapRenderer
from algorithms import dfs_path

class SchoolMapUI:
    def __init__(self, root, layout, graph):
        self.root = root
        self.layout = layout
        self.graph = graph
        
        self.root.title("School Map Graph UI")
        
        self.canvas = tk.Canvas(root, width=1000, height=600, bg="black")
        self.canvas.pack()
        
        self.renderer = MapRenderer(self.canvas)
        
        self._create_controls()
        
        self.renderer.draw_nodes(self.layout)
    
    def _create_controls(self):
        self.selected_building = tk.StringVar()
        options = list(self.layout.keys())
        self.selected_building.set("C107")
        
        self.menu = tk.OptionMenu(self.root, self.selected_building, *options)
        self.menu.pack()
        
        self.btn = tk.Button(self.root, text="Find Path", command=self._on_find_path)
        self.btn.pack()
    
    def _on_find_path(self):
        self.renderer.clear_canvas()
        self.renderer.draw_nodes(self.layout)
        
        goal = self.selected_building.get()
        
        path = dfs_path(self.graph, "ENTRANCE", goal)
        
        if path:
            self.renderer.draw_path(path, self.layout)
        else:
            print("No path found.")
    
    def run(self):
        self.root.mainloop() 