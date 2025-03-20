from abc import ABC, abstractmethod
import json

class Pizza(ABC):
    @abstractmethod
    def __init__(self, name, size, cost, retail, ingredients = []):
        self.name = name
        self.size = size
        self.cost = cost + (10 * (size - 1))
        self.retail = retail + (10 * (size  - 1))
        self.ingredients = ingredients
    
    def set_retail(self):
        return self.retail 
    
class HamAndCheesePizza(ABC):
    def __init__(self, name, size, cost, retail):
        super().__init__(name, size, cost, retail)
        self.ingredients = self.ingredient()

    def ingredient(self):
        ingredient = {"flour" : 500, "yeast" : 7, "salt"  : 10, "olive-oil" : .10, "tomato-sauce" : .30, "cheese" : 250, "ham" : 150}
        return ingredient

class PepperoniPizza(ABC):
    def __init__(self, name, size, cost, retail):
        super().__init__(name, size, cost, retail)
        self.ingredients = self.ingredient()

    def ingredient(self):
        ingredient = {"flour" : 500, "yeast" : 7, "salt"  : 10, "olive-oil" : .10, "tomato-sauce" : .30, "cheese" : 250, "ham" : 150, "oregano" : .5, "pepper" : 10, }
        return ingredient

class VePizza(ABC):
    def __init__(self, name, size, cost, retail):
        super().__init__(name, size, cost, retail)
        self.ingredients = self.ingredient()

    def ingredient(self):
        ingredient = {"flour" : 500, "yeast" : 7, "salt"  : 10, "olive-oil" : .10, "tomato-sauce" : .30, "cheese" : 250, "ham" : 150}
        return ingredient
              
class Stock:
    @abstractmethod
    def __init__(self, name, qty, cost, retail,unit):
        self.name = name
        self.qty = qty
        self.cost = cost
        self.retail = retail

class Ingredient(Stock):
    def __init__(self, name, qty, cost):
        super().__init__(name, qty, cost)
        self.type = 'Ingredient'   

class Beverage(Stock):
    def __init__(self, name, qty, cost, retail):
        super().__init__(name, qty, cost, retail)
        self.type = 'Beverage'
                   
class Supply(Stock):
    def __init__(self, name, qty, cost):
        super().__init__(name, qty, cost)
        self.type = 'Supply'
         

class Factory(ABC):
    @abstractmethod
    def create_stock(self, type, name, qty, cost, retail):
       pass
       
       
class StockFactory(ABC):
    def create_stock(self, type, name, qty, cost, retail): #unit
        if type == "Ingredient":
            return Ingredient(name, qty, cost, retail)
        elif type == "Beverage":
            return Beverage(name, qty, cost, retail) 
        elif type == "Supply":
            return Supply(name, qty, cost, retail)
        else:
            return 'Stock Type Not Found'

class Inventory:
    def __init__(self):
        self.stocks = self.stocks()     
        
    def stocks(self):
        with open('stocks.json', 'r') as file:
            return json.load(file)
    
    def update_inventory(self):
        with open('stocks.json', 'w') as file:
            json.dump(self.stocks, file)
        return 'Succesfully Updated'
    
    def show_inventory(self):
        return self.stocks

    def add_stocks(self,stock):
        self.stocks[stock.type][stock.name]['qty'] = stock.qty
        self.stocks[stock.type][stock.name]['qty'] = stock.cost
        if self.stocks.retail:
            self.stocks[stock.type][stock.name]['retail'] = stock.retail
        return self.update_inventory()
        

