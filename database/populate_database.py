# Import access to database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Access to database tables
from database_setup import Base, user, category, categoryItem

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# DBSession establishes communication with the database
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Print all users 
def printUsers():
    us = session.query(user).all()
    for u in us:
        print u.id
        print u.name + ': ' + u.email + '\n'

# Create a new user
def createUser(name, email, pic):
    u = user(name=name, email=email, picture=pic)
    session.add(u)
    session.commit()
        
# Delete a user
def killUser(id):
    us = session.query(user).filter_by(id=id).one()
    session.delete(us)
    session.commit()

# Create a new category
def createCategory(name, userID):
    cat = category(name=name, user_id=userID)
    session.add(cat)
    session.commit()

# Print all categories
def printAllCategories():
    cats = session.query(category).all()
    for c in cats:
        print c.id
        print c.name + '\n'

# Create an item
def createItem(name, description, categoryID, userID):
    item = categoryItem(name=name, description=description, category_id=1, user_id=userID)
    session.add(item)
    session.commit()

# Print all items 
def printAllItems():
    items = session.query(categoryItem).all()
    for c in items:
        print c.id
        print c.name + '\n'


def deleteAllItems():
    items = session.query(categoryItem).all()
    for i in items:
        session.delete(i)
    session.commit()


# Initial 
'''
createUser('John Doan', 'JDoan4321@gamil.com','https://encrypted-tbn0.gstatic.com/images?q= \
tbn:ANd9GcT3ebeIeow4tnRTtlrzVKnGpFEXbNNWcOpXK8R_qodf0aT7aFDN')

createCategory('Computers', 1)

createItem('Intel i-7', 'This is a cpu!', 1, 1)
createItem('Asus Strix 1080ti', 'This is a gpu!', 1, 1)


# More categories

createCategory('Foods', 1)
createCategory('Exercise', 1)
createCategory('Health', 1)
createCategory('Diseases', 1)
createCategory('Furniture', 1)
createCategory('Clothing', 1)


# More items

createItem('Intel i-5', 'This is a cpu but its not as good as an i-7!', 1, 1)
'''

printUsers()
printAllCategories()
printAllItems()
#deleteAllItems()
printAllItems()






