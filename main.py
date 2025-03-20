from abc import ABC, abstractmethod

#CREATIONAL, ABSTRACT-FACTORY
class Account(ABC):
    users = 0
    @abstractmethod
    def __init__(self, name, password):
        self.name = name 
        self.password = password
        self.user_num = Account.users + 1
        Account.users = self.user_num
    
class User(Account):
    def __init__(self, name, password):
        super().__init__(name, password)
    
class Admin(Account):
    def __init__(self, name, password):
        super().__init__(name, password)
    
    def create_account(self, type, name, password):
        creator = AccountFactory()
        if type.lower() == 'user':
            return creator.createUserAccount(name, password)
        elif type.lower() == 'admin':
            return creator.createAdminAccount(name, password)
        else:
            return 'Please Input Valid Account Type'

class Factory(ABC):
    @abstractmethod
    def createUserAccount(self):
        pass
    
    @abstractmethod
    def createAdminAccount(self):
        pass
    
class AccountFactory(Factory):
    def createUserAccount(self, name, password):
        return User(name, password)
    
    def createAdminAccount(self,name, password):
        return Admin(name, password)


if __name__ == "__main__":
    creator = AccountFactory()
    admin1 = creator.createAdminAccount('rj', '123')
    
    admin1.create_account('user', 'rj', '123')
