import customtkinter as ctk
from tkinter import messagebox, Scrollbar, Canvas, Frame
import json

ADMIN_USERNAME = "serg"
ADMIN_PASSWORD = "123"

INVENTORY_FILE = "inventory.json"

def load_inventory():
    try:
        with open(INVENTORY_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "Margherita": 10,
            "Pepperoni": 10,
            "BBQ Chicken": 10,
            "Hawaiian": 10,
            "Veggie": 10
        }

def save_inventory():
    with open(INVENTORY_FILE, "w") as file:
        json.dump(inventory, file, indent=4)

def insertion_sort(items):
    sorted_items = list(items.items())
    for i in range(1, len(sorted_items)):
        key = sorted_items[i]
        j = i - 1
        while j >= 0 and sorted_items[j][0] > key[0]:
            sorted_items[j + 1] = sorted_items[j]
            j -= 1
        sorted_items[j + 1] = key
    return dict(sorted_items)

inventory = load_inventory()

class PointOfSaleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Point of Sale System")
        self.geometry("600x500")
        ctk.set_appearance_mode("light")

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="black")
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, fg_color='black', text="PIZZAAA", font=("Arial", 40)).pack(pady=50)

        self.main_frame = ctk.CTkFrame(self, width=600, fg_color="orange")
        self.main_frame.pack(side="right", fill="both", expand=True)

        self.admin_btn = ctk.CTkButton(self.sidebar, text="Admin", command=self.show_admin_login)
        self.admin_btn.pack(pady=10, padx=50)

        self.pos_btn = ctk.CTkButton(self.sidebar, text="Point of Sale", command=self.show_pos_page, fg_color="green")
        self.pos_btn.pack(pady=10, padx=50)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_admin_login(self):
        self.clear_main_frame()

        ctk.CTkLabel(self.main_frame, text="Admin Login", font=("Arial", 16)).pack(pady=10)

        username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Username")
        username_entry.pack(pady=5)

        password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*")
        password_entry.pack(pady=5)

        def login():
            if username_entry.get() == ADMIN_USERNAME and password_entry.get() == ADMIN_PASSWORD:
                self.show_admin_panel()
            else:
                messagebox.showerror("Error", "Invalid Credentials")

        login_btn = ctk.CTkButton(self.main_frame, text="Login", command=login)
        login_btn.pack(pady=10)

    def show_admin_panel(self):
        self.clear_main_frame()

        ctk.CTkLabel(self.main_frame, text="Admin Panel", font=("Arial", 16)).pack(pady=10)

        ctk.CTkButton(self.main_frame, text="Inventory", command=self.show_inventory).pack(pady=5)

    def show_inventory(self):
        self.clear_main_frame()

        ctk.CTkLabel(self.main_frame, text="Inventory", font=("Arial", 16)).pack(pady=10)

        canvas = Canvas(self.main_frame)
        scrollbar = Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ctk.CTkLabel(scrollable_frame, text="Add New Product").pack(pady=5)
        name_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Product Name")
        name_entry.pack(pady=5)
        quantity_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Quantity")
        quantity_entry.pack(pady=5)

        def add_product():
            name = name_entry.get().strip()
            quantity = quantity_entry.get().strip()
            if name and quantity.isdigit():
                inventory[name] = int(quantity)
                save_inventory()
                self.show_inventory()
            else:
                messagebox.showerror("Error", "Invalid product name or quantity")

        ctk.CTkButton(scrollable_frame, text="Add Product", command=add_product).pack(pady=5)

        global inventory
        inventory = insertion_sort(inventory)
        save_inventory()
        
        for item, quantity in inventory.items():
            frame = ctk.CTkFrame(scrollable_frame)
            frame.pack(pady=5, padx=10, fill="x")

            ctk.CTkLabel(frame, text=f"{item} - Quantity: {quantity}").pack(side="left", padx=10)
            
            def increase_quantity(pizza=item):
                inventory[pizza] += 1
                save_inventory()
                self.show_inventory()
            
            def decrease_quantity(pizza=item):
                if inventory[pizza] > 0:
                    inventory[pizza] -= 1
                save_inventory()
                self.show_inventory()
            
            def delete_product(pizza=item):
                del inventory[pizza]
                save_inventory()
                self.show_inventory()

            ctk.CTkButton(frame, text="+", width=30, command=increase_quantity).pack(side="right", padx=5)
            ctk.CTkButton(frame, text="-", width=30, command=decrease_quantity).pack(side="right", padx=5)
            ctk.CTkButton(frame, text="Delete", width=50, fg_color="red", command=delete_product).pack(side="right", padx=5)

    def show_pos_page(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Point of Sale", font=("Arial", 16)).pack(pady=10)

if __name__ == "__main__":
    app = PointOfSaleApp()
    app.mainloop()
