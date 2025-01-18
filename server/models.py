from sqlalchemy_serializer import SerializerMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import date, time


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})


from config import db

# Models go here!

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-dates.user', '-categories.dates.user')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    dates = db.relationship('Date', back_populates='user', cascade="all, delete-orphan")
    categories = association_proxy('dates', 'category')

    def to_dict(self):

        return {
            "id": self.id,
            "name": self.name,
            "categories": [
                {

                    "id": category.id,
                    "name": category.name,
                    "dates": [date.to_dict() for date in category.dates if date.user_id == self.id]
                }
                for category in set(self.categories)
            ],
            "dates": [date.to_dict() for date in self.dates],
        }

    def __repr__(self):
        return f'<User {self.name}, {self.password}>'
    
class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'

    serialize_rules = ('-dates.category',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    dates = db.relationship('Date', back_populates='category')

    def to_dict(self):

        return{
            "id": self.id,
            "name": self.name,
            "dates": [date.to_dict() for date in self.dates]
        }

    def __repr__(self):
        return f'<Category {self.name} >'

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    serialize_rules = ('-date.activities',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    date_id = db.Column(db.Integer, db.ForeignKey('dates.id'))

    date = db.relationship('Date', back_populates='activities')

    def to_dict(self):

        return {
            "id": self.id,
            "name": self.name,
        }

    def __repr__(self):
        return f'<Activity {self.name} >'
    

class Date(db.Model, SerializerMixin):
    __tablename__ = 'dates'

    serialize_rules = ('-user.dates', '-category.dates', '-activities.date')

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    description = db.Column(db.String, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    user = db.relationship('User', back_populates='dates')
    category = db.relationship('Category', back_populates='dates')
    activities = db.relationship('Activity', back_populates='date', cascade="all, delete-orphan")

    def to_dict(self):

        return {
            "id": self.id,
            "date": str(self.date),
            "time": str(self.time),
            "description": self.description,
            "category": self.category.name if self.category else None,
            "activities": [activity.to_dict() for activity in self.activities]
        }

    def __repr__(self):
        return f'<Date {self.date}, {self.time}, {self.description}>'

