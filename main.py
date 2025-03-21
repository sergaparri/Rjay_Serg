from abc import ABC, abstractmethod
import json
import os 

#CREATIONAL, ABSTRACT-FACTORY
class Account(ABC):
    users = 0
    @abstractmethod
    def __init__(self, name, password):
        self.name = name 
        self.password = password
        user_num = Account.users + 1
        self.user_num = str(user_num).zfill(3)
        Account.users += 1
        
    
class User(Account):
    def __init__(self, name, password):
        super().__init__(name, password)
        
    
class Admin(Account):
    
    def __init__(self, name, password):
        super().__init__(name, password)
        self.accounts = self.load_accts()
        
    def create_account(self, acc_type, name, password):
        creator = AccountFactory()
        acc_type = acc_type.lower()
        if acc_type == 'user':
            new_acc = creator.create_user_account(name, password)
        elif acc_type == 'admin':
            new_acc = creator.create_admin_account(name, password)
        else:
            return 'Please Input Valid Account Type'
        
        if acc_type not in self.accounts:
            self.accounts[acc_type] = {}
        
        data = vars(new_acc).copy()
        if 'accounts' in data:
            del data['accounts']
        
        user_number = data.pop("user_num")
        self.accounts[acc_type][user_number] = data
        self.update_accts()
        
        return 'Account Succesfully Added'
        
            
    def load_accts(self): 
        if not os.path.exists('accounts.json'):
            return {}
        
        with open('accounts.json', 'r') as file:
            try:
                return json.load(file)
            except:
                return {}
            
    def update_accts(self): 
        with open('accounts.json', 'w') as file:
            json.dump(self.accounts, file)
        return 'Succesfully Saved'

class Factory(ABC):
    
    @abstractmethod
    def create_user_account(self):
        pass
    
    @abstractmethod
    def create_admin_account(self):
        pass
    
class AccountFactory(Factory):
    def create_user_account(self, name, password):
        return User(name, password)
    
    def create_admin_account(self,name, password):
        return Admin(name, password)


if __name__ == "__main__":
    creator = AccountFactory()
    admin1 = creator.create_admin_account('rj', '123')

    
    print(admin1.create_account('user', 'rj', '123'))
    print(admin1.create_account('user', 'rjf', '123'))
    
    
    print(admin1.create_account('admin', 'Serg', '123'))
    print(admin1.accounts)
