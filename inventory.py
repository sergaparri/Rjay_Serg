from abc import ABC, abstractmethod
import json
              
class Stock(ABC):
    @abstractmethod
    def __init__(self, name, qty, cost, retail):
        self.name = name
        self.qty = qty
        self.cost = cost
        self.retail = retail

class Ingredient(Stock):
    def __init__(self, name, qty, cost,retail):
        super().__init__(name, qty, cost, retail)
        self.type = 'Ingredient'   

class Beverage(Stock):
    def __init__(self, name, qty, cost, retail):
        super().__init__(name, qty, cost, retail)
        self.type = 'Beverage'
                   
class Supply(Stock):
    def __init__(self, name, qty, cost, retail):
        super().__init__(name, qty, cost, retail)
        self.type = 'Supply'
         

class Factory(ABC):
    @abstractmethod
    def create_stock(self, type, name, qty, cost, retail):
       pass
       
    
class StockFactory(Factory):
    def __init__(self):
        pass
    
    def create_stock(self, type, name, qty, cost, retail=0):
        if type.lower() == "ingredient":
            return Ingredient(name, qty, cost, retail)
        elif type.lower() == "beverage":
            return Beverage(name, qty, cost, retail) 
        elif type.lower() == "supply":
            return Supply(name, qty, cost, retail)
        else:
            return 'Stock Type Not Found'

class Inventory:
    def __init__(self):
        self.stocks = self.load_stocks()
        self.stock_creator = StockFactory()
        
    def load_stocks(self):
        with open('stocks.json', 'r') as file:
            return json.load(file)
    
    def update_inventory(self):
        with open('stocks.json', 'w') as file:
            json.dump(self.stocks, file)
        return 'Succesfully Updated'
    
    def show_inventory(self):
        return self.stocks

    def stock_unit_validator(self, unit, qty):
        if unit == 'g' or unit == 'grams':
            return qty
        elif unit == 'kg' or unit == 'kilograms':
            return qty * 1000
        else:
            return 'Please Input valid Unit'
        
    def add_stocks(self,type, name, qty, cost, unit, retail=0):
        new_qty = self.stock_unit_validator(unit, qty)
        if isinstance(qty, str): #check unit
            return qty
        new_stock = self.stock_creator.create_stock(type, name, qty, cost, retail)
        if isinstance(new_stock, str): #check type
            return new_stock
        data = vars(new_stock).copy()
        del data["name"]
        self.stocks[type][name] = data
        self.update_inventory()
        return f'{name} added succesfully'
        

if __name__ == "__main__":
    inv = Inventory()
    print(inv.show_inventory())
    
    print(inv.add_stocks('beverage', 'coca-cola', 20, 15, 25))
    
    print(inv.show_inventory())
    
    
    
