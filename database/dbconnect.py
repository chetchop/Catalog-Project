from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
#DO YOU REALLY NEED TO IMPORT ALL EXC
from sqlalchemy import exc
from database_setup import Base, user, category, categoryItem

class DBConnect:
    def __init__(self):
        engine = create_engine('sqlite:///database/catalog.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def getAllCategories(self):
        return self.session.query(category).all()

    def getAllItems(self):
        return self.session.query(categoryItem).all()
        
    def getAllRecentItems(self):
        recentItems = []
        allCategories = self.getAllCategories()
        for c in allCategories:
            item = self.session.query(categoryItem).filter_by(category_id=c.id).\
            order_by(desc(categoryItem.id)).first()
            if item:
                recentItems.append(item)
        return recentItems


    def addCategory(self, name, userID):
        newCategory = category(name=name, user_id=userID)
        self.session.add(newCategory)
        self.session.commit()


    def addItem(self, name, description, categoryID, userID):
        newItem= categoryItem(name=name, description=description, category_id=categoryID, user_id=userID)
        self.session.add(newItem)
        self.session.commit()


    def getCategory(self, categoryID):
        return self.session.query(category).filter_by(id=categoryID).one()


    def getItemsByCategory(self, categoryName):
        categoryID = self.getCategoryByName(categoryName)
        return self.session.query(categoryItem).filter_by(category_id=categoryID.id).all()


    def getCategoryByName(self, categoryName):
        return self.session.query(category).filter_by(name=categoryName).one()


    def getItemCountByCategory(self, categoryName):
        categoryID = self.getCategoryByName(categoryName)
        return self.session.query(categoryItem).filter_by(category_id=categoryID.id).count()


    def getItemByName(self, itemName):
        return self.session.query(categoryItem).filter_by(name=itemName).one()


    def editItem(self, item, name, description, categoryID):
        item.name = name
        item.description = description
        item.category_id = categoryID
        self.session.add(item)
        self.session.commit()


    def deleteItem(self, item):
        self.session.delete(item)
        self.session.commit()

    def categoryNameUsed(self, categoryName):
        result = False
        categories = self.session.query(category).all()
        if categories:
            for c in categories:
                if c.name.lower() == categoryName.lower():
                    result = True
        return result

    def itemNameUsed(self, itemName):
        result = {'used': False, 'category': ''}
        items = self.session.query(categoryItem).all()
        if items:
            for i in items:
                if i.name.lower() == itemName.lower():
                    result['used'] = True
                    result['category'] = i.category.name
        return result

    def createUser(self, username, email, picture):
        newUser = user(name=username, email=email, picture=picture)
        self.session.add(newUser)
        self.session.commit()

    def getUserByID(self, ID):
        return self.session.query(user).filter_by(id=ID).one()

    def getUserIDByEmail(self, email):
        try:
            foundUser = self.session.query(user).filter_by(email=email).one()
            return foundUser.id
        except:
            return None







