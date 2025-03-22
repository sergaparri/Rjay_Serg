from abc import ABC, abstractmethod

class Customer:
    def __init__(self, name, budget, is_senior=False, is_pwd=False):
        self.name = name
        self.budget = budget
        self.is_senior = is_senior
        self.is_pwd = is_pwd
        self.orders = None

    def is_discount_eligible(self):
        return True if self.is_senior or self.is_pwd else False
    
    def get_order(self):
        return self.orders
    
    def get_budget(self):
        return self.budget
    
    def set_budget(self, budget):
        self.budget += budget
    
class PointOfSale:
    def __init_(self):
        self.receipt = Receipt()

    def get_total_orders(self, customer):
        return customer.get_order()
    
    def get_order_total_cost(self, customer):
        total_cost += [item['cost'] for item in self.get_total_order(customer)]
        return total_cost
    
    def get_order_total_retail(self, customer):
        total_retail += [item['retail'] for item in self.get_total_order(customer)]
        return                         
    
    def check_out(self, customer):
        if customer.budget >= self.get_order_total_retail(customer):
            
class Store:
    def __init__(self, name, address):
        self.name = name
        self.address = address
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name

    def set_address(self, address):
        self.address = address

    def get_address(self):
        return self.address
    
    def setaddress(self, address):
        self.address = address
        

class Receipt:
    receipt_num = 0
    def __init__(self, orders, customer):
        self.orders = orders
        self.customer = customer
        self.store = Store()
        self.receipt_num = Receipt.receipt_num + 1
        Receipt.receipt_num += 1

    def get_orders(self):
        return self.orders
    
    def get_customer(self):
        return self.customer
    
    def get_store_info(self):
        return self.store
    
#STRATEGY
class Discount(ABC):
    @abstractmethod    
    def __init__(self):
        self.discount_amt = .20
    
    @abstractmethod
    def apply(self, customer):
        pass

class SeniorDiscount(Discount):
    def __init__(self):
        super().__init__(self)

    def apply(self, customer, customer_cart):
        if customer.orders == None:
            return 'Orders are Empty'
        

class PWDDiscount(Discount):
    pass

