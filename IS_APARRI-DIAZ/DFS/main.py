import tkinter as tk
import time

layout = {
    # Campus Grounds
    "ENTRANCE": {"x": 230, "y": 400, "w": 80, "h": 30, "color": "gray"},
    "CANTEEN": {"x": 150, "y": 350, "w": 80, "h": 40, "color": "#789262"},
    "PARKING": {"x": 150, "y": 250, "w": 80, "h": 40, "color": "#f57c00"},
    "FIELD": {"x": 300, "y": 350, "w": 80, "h": 40, "color": "#388e3c"},
    "CASHIER": {"x": 150, "y": 150, "w": 80, "h": 40, "color": "#5c1f1f"},
    "AC": {"x": 300, "y": 150, "w": 80, "h": 40, "color": "#4d882d"},

    # College Building (CB Ground)
    "C101": {"x": 200, "y": 100, "w": 60, "h": 40, "color": "#2196f3"},
    "C102": {"x": 260, "y": 100, "w": 60, "h": 40, "color": "#2196f3"},
    "C103": {"x": 320, "y": 100, "w": 60, "h": 40, "color": "#2196f3"},
    "C104": {"x": 380, "y": 100, "w": 60, "h": 40, "color": "#2196f3"},
    "C105": {"x": 440, "y": 100, "w": 60, "h": 40, "color": "#2196f3"},
    "C106": {"x": 500, "y": 100, "w": 60, "h": 40, "color": "#2196f3"},
    "C107": {"x": 560, "y": 100, "w": 60, "h": 40, "color": "#2196f3"},
    "C_ADMIN": {"x": 620, "y": 100, "w": 120, "h": 40, "color": "#1976d2"},

    # CB 2nd Floor
    "C201": {"x": 200, "y": 50, "w": 60, "h": 40, "color": "#64b5f6"},
    "C202": {"x": 260, "y": 50, "w": 60, "h": 40, "color": "#64b5f6"},
    "C203": {"x": 320, "y": 50, "w": 60, "h": 40, "color": "#64b5f6"},
    "C204": {"x": 380, "y": 50, "w": 60, "h": 40, "color": "#64b5f6"},
    "C205": {"x": 440, "y": 50, "w": 60, "h": 40, "color": "#64b5f6"},
    "C206": {"x": 500, "y": 50, "w": 60, "h": 40, "color": "#64b5f6"},
    "C207": {"x": 560, "y": 50, "w": 60, "h": 40, "color": "#64b5f6"},
    "C208": {"x": 620, "y": 50, "w": 60, "h": 40, "color": "#64b5f6"},

    # CB 3rd Floor
    "MiniHotel": {"x": 200, "y": 0, "w": 60, "h": 30, "color": "#bbdefb"},
    "Library": {"x": 260, "y": 0, "w": 60, "h": 30, "color": "#bbdefb"},
    "SpeechLab": {"x": 320, "y": 0, "w": 60, "h": 30, "color": "#bbdefb"},
    "Auditorium": {"x": 380, "y": 0, "w": 80, "h": 30, "color": "#bbdefb"},

    # SHS Ground Floor
    "SHS101": {"x": 450, "y": 400, "w": 40, "h": 40, "color": "#f48fb1"},
    "SHS102": {"x": 500, "y": 400, "w": 40, "h": 40, "color": "#f48fb1"},
    "SHS103": {"x": 550, "y": 400, "w": 40, "h": 40, "color": "#f48fb1"},
    "SHS104": {"x": 600, "y": 400, "w": 40, "h": 40, "color": "#f48fb1"},
    "SHS_GUIDANCE": {"x": 650, "y": 400, "w": 80, "h": 40, "color": "#f8bbd0"},
    "SHS_AC": {"x": 740, "y": 400, "w": 60, "h": 40, "color": "#f8bbd0"},
    "SHS_EXIT": {"x": 810, "y": 400, "w": 60, "h": 40, "color": "gray"},

    # SHS 2nd Floor
    "SHS201": {"x": 450, "y": 350, "w": 40, "h": 40, "color": "#f06292"},
    "SHS202": {"x": 500, "y": 350, "w": 40, "h": 40, "color": "#f06292"},
    "SHS203": {"x": 550, "y": 350, "w": 40, "h": 40, "color": "#f06292"},
    "SHS204": {"x": 600, "y": 350, "w": 40, "h": 40, "color": "#f06292"},
    "SHS205": {"x": 650, "y": 350, "w": 40, "h": 40, "color": "#f06292"},
    "SHS206_A": {"x": 700, "y": 350, "w": 40, "h": 40, "color": "#f06292"},
    "SHS206_B": {"x": 750, "y": 350, "w": 40, "h": 40, "color": "#f06292"},
    "GYM": {"x": 750, "y": 280, "w": 80, "h": 40, "color": "#81d4fa"},

    # SHS Back Ground Floor
    "SHS105": {"x": 450, "y": 450, "w": 40, "h": 40, "color": "#f8bbd0"},
    "SHS106": {"x": 500, "y": 450, "w": 40, "h": 40, "color": "#f8bbd0"},
    "SHS107": {"x": 550, "y": 450, "w": 40, "h": 40, "color": "#f8bbd0"}
}


