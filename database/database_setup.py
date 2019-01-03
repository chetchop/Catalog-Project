#!/usr/bin/env python3
#
# Database setup for a catalog application

# Imports to allow use of SqlAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


# table containing users
class user(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# table containing categories
class category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(user)

    # Category data in serializable format
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


# table containing items
class categoryItem(Base):
    __tablename__ = 'categoryItem'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(user)

    # Item data in serializable format
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }


engine = create_engine('sqlite:///database/catalog.db')
Base.metadata.create_all(engine)
