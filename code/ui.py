import customtkinter as ctk
from tkinter import messagebox

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

inventory = {
    "Margherita": 10,
    "Pepperoni": 10,
    "BBQ Chicken": 10,
    "Hawaiian": 10,
    "Veggie": 10
}

class PointOfSaleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Point of Sale System")
        self.geometry("800x500")
        ctk.set_appearance_mode("light")

        # Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # Main Frame
        self.main_frame = ctk.CTkFrame(self, width=600)
        self.main_frame.pack(side="right", fill="both", expand=True)

        # Sidebar Buttons
        self.admin_btn = ctk.CTkButton(self.sidebar, text="Admin", command=self.show_admin_login)
        self.admin_btn.pack(pady=10, padx=10)

        self.pos_btn = ctk.CTkButton(self.sidebar, text="Point of Sale", command=self.show_pos_page)
        self.pos_btn.pack(pady=10, padx=10)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # Admin Login Page
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

    # Admin Panel
    def show_admin_panel(self):
        self.clear_main_frame()

        ctk.CTkLabel(self.main_frame, text="Admin Panel", font=("Arial", 16)).pack(pady=10)

        ctk.CTkButton(self.main_frame, text="Inventory", command=self.show_inventory).pack(pady=5)

    # Inventory Page
    def show_inventory(self):
        self.clear_main_frame()

        ctk.CTkLabel(self.main_frame, text="Inventory", font=("Arial", 16)).pack(pady=10)

        # Add Product Section
        ctk.CTkLabel(self.main_frame, text="Add New Product").pack(pady=5)
        name_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Product Name")
        name_entry.pack(pady=5)
        quantity_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Quantity")
        quantity_entry.pack(pady=5)

        def add_product():
            name = name_entry.get().strip()
            quantity = quantity_entry.get().strip()
            if name and quantity.isdigit():
                inventory[name] = int(quantity)
                self.show_inventory()
            else:
                messagebox.showerror("Error", "Invalid product name or quantity")

        ctk.CTkButton(self.main_frame, text="Add Product", command=add_product).pack(pady=5)

        for item, quantity in list(inventory.items()):
            frame = ctk.CTkFrame(self.main_frame)
            frame.pack(pady=5, padx=10, fill="x")

            ctk.CTkLabel(frame, text=f"{item} - Quantity: {quantity}").pack(side="left", padx=10)
            
            def increase_quantity(pizza=item):
                inventory[pizza] += 1
                self.show_inventory()
            
            def decrease_quantity(pizza=item):
                if inventory[pizza] > 0:
                    inventory[pizza] -= 1
                self.show_inventory()
            
            def delete_product(pizza=item):
                del inventory[pizza]
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