graph = {
    "ENTRANCE": ["CANTEEN", "PARKING","CASHIER"],
    "CANTEEN": ["FIELD"],
    "PARKING": ["FIELD"],
    "FIELD": ["AC"],
    "AC": ["C101", "SHS101"],


    # College Building Path
    "C101": ["C102"], "C102": ["C103"], "C103": ["C104"], "C104": ["C105"],
    "C105": ["C106"], "C106": ["C107"], "C107": ["C201"],
    "C201": ["C202"], "C202": ["C203"], "C203": ["C204"], "C204": ["C205"],
    "C205": ["C206"], "C206": ["C207"], "C207": ["C208"],
    "C208": ["MiniHotel"], "MiniHotel": ["Library"], "Library": ["SpeechLab"], "SpeechLab": ["Auditorium"],

    # SHS Ground to 2nd floor
    "SHS101": ["SHS102", "SHS105"],  
    "SHS102": ["SHS103"],
    "SHS103": ["SHS104"],
    "SHS104": ["SHS201", "SHS_GUIDANCE"],

    # SHS Back Ground Floor
    "SHS105": ["SHS106"],
    "SHS106": ["SHS107"],

    # SHS 2nd Floor
    "SHS201": ["SHS202"],
    "SHS202": ["SHS203"],
    "SHS203": ["SHS204"],
    "SHS204": ["SHS205"],
    "SHS205": ["SHS206_A"],
    "SHS206_A": ["SHS206_B"],
    "SHS206_B": ["GYM"],

    # SHS Exit Path
    "SHS_GUIDANCE": ["SHS_AC"],
    "SHS_AC": ["SHS_EXIT"]
}

# DFS Algorithm
def dfs_path(graph, start, goal, path=None, visited=None):
    if path is None: path = []
    if visited is None: visited = set()
    path.append(start)
    visited.add(start)
    if start == goal:
        return path
    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            result = dfs_path(graph, neighbor, goal, path.copy(), visited.copy())
            if result:
                return result
    return None

root = tk.Tk()
root.title("School Map Graph UI")
canvas = tk.Canvas(root, width=1000, height=600, bg="black")
canvas.pack()

def draw_nodes():
    for label, props in layout.items():
        x, y, w, h = props['x'], props['y'], props['w'], props['h']
        color = props['color']
        canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline="white")
        canvas.create_text(x + w / 2, y + h / 2, text=label, fill="black")

def draw_path(path):
    for i in range(len(path) - 1):
        a = layout[path[i]]
        b = layout[path[i+1]]
        x1 = a['x'] + a['w'] // 2
        y1 = a['y'] + a['h'] // 2
        x2 = b['x'] + b['w'] // 2
        y2 = b['y'] + b['h'] // 2
        canvas.create_line(x1, y1, x2, y2, fill="yellow", width=3)
        canvas.update()
        time.sleep(0.3)

selected_building = tk.StringVar()
options = list(layout.keys())
selected_building.set("C107")
menu = tk.OptionMenu(root, selected_building, *options)
menu.pack()

def on_find_path():
    canvas.delete("all")
    draw_nodes()
    goal = selected_building.get()
    path = dfs_path(graph, "ENTRANCE", goal)
    if path:
        draw_path(path)
    else:
        print("No path found.")

btn = tk.Button(root, text="Find Path", command=on_find_path)
btn.pack()

draw_nodes()
root.mainloop()
