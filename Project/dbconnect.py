#!/usr/bin/env python3
#
# Database connection object

# Imports
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, user, category, categoryItem


# Class definition
class DBConnect:
    def __init__(self):
        engine = create_engine('sqlite:///catalog.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    # Returns all Categories
    def getAllCategories(self):
        return self.session.query(category).all()

    # Returns all items
    def getAllItems(self):
        return self.session.query(categoryItem).all()

    # Returns last added item in each category
    def getAllRecentItems(self):
        recentItems = []
        allCategories = self.getAllCategories()
        for c in allCategories:
            item = self.session.query(categoryItem)\
                                      .filter_by(category_id=c.id)\
                                      .order_by(desc(categoryItem.id)).first()
            if item:
                recentItems.append(item)
        return recentItems

    # Add in a new category
    def addCategory(self, name, userID):
        newCategory = category(name=name, user_id=userID)
        self.session.add(newCategory)
        self.session.commit()

    # Add in a new item
    def addItem(self, name, description, categoryID, userID):
        newItem = categoryItem(name=name,
                               description=description,
                               category_id=categoryID,
                               user_id=userID)
        self.session.add(newItem)
        self.session.commit()

    # Returns a category given an ID
    def getCategory(self, categoryID):
        return self.session.query(category).filter_by(id=categoryID).one()

    # Returns items in a given category
    def getItemsByCategory(self, categoryName):
        categoryID = self.getCategoryByName(categoryName)
        item = self.session.query(categoryItem)\
                           .filter_by(category_id=categoryID.id)\
                           .all()
        return item

    # Returns a category by name
    def getCategoryByName(self, categoryName):
        return self.session.query(category).filter_by(name=categoryName).one()

    # Returns the number of items in given category
    def getItemCountByCategory(self, categoryName):
        categoryID = self.getCategoryByName(categoryName)
        return self.session.query(categoryItem)\
                           .filter_by(category_id=categoryID.id)\
                           .count()

    # Returns an item given a name
    def getItemByName(self, itemName):
        return self.session.query(categoryItem).filter_by(name=itemName).one()

    # Edits an item
    def editItem(self, item, name, description, categoryID):
        item.name = name
        item.description = description
        item.category_id = categoryID
        self.session.add(item)
        self.session.commit()

    # Deletes an item
    def deleteItem(self, item):
        self.session.delete(item)
        self.session.commit()

    # Determines if category name is already being used
    def categoryNameUsed(self, categoryName):
        result = False
        categories = self.session.query(category).all()
        if categories:
            for c in categories:
                if c.name.lower() == categoryName.lower():
                    result = True
        return result

    # Determines if item name is already being used
    def itemNameUsed(self, itemName):
        result = {'used': False, 'category': ''}
        items = self.session.query(categoryItem).all()
        if items:
            for i in items:
                if i.name.lower() == itemName.lower():
                    result['used'] = True
                    result['category'] = i.category.name
        return result

    # Create a new user
    def createUser(self, username, email, picture):
        newUser = user(name=username, email=email, picture=picture)
        self.session.add(newUser)
        self.session.commit()

    # Returns a user given a id
    def getUserByID(self, ID):
        try:
            return self.session.query(user).filter_by(id=ID).one()
        except NoResultFound:
            return None

    # Returns a user given an email address
    def getUserIDByEmail(self, email):
        try:
            foundUser = self.session.query(user).filter_by(email=email).one()
            return foundUser.id
        except NoResultFound:
            return None
